# app/controllers/home_controller.py
class LoginController:
    def loginDiv(self, params):
        return {
            "template": "pages/login.html",
            "context": {

            },
            "status": 200,
        }

    def makeLogin(self, params):
        print(params)
        flag = False
        if(params.get("username") == "adar" and params.get("password") == "1234"):
            flag = True
        return {
            "json": {
                "flag": flag,
            },
            "status": 200
        }
