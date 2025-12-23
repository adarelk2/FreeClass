from models.users_model import UsersModel
from core.controller_base import ControllerBase
from core.database import db
from core.config import (SECRET_JWT_KEY)
import jwt
import time

class AdminloginController(ControllerBase):
    def print(self, params):
        context = {}

        return self.responseHTML(context, "admin-login")

    def checkLogin(self,params):
        context = {}
        flag = False
        users_model = UsersModel(db)
        username = params["username"]
        password = params["password"]

        user = users_model.filter({"username" : username, "password": password})
        print(user)
        if len(user)>0:

            encoded = jwt.encode({"exp":int(time.time())+60 , "username": user[0]['username'], "role":user[0]['role']}, SECRET_JWT_KEY, algorithm="HS256")
            context['token'] = encoded
            flag = True
        return self.responseJSON(context, flag)

