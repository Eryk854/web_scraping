import os
from typing import Dict

import pandas as pd
import requests
from dotenv import load_dotenv

from read_config_value import read_config_value

load_dotenv()


def prepare_request_parmas(address: str, api_key: str, country: str) -> Dict:
    params = {"country": country, "apiKey": api_key}
    address_values = get_address_values(address)
    params.update(address_values)
    return params


def geocode(address: str, api_key: str, country: str) -> dict:
    params = prepare_request_parmas(address, api_key, country)
    headers = {"Accept": "application/json"}

    print(address)
    if None not in params.values():
        return get_geocode_response(params, headers)
    return {}


def geocode_otodom(row: pd.Series, api_key: str, country: str = "Poland") -> pd.Series:
    geocoded_values = geocode(row["Adres"], api_key, country)
    geocoded_values = pd.Series(geocoded_values)
    result = pd.concat([row, geocoded_values])
    return result


def geocode_nieruchomosci(row: pd.Series, api_key: str, country: str = "Poland") -> pd.Series:
    print(row["Adres"])
    street = row["Adres"].split(",")[0]
    params = {"country": country, "apiKey": api_key, "city": row["Miasto"], "street": street}
    headers = {"Accept": "application/json"}

    geocoded_values = get_geocode_response(params, headers)
    geocoded_values = pd.Series(geocoded_values)
    result = pd.concat([row, geocoded_values])
    return result


def get_geocode_response(params: dict, headers: dict) -> dict:
    url = read_config_value("geocoding")["geocoding_url"]
    resp = requests.get(url, params=params, headers=headers)
    geocoded_response = {}
    geocode_place = {}
    rank = {}
    if resp.status_code == 200:
        resp_content = resp.json()
        if resp_content["features"]:
            full_response = resp_content["features"][0]
            geocode_place = full_response["properties"]
            rank = geocode_place.get("rank", None)

    geocoded_response["latitude"] = geocode_place.get("lat", None)
    geocoded_response["longitude"] = geocode_place.get("lon", None)
    geocoded_response["formatted_address"] = geocode_place.get("formatted", None)
    geocoded_response["result_confidence"] = rank.get("confidence", None)
    geocoded_response["suburb"] = geocode_place.get("suburb", None)
    geocoded_response["building_category"] = geocode_place.get("category", None)
    geocoded_response["result_type"] = geocode_place.get("result_type", None)

    return geocoded_response


def get_address_values(address: str) -> dict:
    address_elements = address.split(",")

    geocoding_config = read_config_value("geocoding")
    acceptable_cities = geocoding_config["acceptable_cities"]
    street_prefixes = geocoding_config["street_prefixes"]

    address_values = {}
    for address_element in address_elements:
        address_element = address_element.strip()
        address_element = address_element.lower()
        if any(city in address_element for city in acceptable_cities):
            address_values["city"] = address_element
        for street_prefix in street_prefixes:
            if street_prefix in address_element:
                address_values["street"] = address_element.lstrip(street_prefix)

    if "city" in address_values and "street" in address_values:
        return address_values

    address_values = {}
    for address_element in address_elements:
        address_element = address_element.strip()
        address_element = address_element.lower()
        if any(city in address_element for city in acceptable_cities):
            address_values["city"] = address_element
        else:
            address_values["state"] = address_element
    return address_values


if __name__ == "__main__":
    API_KEY = os.getenv("API_KEY")
    file_path = "nieruchomosci/nieruchomosci_online_with_price.csv"
    # file_path = "otodom/otodom.csv"
    df = pd.read_csv(file_path, sep="\t")
    df = df.iloc[:100, :]
    # df = df.apply(geocode_otodom, api_key=API_KEY, axis=1)
    df = df.apply(geocode_nieruchomosci, api_key=API_KEY, axis=1)
    df.to_csv("nieruchomosci/geocoded/geocoded1.csv", index=False, sep="\t")

    # address = "Pradnik Bialy, Krakow, Krakow "
    # params = prepare_request_parmas(address, API_KEY, "Poland")
    # headers = {"Accept": "application/json"}
    # get_geocode_response(params, headers)

