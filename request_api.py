import requests
import os
import json
from winotify import Notification

# if old JSON file exists, delete it
if os.path.exists("cars.json"):
    os.remove("cars.json")

# prepare Windows toasts
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img", "favicon.ico")
failed_connection_toast = Notification(
    app_id="TrafiTracker",
    title="Brak połączenia z serwerami",
    msg="Nie udało się wczytać danych z serwerów.",
    duration="short",
    icon=icon_path
)

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

def find_new_cars(latest_data):
    if os.path.exists("cars.json"):
        found_cars_id = []
        new_cars_found = 0

        with open("cars.json", "r") as cars_file:
            found_cars = json.load(cars_file)

        # save which car IDs were already present
        for old_car in found_cars:
            found_cars_id.append(old_car["id"])

        # check which car IDs are new, and report them as new cars
        for new_car in latest_data:
            if new_car["id"] in found_cars_id:
                continue
            new_cars_found += 1

        if new_cars_found == 1:
            new_cars_toast = Notification(
                app_id="TrafiTracker",
                title=f"Znaleziono 1 nowe auto!",
                msg="Przejdź do panelu aplikacji",
                duration="short",
                icon=icon_path
            )
            new_cars_toast.show()
        elif new_cars_found > 1:
            new_cars_toast = Notification(
                app_id="TrafiTracker",
                title=f"Znaleziono {new_cars_found} nowe auta!",
                msg="Przejdź do panelu aplikacji",
                duration="short",
                icon=icon_path
            )
            new_cars_toast.show()

    # save cars.json from the latest data
    with open("cars.json", "w") as cars_json:
        json.dump(latest_data, cars_json)

def fetch_data():
    url_params = "zoneId=9&discounts=false&discountType=Relokacja"
    target_url = "https://fioletowe.live/api/v1/cars?" + url_params

    # if GET request fails, raise an exception
    try:
        response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    except requests.exceptions.ConnectionError as exception:
        print(f"Couldn't connect to api, exception:{exception}")
        failed_connection_toast.show()
        return None

    # if http status code is not 200 OK (no connection or other problems)
    if response.status_code != 200:
        print(f"The server is returning HTTP status code {response.status_code}")
        return None

    response = response.json()
    parsed_json = response["cars"]

    find_new_cars(parsed_json)

    return parsed_json


def add_data():
    data = fetch_data()

    if data is None:
        return None

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

    return cars