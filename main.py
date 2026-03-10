from flask import Flask, render_template, url_for
import request_api as api
app = Flask("__name__")

@app.route("/")
def index():
    cars = prepare_data()
    return render_template(
        "index.html",
        cars=cars)


def prepare_data():
    data = api.process_data()

    if data is None:
        return None

    cars = []
    for car in data:
        car["available"] = "Tak" if car["available"] == "True" else "Nie"
        car["lastUpdate"] = car["lastUpdate"].replace("T", " ")[:-1]
        cars.append(car)
    return cars