from flask import Flask, request
from core.application import Application

app = Flask(__name__)
application = Application()
@app.get("/")
def root():
    # default controller: home
    return application.handle(request, "home")
    
@app.get("/<controller>")
def dispatch(controller):
    return application.handle(request, controller)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
