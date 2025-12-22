from flask import Flask, request
from core.database import db
from core.application import Application

db.connect()
app = Flask(__name__)
application = Application()

@app.route("/<controller>", methods=["GET", "POST"])
def dispatch(controller):
    return application.handle(request, controller)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
