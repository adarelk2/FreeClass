# core/application.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Union
import json
import jwt

from flask import render_template, abort, Response, jsonify
from werkzeug.wrappers import Request

from core.controller_loader import ControllerLoader
from core.config import SECRET_JWT_KEY
from models.User import User
from container import AppContainer

@dataclass
class AppCall:
    controller_name: str
    method_name: str
    params: Dict[str, Any]


class Application:
    def __init__(self, controller_loader: Optional[ControllerLoader] = None, logger: Any = None):
        self.controller_loader = controller_loader or ControllerLoader()
        self.logger = logger

    def _extract_jwt_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from:
        1. Authorization header (Bearer token)
        2. URL params (?token=x or &token=x)
        3. Request body params ({"token": "x"} or {"params": {"token": "x"}})
        """
        # Try Authorization header first
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        # Try URL query params
        token_from_query = request.args.get("token")
        if token_from_query:
            return token_from_query
        
        # Try request body (JSON params)
        payload: Dict[str, Any] = request.get_json(silent=True) or {}
        if isinstance(payload, dict):
            # Direct param
            if "token" in payload:
                return payload.get("token")
            # Nested in params object
            if "params" in payload and isinstance(payload["params"], dict):
                if "token" in payload["params"]:
                    return payload["params"].get("token")
        
        # Try form data
        token_from_form = request.form.get("token")
        if token_from_form:
            return token_from_form
        
        return None

    def _validate_jwt_and_get_user(self, token: str) -> Optional[User]:
        """Validate JWT token and return User object"""
        try:
            payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=["HS256"])
            # Extract user info from token payload
            user = User(
                username=payload.get("username", ""),
                role=payload.get("role", "user"),
                id=payload.get("id")
            )
            return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    def handle(self, request: Request, controller_from_path: str) -> Response:
        errors: list[str] = []
        
        call = self._parse_request(request, controller_from_path)
        if not self._is_valid_request(call, errors):
            return render_template("error.html", errors=errors), 400

        try:
            container = AppContainer()
            
            # Extract and validate JWT token
            token = self._extract_jwt_token(request)
            user: Optional[User] = None
            if token:
                user = self._validate_jwt_and_get_user(token)
            print(user)
            # Check permissions: if controller requires auth and user is not valid, deny
            permission_service = container.permission_service
            allowed_roles = permission_service.get_permissions_by_controller(call.controller_name)
            
            if allowed_roles and not user:
                # Controller requires permission but no valid user
                return jsonify({"msg": "Access Denied: Authentication required", "flag": False}), 403
            
            if user and allowed_roles and not permission_service.has_permission(user, call.controller_name):
                # User authenticated but doesn't have required role
                return jsonify({"msg": "Access Denied: Insufficient permissions", "flag": False}), 403
            
            # Add user to params if authenticated
            if user:
                call.params["user"] = user

            controller = self.controller_loader.get_controller(call.controller_name, container)

            method = getattr(controller, call.method_name, None)
            if not callable(method):
                return render_template(
                    "error.html",
                    errors=[f"Action '{call.method_name}' not found in controller '{call.controller_name}'"],
                ), 404

            # Controllers expect: method(params: dict)
            result = method(call.params)

            if self.logger is not None:
                try:
                    self.logger.insert(
                        {
                            "params": call.params,
                            "method": call.method_name,
                            "controller": call.controller_name,
                        }
                    )
                except Exception:
                    pass

            return self._build_response(result)

        except Exception as err:
            return render_template("error.html", errors=[f"Internal Error: {str(err)}"]), 500

    def _parse_request(self, request: Request, controller_from_path: str) -> AppCall:
        controller_name = (controller_from_path or "home").lower().strip()

        # Safer JSON parsing (won't throw)
        payload: Dict[str, Any] = request.get_json(silent=True) or {}

        # method can come from query, json, or form
        method_name = (
            request.args.get("method")
            or (payload.get("method") if isinstance(payload, dict) else None)
            or request.form.get("method")
            or "print"
        )
        method_name = str(method_name).strip()

        # Query params (flat=True keeps single values)
        merged_params: Dict[str, Any] = request.args.to_dict(flat=True)
        merged_params.pop("method", None)

        # Body params:
        # Prefer JSON: {"params": {...}}
        body_params: Dict[str, Any] = {}
        if isinstance(payload, dict):
            maybe_params = payload.get("params")
            if isinstance(maybe_params, dict):
                body_params = maybe_params

        # Optional: support form field named "params"
        # - if it's a JSON string, parse it
        # - if not JSON, ignore it (keeps behavior safe/consistent)
        form_params_raw = request.form.get("params")
        if not body_params and form_params_raw:
            if isinstance(form_params_raw, str):
                try:
                    parsed = json.loads(form_params_raw)
                    if isinstance(parsed, dict):
                        body_params = parsed
                except Exception:
                    # ignore non-json "params" field
                    pass

        params = {**merged_params, **body_params}

        return AppCall(controller_name=controller_name, method_name=method_name, params=params)

    def _is_valid_request(self, call: AppCall, errors: list[str]) -> bool:
        if not self.controller_loader.is_controller_exist(call.controller_name):
            errors.append(f"Controller '{call.controller_name}' not found")
            return False

        if call.method_name.startswith("_"):
            errors.append("Action not allowed")
            return False

        return True

    def _build_response(self, result: Any) -> Response:
        # Allow returning (response, status) or Flask Response
        if isinstance(result, tuple):
            return result  # type: ignore[return-value]

        if hasattr(result, "status_code"):
            return result  # type: ignore[return-value]

        # JSON envelope: {"json": {...}, "status": 200}
        if isinstance(result, dict) and "json" in result:
            status = int(result.get("status", 200))
            return jsonify(result["json"]), status

        # Template envelope: {"template": "x.html", "context": {...}, "status": 200}
        if isinstance(result, dict) and "template" in result:
            template = result["template"]
            context = result.get("context", {})
            status = int(result.get("status", 200))
            return render_template(template, **context), status

        abort(500)
