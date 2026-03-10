import requests

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

def fetch_data():
    url_params = "zoneId=9&discounts=false&discountType=Relokacja"
    target_url = "https://fioletowe.live/api/v1/cars?" + url_params

    response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    if response.status_code != 200:
        print(f"Couldn't connect to api, status code: {response.status_code}")
        return None

    response = response.json()

    if len(response) == 0:
        print("No data retrieved")
        return None

    parsed_json = response["cars"]
    return parsed_json


def process_data():
    data = fetch_data()

    if not len(data):
        return {}

    for i in range(0, len(data)):
        # adding google maps link based on latitude and longitude
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
        data[i]["modelName"] = car_models[car_id]

    return data