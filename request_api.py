import requests
import os
import json
from winotify import Notification
from geopy.geocoders import Photon

# parameters for Traficar API
api_params = {"zoneId": "9", "discounts": "true", "discountType": "Relokacja"}

# an option to use geolocation or not
geolocation_switch = 0

# add geolocator for area location retrieval
geolocator = Photon(user_agent="TrafiTracker2")

# if old cars.json file exists, delete it
if os.path.exists("cars.json"):
    os.remove("cars.json")

# prepare Windows toast
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

def add_new_info(car_list):
    for car in car_list:
        # if lat in car check if changed. If not - skip

        # adding Google Maps link based on latitude and longitude
        lat = car["lat"]
        lng = car["lng"]

        # https://www.google.pl/maps/search/lat,+lng/@lat,lng,17z
        g_maps_url = (
            f"https://www.google.pl/maps/search/"
            f"{lat},+{lng}/"
            f"@{lat},{lng},17z"
        )
        car["gmaps"] = g_maps_url

        # added geodata
        if geolocation_switch:
            try:
                geo_location = geolocator.reverse((lat, lng))
                address_raw = geo_location.raw.get("properties", {})
                address = ""
                for part in ["name", "street", "locality", "district"]:
                    if part in address_raw:
                        address += f"{address_raw[part]} |"
                precise_location = address if geo_location else "Brak danych geolokalizacyjnych"
            except Exception as e:
                print(f"Exception in geolocating your car: {e}")
                precise_location = "Brak danych geolokalizacyjnych"
        else:
            precise_location = "Brak danych geolokalizacyjnych"

        car["preciseLocation"] = precise_location

        # don't process more data, if it's already there
        if "carImage" in car:
            continue

        # adding car model information
        car_id = car["modelId"]
        car_model = car_models[car_id]
        car["modelName"] = car_model

        # adding image name
        car_image_name = (car_model.split(" ")[0] + "-" + car_model.split(" ")[1]).lower() + ".png"
        if car_image_name not in image_names:
            car_image_name = "no-image.png"
        car["carImage"] = car_image_name

        # adding availability image
        if car["available"]:
            car["availableImage"] = "green-av.png"

    return car_list

def find_new_cars(latest_data):
    all_cars = []
    old_car_ids = []
    new_cars = []
    new_car_ids = []
    new_cars_counter = 0
    removed_cars_counter = 0

    # scenario 1: cars.json doesn't exist, save all cars to a list, then to a .json file, then return the list
    if not os.path.exists("cars.json"):
        for car in latest_data:
            all_cars.append(car)
        add_new_info(all_cars)
        with open("cars.json", "w") as cars_file:
            json.dump(all_cars, cars_file)
        return all_cars

    # load already saved cars
    with open("cars.json", "r") as cars_file:
        old_cars = json.load(cars_file)

    # add old cars from the .json file, and add their ids to a second list
    for car in old_cars:
        old_car_ids.append(car["id"])

    # scenario 2: new cars appeared
    for new_car in latest_data:
        new_car_ids.append(new_car["id"])
        if new_car["id"] not in old_car_ids:
            # add new cars from the latest refresh
            new_cars.append(new_car)
            new_cars_counter += 1
        else:
            # update "lastUpdate" value
            for old_car in old_cars:
                if old_car["id"] == new_car["id"]:
                    old_car["lastUpdate"] = new_car["lastUpdate"]

    # create and show Windows toast for new cars
    if new_cars_counter:
        new_cars_toast = Notification(
            app_id="TrafiTracker",
            title="Nowe auta!",
            msg=f"Znalezionych nowych aut: {new_cars_counter}",
            duration="short",
            icon=icon_path
        )
        new_cars_toast.show()

    # scenario 3: cars they stopped being available
    for old_car in old_cars:
        if old_car["id"] not in new_car_ids and old_car["available"] == True:
            old_car["available"] = False
            old_car["availableImage"] = "red-av.png"
            removed_cars_counter += 1

    # create and show Windows toast if any car stopped being available
    if removed_cars_counter:
        car_archived_toast = Notification(
            app_id="TrafiTracker",
            title="Przynajmniej jeden Traficar przestał być dostępny!",
            msg=f"Zarchiwizowanych aut: {removed_cars_counter}",
            duration="short",
            icon=icon_path
        )
        car_archived_toast.show()

    # save results to .json file and return the list
    all_cars = old_cars + new_cars
    all_cars = add_new_info(all_cars)
    with open("cars.json", "w") as cars_file:
        json.dump(all_cars, cars_file)

    return all_cars

def fetch_data():
    url_params = (
        f"zoneId={api_params["zoneId"]}"
        f"&discounts={api_params["discounts"]}"
        f"&discountType={api_params["discountType"]}"
    )
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

    # process json data
    processed_cars = find_new_cars(parsed_json)

    return processed_cars


def prepare_data_to_gui():
    data = fetch_data()

    cars = []
    for car in data:
        car["availableGUI"] = "Tak" if car["available"] == True else "Nie"
        if "T" in car["lastUpdate"]:
            hour_timestamp = str(int(car["lastUpdate"][11:13]) + 1)
            hour_timestamp = "0" + hour_timestamp if len(hour_timestamp) == 1 else hour_timestamp
            last_update = car["lastUpdate"][0:11] + hour_timestamp + car["lastUpdate"][13:]

            car["lastUpdate"] = last_update.replace("T", " ")[:-1]
        cars.append(car)

    return cars