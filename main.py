from flask import Flask, render_template, url_for
import request_api as api
app = Flask("__name__")

@app.route("/")
def index():
    cars = api.prepare_data_to_gui()
    return render_template(
        "index.html",
        cars=cars)