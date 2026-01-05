from core.controller_base import ControllerBase
from core.config import (SECRET_JWT_KEY)
import jwt
import time

class AdminloginController(ControllerBase):
    def __init__(self, _container):
        self.users_model = _container.users_model

    def print(self, params):
        context = {}

        return self.responseHTML(context, "admin-login")

    def checkLogin(self,params):
        context = {}
        flag = False
        users_model = self.users_model
        print(users_model)
        username = params["username"]
        password = params["password"]

        user = users_model.filter({"username" : username, "password": password})
        if len(user)>0:

            encoded = jwt.encode({"exp":int(time.time())+60 , "username": user[0]['username'], "role":user[0]['role']}, SECRET_JWT_KEY, algorithm="HS256")
            context['token'] = encoded
            flag = True
        return self.responseJSON(context, flag)

