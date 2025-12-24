from flask import Flask, request
from core.application import Application
from core.config import SERVER_PORT

app = Flask(__name__)
application = Application()

@app.route("/", defaults={"controller": "home"}, methods=["GET", "POST"])
@app.route("/<controller>", methods=["GET", "POST"])
def dispatch(controller):
    return application.handle(request, controller)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVER_PORT, debug=True)
