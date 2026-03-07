from flask import Flask, render_template, url_for
import request_api as api
app = Flask("__name__")

@app.route("/")
def index():
    params = prepare_data()
    return render_template(
        "index.html",
        id=params["id"],
        carsNum=params["carsNum"])


def prepare_data():
    data = api.process_data()

    if data is None:
        params = {
            "id": None,
            "carsNum": None
        }
        return params

    id = data[0]["id"]
    carsNum = len(data)

    params = {
        "id": id,
        "carsNum": carsNum
    }

    return params