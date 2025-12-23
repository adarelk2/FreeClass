from models.users_model import UsersModel
from core.controller_base import ControllerBase
from core.database import db

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
        if len(user)>0:
            flag = True
        return self.responseJSON(context, flag)



