from core.controller_base import ControllerBase
from core.config import (SECRET_JWT_KEY)
import jwt
import time

class AdminloginController(ControllerBase):
    def __init__(self, _container):
        self.users_service = _container.users_service

    def print(self, params):
        context = {}

        return self.responseHTML(context, "admin-login")


    def checkLogin(self, params):
        username = params["username"]
        password = params["password"]
        user = self.users_service.authenticate(username, password)
        if user:
            # Include user id in JWT payload for User object reconstruction
            encoded = jwt.encode({
                "exp": int(time.time()) + 3600,
                "username": user['username'],
                "role": user['role'],
                "id": user.get('id')
            }, SECRET_JWT_KEY, algorithm="HS256")
            context = {}
            context['token'] = encoded
            return self.responseJSON(context, True)

        return self.responseJSON("Error - user not found", False)
