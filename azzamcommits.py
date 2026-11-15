import os
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_all():
    api_key = os.getenv("API_KEY")
    offset = 0
    limit = 100
    all_countries = []
    fields = "cca2,name.common,name.official,cca3,alpha_2,alpha_3,region,subregion"
    
    while True:
        headers = {"X-API-Key": api_key}
        params = {"offset": offset, "limit": limit, "fields": fields}
        
        res = requests.get("YOUR_API_URL_HERE", headers=headers, params=params).json()
        all_countries.extend(res.get("data", []))
        
        if res.get("meta", {}).get("more"):
            offset += 100
        else:
            break
            
    return all_countries