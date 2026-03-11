import requests
import os
from winotify import Notification, audio

icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img", "favicon.ico")

car_models = {
    2: "RENAULT Clio IV",
    5: "RENAULT Zoe",
    15: "RENAULT Master",
    17: "RENAULT Clio V",
    18: "DACIA Spring",
    22: "DACIA Dokker",
    59: "DACIA Sandero",
    60: "RENAULT Arkana",
    62: "RENAULT Megane E-Tech",
    65: "RENAULT Express",
    66: "NAVEE D1 Pro"
}

image_names = [
    "renault-express.png",
    "renault-master.png",
    "renault-arkana.png",
    "renault-clio.png",
    "dacia-dokker.png",
    "dacia-sandero.png"
]

def fetch_data():
    url_params = "zoneId=9&discounts=false&discountType=Relokacja"
    target_url = "https://fioletowe.live/api/v1/cars?" + url_params

    response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    if response.status_code != 200:
        print(f"Couldn't connect to api, status code: {response.status_code}")
        return None

    response = response.json()

    if response is None:
        print("No data retrieved")
        return None

    parsed_json = response["cars"]
    return parsed_json


def add_data():
    data = fetch_data()

    if not data:
        return {}

    for i in range(0, len(data)):
        # adding Google Maps link based on latitude and longitude
        lat = data[i]["lat"]
        lng = data[i]["lng"]

        # https://www.google.pl/maps/search/lat,+lng/@lat,lng,17z
        g_maps_url = (
            f"https://www.google.pl/maps/search/"
            f"{lat},+{lng}/"
            f"@{lat},{lng},17z"
        )
        data[i]["gmaps"] = g_maps_url

        # adding car model information
        car_id = data[i]["modelId"]
        car_model = car_models[car_id]
        data[i]["modelName"] = car_model

        # adding image name
        car_image_name = (car_model.split(" ")[0] + "-" + car_model.split(" ")[1]).lower() + ".png"
        if car_image_name not in image_names:
            car_image_name = "no-image.png"
        data[i]["imageName"] = car_image_name

    return data

def prepare_data_to_gui():
    data = add_data()

    if data is None:
        return None

    cars = []
    for car in data:
        car["available"] = "Tak" if car["available"] == True else "Nie"
        car["lastUpdate"] = car["lastUpdate"].replace("T", " ")[:-1]
        cars.append(car)

    new_car_toast = Notification(
        app_id="TrafiTracker",
        title="Nowe auta!",
        msg="",
        duration="short",
        icon=icon_path
    )
    new_car_toast.show()
    return cars