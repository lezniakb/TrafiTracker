import requests

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
        lat = data[i]["lat"]
        lng = data[i]["lng"]

        # https://www.google.pl/maps/search/lat,+lng/@lat,lng,17z
        g_maps_url = (
            f"https://www.google.pl/maps/search/"
            f"{lat},+{lng}/"
            f"@{lat},{lng},17z"
        )
        data[i]["gmaps"] = g_maps_url

    return data