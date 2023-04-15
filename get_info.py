import sys

import pandas as pd

from ebay_scrape import get_description, get_item_specs, get_listing_price
from get_info_helpers import generate_styled_breifing, generate_str_breifing, style_from_description, style_from_specs
from kbb_scrape import get_ranges, get_styles
from utils import get_best_pair, serialize, thousands
from vin_decoder import vin_decode
from thread_class import ReturnValueThread
from datetime import datetime


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

def analyze_car(url: str, verbose=0) -> None:
    """
    Analyzes a car listing on eBay by decoding the VIN number, determining the make and model, and getting price ranges
    from Kelley Blue Book. Outputs a briefing with relevant information.

    Args:
    - url (str): The URL of the eBay listing to analyze
    - verbose (int): The level of verboseness. 0 is the default (no stout)

    Returns:
    - None
    """

    # get info from ebay listing
    start = datetime.now()
    if verbose > 0: print('Getting info from ebay...')

    descr_thread = ReturnValueThread(target=get_description, args=(url,)) 
    specs_thread = ReturnValueThread(target=get_item_specs, args=(url,))
    price_thread = ReturnValueThread(target=get_listing_price, args=(url,)) 
    descr_thread.start()
    specs_thread.start()
    price_thread.start()
    
    specs = specs_thread.join()

    # vin lookup
    print(f'vin lookup at {datetime.now() - start}')
    if verbose > 0: print('Decoding VIN number...')
    vin_decode_thread = ReturnValueThread(target=vin_decode, args=(specs['VIN'], specs['Year']))
    vin_decode_thread.start()

    # load in dataset of makes and models
    available_models = pd.read_csv('models_years_db.csv')

    # get data from threads
    print(f'get data from threads at {datetime.now() - start}')
    listing_price = price_thread.join()
    vin_decoded = vin_decode_thread.join()

    # Vehicle Variables
    make = vin_decoded['Make'].title()
    year = specs['Year']
    condition = 'fair'
    mileage = specs['Mileage']

    # get model
    print(f'get model at {datetime.now() - start}')

    if verbose > 0: print('Analyzing listing for model ...')
    available_models = available_models.loc[available_models['Make'] == make]
    available_models = available_models['Model'].to_list()

    model = get_best_pair([vin_decoded['Model'], specs['Trim']], available_models)
    model = model.values[0][1]

    # Get KBB styles
    print(f'get styles at {datetime.now() - start}')
    if verbose > 0: print('Analyzing listing for style ...')
    body = vin_decoded['BodyClass']
    available_styles = get_styles(
        serialize(make), 
        serialize(model), 
        serialize(year),
        serialize(body))
    
    print(f'pick styles at {datetime.now() - start}')
    desc = descr_thread.join() # load in data from descr_thread

    style = pick_style(available_styles, specs, desc)

    if verbose > 1:  print(f'\n[INFO] Vehicle Information:\nMake: {make}, model: {model}, style: {style}, year: {year}, mileage: {thousands(mileage)}, listing price: ${thousands(listing_price)}\n')

    if verbose > 0: print('Getting Trade-In ranges from KBB...')

    print(f'get ranges at {datetime.now() - start}')
    trade_in_ranges = get_ranges(
        serialize(make), 
        serialize(model), 
        serialize(style), 
        serialize(year), 
        serialize(condition, replace_with=''), 
        serialize(mileage),
        trade_in=True)

    if verbose > 0: print('Getting private party ranges from KBB...')

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
    if verbose > 0: print('\n\n##### Breifing #####')

    breifing_styled = generate_styled_breifing(
        year,
        make,
        style,
        model,
        mileage,
        desc,
        listing_price,
        url,
        private_party_ranges,
        trade_in_ranges
    )

    return breifing_styled
    
if __name__ == '__main__':
    LISTING_URL = 'https://www.ebay.com/itm/385540746588?hash=item59c404ed5c%3Ag%3APtQAAOSwzgBkNWTH&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049'
    print(analyze_car(LISTING_URL)[0])
