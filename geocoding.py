import os
from typing import Dict, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


def prepare_request_parmas(address: str, api_key: str, country: str = "Poland") -> Dict:
    params = {"country": country, "apiKey": api_key}
    city, street = get_address_values(address)
    params["city"] = city
    params["street"] = street
    return params


def geocode(address: str, api_key: str, country: str = "Poland"):
    params = prepare_request_parmas(address, api_key, country)
    headers = {"Accept": "application/json"}

    latitude, longitude, formatted_address, result_confidence = None, None, None, None
    if None not in params.values():
        geocode_place = get_geocode_response(params, headers)
        latitude = geocode_place.get("lat", None)
        longitude = geocode_place.get("lon", None)
        formatted_address = geocode_place.get("formatted", None)
        rank = geocode_place.get("rank", None)
        result_confidence = rank.get("confidence", None)
    else:
        print(f"Cannot get geocoded information about this address: {address}")

    return latitude, longitude, formatted_address, result_confidence


def geocode_otodom(dataframe: pd.DataFrame, api_key: str):
    lat, lon, new_address, confidence = geocode(dataframe["Adres"], api_key)
    dataframe["latitude"] = lat
    dataframe["longitude"] = lon
    dataframe["formatted_address"] = new_address
    dataframe["result_confidence"] = confidence
    return dataframe


def get_geocode_response(params: dict, headers: dict) -> Dict:
    url = "https://api.geoapify.com/v1/geocode/search"
    resp = requests.get(url, params=params, headers=headers)
    resp_content = resp.json()
    full_response = resp_content["features"][0]
    return full_response["properties"]


def get_address_values(address: str) -> Tuple[str, str]:
    address_elements = address.split(",")
    city, street = None, None
    for address_element in address_elements:
        address_element = address_element.strip()
        if any(city in address_element for city in ["Warszawa", "Gdansk"]):
            city = address_element
        for street_prefix in ["ul.", "al."]:
            if street_prefix in address_element:
                street = address_element.lstrip(street_prefix)
    return city, street


if __name__ == "__main__":
    API_KEY = os.getenv("API_KEY")
    file_path = "otodom/otodom.csv"
    df = pd.read_csv(file_path, sep="\t")
    df = df.iloc[250:265, :]
    df = df.apply(geocode_otodom, api_key=API_KEY, axis=1)
    print(df.head())
