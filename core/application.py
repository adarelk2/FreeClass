# core/application.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from flask import render_template, abort, Response, jsonify
from werkzeug.wrappers import Request

from core.controller_loader import ControllerLoader


@dataclass
class AppCall:
    controller_name: str
    method_name: str
    params: Dict[str, Any]


class Application:
    def __init__(self, controller_loader: Optional[ControllerLoader] = None, logger: Any = None):
        self.controller_loader = controller_loader or ControllerLoader()
        self.logger = logger

    def handle(self, request: Request, controller_from_path: str) -> Response:
        errors: list[str] = []
        call = self._parse_request(request, controller_from_path)

        if not self._is_valid_request(call, errors):
            return render_template("error.html", errors=errors), 400

        try:
            controller = self.controller_loader.get_controller(call.controller_name)

            method = getattr(controller, call.method_name, None)
            if not callable(method):
                return render_template(
                    "error.html",
                    errors=[f"Action '{call.method_name}' not found in controller '{call.controller_name}'"],
                ), 404

            result = method(call.params)

            if self.logger is not None:
                try:
                    self.logger.insert({
                        "params": call.params,
                        "method": call.method_name,
                        "controller": call.controller_name,
                    })
                except Exception:
                    pass

            return self._build_response(result)

        except Exception as err:
            return render_template("error.html", errors=[f"Internal Error: {str(err)}"]), 500

    def _parse_request(self, request: Request, controller_from_path: str) -> AppCall:
        controller_name = (controller_from_path or "home").lower().strip()

        method_name = (
            request.args.get("method")
            or (request.json.get("method") if request.is_json and request.json else None)
            or request.form.get("method")
            or "print"
        )
        method_name = method_name.strip()

        merged_params = dict(request.args)
        merged_params.pop("method", None)

        body_params = (
            (request.json.get("params") if request.is_json and request.json else None)
            or request.form.get("params")
            or {}
        )

        if isinstance(body_params, dict):
            params = {**merged_params, **body_params}
        else:
            params = merged_params

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
        if isinstance(result, tuple):
            return result

        if hasattr(result, "status_code"):
            return result

        # ✅ JSON response
        if isinstance(result, dict) and "json" in result:
            status = int(result.get("status", 200))
            return jsonify(result["json"]), status

        # ✅ Template response
        if isinstance(result, dict) and "template" in result:
            template = result["template"]
            context = result.get("context", {})
            status = int(result.get("status", 200))
            return render_template(template, **context), status

        abort(500)
