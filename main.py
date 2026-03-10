from flask import Flask, render_template, url_for
import request_api as api
app = Flask("__name__")

@app.route("/")
def index():
    params = prepare_data()
    return render_template(
        "index.html",
        id=params["id"],
        cars=params["cars"])


def prepare_data():
    data = api.process_data()

    if data is None:
        params = {
            "id": None,
            "cars": [],
        }
        return params

    id = data[0]["id"]
    cars = []

    for car in data:
        cars.append(car)

    params = {
        "id": id,
        "cars": cars
    }

    return params