import requests
import json

def get_models(make):
    with requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformake/{make}?format=json') as r:
        blob = json.loads(r.text)
        return dict(blob['Results'])

def get_all_makes():
    with requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json') as r:
        blob = json.loads(r.text)
        return dict(blob['Results'])

def vin_decode(VIN, year):
    with requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/{VIN}?format=json&modelyear={year}') as r:
        blob = json.loads(r.text)
        
        return blob['Results'][0]

def get_vin_decode_info():
    with requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/getvehiclevariablelist?format=json') as r:
        blob = json.loads(r.text)
        return dict(blob['Results'])

if __name__ == '__main__':
    print(json.dumps(vin_decode('Wauvvafr3Ca007152', ''), indent=4))