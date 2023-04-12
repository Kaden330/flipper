import sys

import numpy as np
import pandas as pd

from ebay_scrape import get_description, get_item_specs, get_listing_price
from get_info_helpers import style_from_description, style_from_specs, generate_breifing
from kbb_scrape import get_ranges, get_styles
from utils import get_best_pair, searalize, thousands
from vin_decoder import vin_decode


def pick_style(available_styles, specs, desc):
    if len(available_styles) == 1:
        print('[INFO] Only one style avalible')
        return available_styles[0]

    else:
        try: return style_from_specs(available_styles, specs)
        except: return style_from_description(available_styles, desc)

def analyze_car(url):
    # get info from ebay listing

    print('Getting info from ebay...')
    listing_price = get_listing_price(url)
    specs = get_item_specs(url)
    desc = get_description(url)

    # vin lookup
    print('Decoding VIN number...')
    vin_decoded = vin_decode(specs['VIN'], specs['Year'])

    # Vehicle Variables
    make = vin_decoded['Make'].title()
    year = specs['Year']
    condition = 'fair'
    mileage = specs['Mileage']

    # get model
    print('Analyzing listing for model ...')
    available_models = pd.read_csv('models_years_db.csv')
    available_models = available_models.loc[available_models['Make'] == make]
    available_models = available_models['Model'].to_list()
    
    model = get_best_pair([vin_decoded['Model'], specs['Trim']], available_models)
    model = model.values[0][1]

    # Get KBB styles
    print('Analyzing listing for style ...')
    body = vin_decoded['BodyClass']
    available_styles = get_styles(
            searalize(make), 
            searalize(model), 
            searalize(year),
            searalize(body))

    style = pick_style(available_styles, specs, desc)

    print(f'\n[INFO] Vehicle Information:\nMake: {make}, model: {model}, style: {style}, year: {year}, mileage: {thousands(mileage)}, listing price: ${thousands(listing_price)}\n')

    print('Getting Trade-In ranges from KBB...')

    trade_in_ranges = get_ranges(
        searalize(make), 
        searalize(model), 
        searalize(style), 
        searalize(year), 
        searalize(condition, replace_with=''), 
        searalize(mileage),
        trade_in=True)

    print('Getting private party ranges from KBB...')

    private_party_ranges = get_ranges(
        searalize(make), 
        searalize(model), 
        searalize(style), 
        searalize(year), 
        'good', 
        searalize(mileage),
        trade_in=False)

    mileage = int(mileage)
    
    # Generate Breifing
    print('\n\n##### Breifing #####')

    breifing_str = generate_breifing(
        year,
        make,
        style,
        model,
        mileage,
        desc,
        listing_price,
        private_party_ranges,
        trade_in_ranges
    )

    print(breifing_str)
    
if __name__ == '__main__':
    LISTING_URL = sys.argv[1]
    analyze_car(LISTING_URL)
