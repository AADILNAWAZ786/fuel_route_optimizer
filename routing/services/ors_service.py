import os
import requests


def geocode_location(location):
    url = "https://api.openrouteservice.org/geocode/search"

    headers = {"Authorization": os.getenv("ORS_API_KEY")}

    params = {"text": location, "size": 1}

    response = requests.get(url, headers=headers, params=params)

    response.raise_for_status()

    data = response.json()

    if not data.get("features"):
        return None

    return data["features"][0]["geometry"]["coordinates"]

def get_route(start_coords, end_coords):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {"Authorization": os.getenv("ORS_API_KEY"), "Content-Type": "application/json"}

    body = {"coordinates": [start_coords, end_coords]}

    response = requests.post(url, headers=headers, json=body)

    response.raise_for_status()

    return response.json()