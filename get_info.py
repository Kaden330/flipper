import sys

import pandas as pd

from ebay_scrape import get_description, get_item_specs, get_listing_price
from get_info_helpers import (generate_str_breifing, style_from_description, style_from_specs)
from kbb_scrape import get_ranges, get_styles
from utils import get_best_pair, serialize, thousands
from vin_decoder import vin_decode


def pick_style(available_styles: list, specs: dict, desc: str) -> str:
    """
    Picks the best style from a list of available styles based on specifications and descriptions.

    Args:
    - available_styles (list): List of available style names
    - specs (dict): Dictionary containing style specifications
    - desc (str): Description of the desired style

    Returns:
    - str: The best style name that matches the specifications or description.
    """
    # If there is only one style available, return it
    if len(available_styles) == 1: return available_styles[0]

    # If there are multiple styles available, try to match based on specifications
    # If that fails, match based on description
    else:
        try: return style_from_specs(available_styles, specs)
        except: return style_from_description(available_styles, desc)

def analyze_car(url: str) -> None:
    """
    Analyzes a car listing on eBay by decoding the VIN number, determining the make and model, and getting price ranges
    from Kelley Blue Book. Outputs a briefing with relevant information.

    Args:
    - url (str): The URL of the eBay listing to analyze

    Returns:
    - None
    """

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
        serialize(make), 
        serialize(model), 
        serialize(year),
        serialize(body))

    style = pick_style(available_styles, specs, desc)

    print(f'\n[INFO] Vehicle Information:\nMake: {make}, model: {model}, style: {style}, year: {year}, mileage: {thousands(mileage)}, listing price: ${thousands(listing_price)}\n')

    print('Getting Trade-In ranges from KBB...')

    trade_in_ranges = get_ranges(
        serialize(make), 
        serialize(model), 
        serialize(style), 
        serialize(year), 
        serialize(condition, replace_with=''), 
        serialize(mileage),
        trade_in=True)

    print('Getting private party ranges from KBB...')

    private_party_ranges = get_ranges(
        serialize(make), 
        serialize(model), 
        serialize(style), 
        serialize(year), 
        'good', 
        serialize(mileage),
        trade_in=False)

    mileage = int(mileage)

    # Generate Breifing
    print('\n\n##### Breifing #####')

    breifing_str = generate_str_breifing(
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
