from flask import Flask, render_template, url_for
import request_api as api
app = Flask("__name__")

@app.route("/")
def index():
    data = api.process_data()
    carsNum = len(data)
    return render_template(
        "index.html",
        id=data[0]["id"],
        carsNum=carsNum)