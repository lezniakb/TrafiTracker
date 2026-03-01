import requests

def fetch_data():
    url_params = "zoneId=9&discounts=false&discountType=Relokacja"
    target_url = "https://fioletowe.live/api/v1/cars?" + url_params

    response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    response = response.json()

    parsed_json = response["cars"][0]

    return parsed_json


def request_refresh():
    response = fetch_data()


request_refresh()