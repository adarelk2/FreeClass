from flask import Flask
from flask import request
from flask import url_for
from flask import render_template

app = Flask(__name__)
@app.route("/<controller_name>")
def test(controller_name):
    print(controller_name)
    print(request.args['method'])
    return render_template("pages/index.html", user={"name": "Adar"}, lang="he", dir="rtl", script=request.args['method'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)

