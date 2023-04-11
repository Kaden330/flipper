import difflib
import json
import logging
import sys
from difflib import get_close_matches, SequenceMatcher

import numpy as np
import pandas as pd

from ebay_scrape import get_description, get_item_specs, get_listing_price
from kbb_scrape import get_ranges, get_styles
from utils import dollar_to_int, searalize, thousands, get_best_pair
from vin_decoder import (get_all_makes, get_models, get_vin_decode_info,
                         vin_decode)

logging.basicConfig(filename="newfile.log", filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
 
# Test messages

def dict_format(dict):
    return json.dumps(dict, indent=4)

def analyze_car(url):
    # get info from ebay listing

    print('Getting info from ebay...')
    logger.info('Getting listing price')
    listing_price = get_listing_price(url)
    specs = get_item_specs(url)
    desc = get_description(url)
    print('final Specs:', specs)

    # vin lookup
    print('Decoding VIN number...')
    logger.info('Decoding VIN number')
    vin_decoded = vin_decode(specs['VIN'], specs['Year'])

    # Kbb Search
    print('Analyzing listing for style ...')
    logger.info('Analyzing listing for style')
    year = specs['Year']
    make = vin_decoded['Make'].title()
    body = vin_decoded['BodyClass']
    available_models = pd.read_csv('models_years_db.csv')
    available_models = available_models.loc[available_models['Make'] == make]
    available_models = available_models['Model'].to_list()
    
    model = get_best_pair([vin_decoded['Model'], specs['Trim']], available_models)
    model = model.values[0][1]

    # Get KBB styles
    logger.info('Getting possible styles from KBB')
    available_styles = get_styles(
            searalize(make), 
            searalize(model), 
            searalize(year),
            searalize(body))

    print('\n\n\n', available_styles)
    if len(available_styles) == 1:
        print('[INFO] Only one style avalible')
        logger.info('Only one style availible')
        style = available_styles[0]

    else:
        try:
            logger.info('Trying to use listing trim to pick style')
            # Use trim from listing to pick the closest option from kbb
            style = get_close_matches(specs['Trim'], available_styles, cutoff=0)[0]

        except:
            try:
                print("[INFO] Couldn\'t extrapolate style level from specs. Searcing description")
                logger.info('Couldn\'t extrapolate style level from specs. Searcing description')

                # Use discription from listing to pick the closest option from kbb
                desc = ''.join([ c if (c.isalnum() or c.isspace()) else '' for c in desc ])
                words = desc.split(' ')

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

                style = max(scored_pairs, key=scored_pairs.get)

            except: 
                # If theres no key that matches pic the middle one
                print("[INFO] Couldn\'t extrapolate style level from listing. Picking middle option (median expense)")
                logger.info('Couldn\'t extrapolate style level from listing. Picking middle option (median expense)')
                
                size = len(available_styles)
                middle_index = size//2
                style = available_styles[middle_index]


    condition = 'fair'
    mileage = specs['Mileage']

    print(f'\n[INFO] Vehicle Information:\nMake: {make}, model: {model}, style: {style}, year: {year}, mileage: {thousands(mileage)}, listing price: ${thousands(listing_price)}\n')

    print('Getting Trade-In ranges from KBB...')
    logger.info('Getting Trade-In ranges from KBB')

    trade_in_ranges = get_ranges(
        searalize(make), 
        searalize(model), 
        searalize(style), 
        searalize(year), 
        searalize(condition, replace_with=''), 
        searalize(mileage),
        trade_in=True)

    print('Getting private party ranges from KBB...')
    logger.info('Getting private party ranges from KBB')

    private_party_ranges = get_ranges(
        searalize(make), 
        searalize(model), 
        searalize(style), 
        searalize(year), 
        'good', 
        searalize(mileage),
        trade_in=False)

    # Calculate important factors
    logger.info('Calculating important factors')

    best_delta = dollar_to_int(private_party_ranges['high']) - dollar_to_int(trade_in_ranges['low'])
    worst_delta = dollar_to_int(private_party_ranges['low']) - dollar_to_int(trade_in_ranges['high'])
    avg_delta = dollar_to_int(private_party_ranges['value']) - dollar_to_int(trade_in_ranges['value'])

    listing_best_delta = dollar_to_int(private_party_ranges['high']) - listing_price
    listing_worst_delta = dollar_to_int(private_party_ranges['low']) - listing_price
    listing_avg_delta = dollar_to_int(private_party_ranges['value']) - listing_price

    mileage = int(mileage)
    if mileage < 25000: mileage_rating = 'very low mileage'
    if mileage < 50000: mileage_rating = 'low mileage'
    elif mileage < 100000: mileage_rating = 'mid mileage'
    elif mileage < 150000: mileage_rating = 'high mileage'
    elif mileage < 200000: mileage_rating = 'very high mileage'
    else: mileage_rating = 'unbelievably high mileage'

    # Generate Breifing
    logger.info('Generating breifing')

    print('\n\n##### Breifing #####')

    print(f'\nThis car is a {year} {make} {style} {model} with {mileage_rating} ({thousands(mileage)}). It\'s listed at ${thousands(listing_price)}.\nThe best case senario for profit baised on the listing price is ${thousands(listing_best_delta)}')

    print('\nListing Description:')
    print(f'\n{desc}\n')
        
    print(f"Trade in prices range from {trade_in_ranges['low']} to {trade_in_ranges['high']}")
    print(f"Private party prices range from {private_party_ranges['low']} to {private_party_ranges['high']}")
    print(f"The potential profit ranges from ${thousands(worst_delta)} to ${thousands(best_delta)} and averages around ${thousands(avg_delta)}")
    print(f"The profit at listing price ranges from ${thousands(listing_worst_delta)} to ${thousands(listing_best_delta)} and averages around ${thousands(listing_avg_delta)}")

    print('\nDetails:')
    print(year)
    print(make)
    print(style)
    print(model)
    print(mileage)
    print(f'listed at ${listing_price}')
    print(f'potential avg profit ${avg_delta}')
    print(f'potential listing profit ${listing_avg_delta}')

if __name__ == '__main__':
    LISTING_URL = sys.argv[1]
    analyze_car(LISTING_URL)
