# app/controllers/home_controller.py
class HomeController:
    def print(self, params):
        # Your old example: render_template("pages/index.html", user={"name": ...}, page=controller)
        name = params.get("name", "Guest")

        return {
            "template": "pages/index.html",
            "context": {
                "user": {"name": name},
                "page": "home",
            },
            "status": 200,
        }

    def print2(self, params):
        # Your old example: render_template("pages/index.html", user={"name": ...}, page=controller)
        name = params.get("name", "Guest")

        return {
            "template": "pages/index.html",
            "context": {
                "user": {"name": name},
                "page": "home",
            },
            "status": 200,
        }

    def index(self, params):
        return self.print(params)
