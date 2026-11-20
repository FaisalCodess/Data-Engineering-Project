import json
import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.restcountries.com/countries/v5"

def fetch_all():
    api_key = os.getenv("RESTCOUNTRIES_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    offset = 0
    limit = 100
    all_countries = []
    response_fields = "uuid,names.common,names.official,codes.alpha_2,codes.alpha_3,region,subregion,capitals,population,area.kilometers,coordinates.lat,coordinates.lng,landlocked,classification.sovereign,classification.dependency,classification.disputed,classification.un_member,economy.gini_coefficient,languages,currencies,borders"

    while True:
        params = {"offset": offset, "limit": limit, "response_fields": response_fields}

        response = requests.get(API_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()["data"]

        all_countries.extend(data["objects"])

        if data["meta"]["more"]:
            offset += limit
        else:
            break

    return all_countries

def save_raw_json(data):
    output_dir = os.path.join("data", "raw") # data/raw/
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, "countries_raw.json") # data/raw/countries_raw.json
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _join_dict_values(items, key):
    """Join one key from a list of dicts with '|' and return (joined_string, count)."""
    values = [item.get(key, "") for item in (items or []) if isinstance(item, dict)]
    return "|".join(values), len(values)

def flatten(countries_data):
    rows = []
    for c in countries_data:
        names = c.get("names", {})
        codes = c.get("codes", {})
        capitals_list = c.get("capitals", [])
        capital = capitals_list[0].get("name", "") if capitals_list and isinstance(capitals_list[0], dict) else ""
        
        area_dict = c.get("area", {})
        coords = c.get("coordinates", {})
        classification = c.get("classification", {})
        
        economy = c.get("economy", {})
        gini_dict = economy.get("gini_coefficient", {})
        gini = None
        if gini_dict and isinstance(gini_dict, dict):
            valid_years = [str(k) for k in gini_dict.keys() if k is not None]
            if valid_years:
                gini = gini_dict.get(max(valid_years), None)

        langs_raw = c.get("languages", [])
        languages, n_languages = _join_dict_values(langs_raw, key="name")

        curr_raw = c.get("currencies", [])
        currencies, n_currencies = _join_dict_values(curr_raw, key="name")

        borders_raw = c.get("borders", [])
        if borders_raw and isinstance(borders_raw, list):
            if isinstance(borders_raw[0], dict):
                borders_joined, _ = _join_dict_values(borders_raw, key="code")
            else:
                borders_joined = "|".join([str(b) for b in borders_raw])
            n_borders = len(borders_raw)
        else:
            borders_joined = ""
            n_borders = 0

        row = {
            "uuid": c.get("uuid", ""),
            "name_common": names.get("common", ""),
            "name_official": names.get("official", ""),
            "alpha2": codes.get("alpha_2", ""),
            "alpha3": codes.get("alpha_3", ""),
            "region": c.get("region", ""),
            "subregion": c.get("subregion", ""),
            "capital": capital,
            "population": c.get("population", None),
            "area_km2": area_dict.get("kilometers", None),
            "lat": coords.get("lat", None),
            "lng": coords.get("lng", None),
            "landlocked": c.get("landlocked", None),
            "sovereign": classification.get("sovereign", None),
            "dependency": classification.get("dependency", None),
            "disputed": classification.get("disputed", None),
            "un_member": classification.get("un_member", None),
            "gini": gini,
            "languages": languages,
            "n_languages": n_languages,
            "currencies": currencies,
            "n_currencies": n_currencies,
            "borders": borders_joined,
            "n_borders": n_borders
        }
        rows.append(row)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    countries = fetch_all()
    save_raw_json(countries)
    df = flatten(countries)
    
    df.to_csv("data/raw/countries_flat.csv", index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} rows and {df.shape[1]} columns")