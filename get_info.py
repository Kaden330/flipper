import difflib
import json
import sys
from difflib import get_close_matches, SequenceMatcher

import numpy as np
import pandas as pd

from ebay_scrape import get_description, get_item_specs, get_listing_price
from kbb_scrape import get_ranges, get_styles
from utils import dollar_to_int, searalize, thousands, get_best_pair
from vin_decoder import (get_all_makes, get_models, get_vin_decode_info,
                         vin_decode)


def dict_format(dict):
    return json.dumps(dict, indent=4)

def mileage_level(mileage:int) -> str:
    if mileage < 25000: return 'very low mileage'
    if mileage < 50000: return 'low mileage'
    elif mileage < 100000: return 'mid mileage'
    elif mileage < 150000: return 'high mileage'
    elif mileage < 200000: return 'very high mileage'
    else: return 'unbelievably high mileage'

def style_from_description(available_styles, description):
    try:
        print("[INFO] Extrapolating style from description")

        # Use discription from listing to pick the closest option from kbb
        description = ''.join([ c if (c.isalnum() or c.isspace()) else '' for c in description ])
        words = description.split(' ')

        average_len_of_style = int(np.floor(np.mean([len(style.split(' ')) for style in available_styles])))

        pairs = []
        for i in range(len(words)-average_len_of_style):
            pair = ' '.join(words[i:i+average_len_of_style])
            pairs.append(pair)

        scored_pairs = {}
        for style in available_styles:
            pair_scores = []
            for pair in pairs:
                pair_scores.append(SequenceMatcher(None, style, pair).ratio())
            
            scored_pairs[style] = np.max(pair_scores)

        return max(scored_pairs, key=scored_pairs.get)

    except: 
        # If theres no key that matches pic the middle one
        print("[INFO] Couldn\'t extrapolate style level from listing. Picking middle option (median expense)")
        
        size = len(available_styles)
        middle_index = size//2
        return available_styles[middle_index]
    

def style_from_specs(available_styles, listing_specs):
    # Use trim from listing to pick the closest option from kbb
    return get_close_matches(listing_specs['Trim'], available_styles, cutoff=0)[0]


def pick_style(available_styles, specs, desc):
    if len(available_styles) == 1:
        print('[INFO] Only one style avalible')
        return available_styles[0]

    else:
        try: return style_from_specs(available_styles, specs)
        except: return style_from_description(available_styles, desc)

def analyze_car(url):
    # get info from ebay listing

    print('Getting info from ebay...', end='\r')
    print('Getting info from ebay... listing price', end='\r')
    listing_price = get_listing_price(url)
    print('Getting info from ebay... listing specs', end='\r')
    specs = get_item_specs(url)
    print('Getting info from ebay... listing description')
    desc = get_description(url)
    print('Getting info from ebay... done')
    print('final Specs:', specs)

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

    class Page():
        def __init__(self, init_str=''):
            self.body = init_str

        def press(self, str, end='\n'):
            self.body = self.body + (str+end)
    
    def generate_breifing(year, make, style, model, mileage:int, desc, listing_price:int, private_party_ranges, trade_in_ranges):

        # Calculate important factors

        best_delta = dollar_to_int(private_party_ranges['high']) - dollar_to_int(trade_in_ranges['low'])
        worst_delta = dollar_to_int(private_party_ranges['low']) - dollar_to_int(trade_in_ranges['high'])
        avg_delta = dollar_to_int(private_party_ranges['value']) - dollar_to_int(trade_in_ranges['value'])

        listing_best_delta = dollar_to_int(private_party_ranges['high']) - listing_price
        listing_worst_delta = dollar_to_int(private_party_ranges['low']) - listing_price
        listing_avg_delta = dollar_to_int(private_party_ranges['value']) - listing_price
        
        # Generate Breifing
        breifing = Page()

        breifing.press(f'\nThis car is a {year} {make} {style} {model} with {mileage_level(mileage)} ({thousands(mileage)}). It\'s listed at ${thousands(listing_price)}.\nThe best case senario for profit baised on the listing price is ${thousands(listing_best_delta)}')

        breifing.press('\nListing Description:')
        breifing.press(f'\n{desc}\n')
            
        breifing.press(f"Trade in prices range from {trade_in_ranges['low']} to {trade_in_ranges['high']}")
        breifing.press(f"Private party prices range from {private_party_ranges['low']} to {private_party_ranges['high']}")
        breifing.press(f"The potential profit ranges from ${thousands(worst_delta)} to ${thousands(best_delta)} and averages around ${thousands(avg_delta)}")
        breifing.press(f"The profit at listing price ranges from ${thousands(listing_worst_delta)} to ${thousands(listing_best_delta)} and averages around ${thousands(listing_avg_delta)}")

        breifing.press('\nDetails:')
        breifing.press(year)
        breifing.press(make)
        breifing.press(style)
        breifing.press(model)
        breifing.press(thousands(mileage))
        breifing.press(f'listed at ${listing_price}')
        breifing.press(f'potential avg profit ${avg_delta}')
        breifing.press(f'potential listing profit ${listing_avg_delta}')

        return breifing.body
    
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
