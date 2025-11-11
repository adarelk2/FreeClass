from flask import Flask
from flask import request
from flask import url_for
from flask import render_template

app = Flask(__name__)
@app.route("/<controller_name>")
def test(controller_name):
    return render_template("pages/index.html", user={"name": request.args['name']}, page=controller_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)

