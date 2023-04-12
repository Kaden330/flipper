import time
from typing import List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils import StyleException, calc_simalarity, dollar_to_int, search_a_in_b, serialize

custom_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        
def get_styles(make: str, model: str, year: int, body_type: str = None, verbose=0) -> List[str]:
    """
    Get a list of styles for a given vehicle make, model, and year from kbb.com.
    
    Args:
    - make (str): the make of the vehicle
    - model (str): the model of the vehicle
    - year (int): the year of the vehicle
    - body_type (str): the body type of the vehicle (optional)

    Returns:
    - List[str]: a list of styles for the given vehicle parameters
    """
    
    # set Chrome driver options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument(f'user-agent={custom_user_agent}')
    
    # initialize Chrome webdriver
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # navigate to kbb.com styles page for the given vehicle parameters
    browser.get(f'https://www.kbb.com/{make}/{model}/{year}/styles/?intent=buy-used')

    if verbose > 2: print(f'https://www.kbb.com/{make}/{model}/{year}/styles/?intent=buy-used')

    styles = []
    try:
        # wait for the styles to load and extract them
        styles_obj = WebDriverWait(browser, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'toggle')))
        for style in styles_obj:
            style_str = style.text
            split = style_str.split('\n')
            styles.append(split[0])
    
    except:
        # if styles do not load, try to find the closest matching category and extract its styles
        cattegories = WebDriverWait(browser, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'css-v9y0wd')))
        catt_scores = {}

        # calculate similarity scores between body_type and the available categories
        for catt in cattegories:
            catt_scores[catt.text] = [calc_simalarity(body_type, catt.text), catt]

        # select the category with the highest similarity score and click on it
        cattegory = max(catt_scores, key=lambda dict: dict[0])
        catt_scores[cattegory][1].click()

        # get the URL for the selected category and navigate to it
        new_url = browser.current_url
        browser.quit()
        del browser

        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        browser.get(new_url)
        final_url = browser.current_url
        browser.quit()

        styles.append(final_url.split('/')[6])

    # check if styles list contains any invalid values and raise an exception if it does
    break_list = ['Price New/Used', 'Search by Price', 'Cars For Sale']
    if search_a_in_b(styles, break_list):
        if verbose > 2: print(styles)
        raise StyleException('function was not supplied with real values.`make` `model` or `year` are invalid vehicle parameters')
    else:
        return styles


def get_ranges(make: str, model: str, style: str, year: int, condition: str, mileage: int, trade_in: bool = True) -> dict:
    """
    Get price ranges for a specified vehicle model based on various conditions.

    Args:
        - make (str): The make of the vehicle.
        - model (str): The model of the vehicle.
        - style (str): The style of the vehicle.
        - year (int): The year of the vehicle.
        - condition (str): The condition of the vehicle (e.g., "fair", "good", "excellent").
        - mileage (int): The mileage of the vehicle.
        - trade_in (bool, optional): Whether to get trade-in prices or private-party prices. Defaults to True.

    Returns:
        - dict: A dictionary containing the low, high, and value of the price range.
    """
    
    # Define parsers for different price types
    def _trade_in_parser(str):
        parsed_data = {}
        split = str.split(' ')
        parsed_data['low']= split[2]
        parsed_data['high'] = split[4]
        parsed_data['value'] = split[-1]
        return parsed_data

    def _private_party_parser(str):
        parsed_data = {}
        split = str.split(' ')
        parsed_data['low']= split[3]
        parsed_data['high'] = split[5]
        parsed_data['value'] = split[-1]
        return parsed_data

    # Select parser based on price type
    if trade_in:
        price_type = 'trade-in'
        parser = _trade_in_parser
    else:
        price_type = 'private-party'
        parser = _private_party_parser
                    
    # Set up webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument(f'user-agent={custom_user_agent}')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Navigate to URL
    browser.get(f'https://www.kbb.com/{make}/{model}/{year}/{style}/?condition={condition}&intent=trade-in-sell&mileage={mileage}&pricetype={price_type}')

    # Get price ranges
    ranges = browser.find_element(By.CLASS_NAME, 'css-je8g23')
    values = ranges.get_attribute("aria-label")

    browser.quit()
    time.sleep(5)

    # Parse and return price range
    return parser(values)

if __name__ == '__main__':
    import json

    # Prompt user for make, model, year, condition, and mileage of the car
    make = input('make?: ')
    model = input('model?: ')
    year = input('year?: ')
    condition = input('condition? (Poor, Fair, Good, Very Good, or Excellent): ')
    mileage = input('mileage?: ')
    verbose = 1

    # Get available styles for the car
    if verbose > 0: (f'\nAvailable styles for a {year} {model}...')
    available_styles = get_styles(
        serialize(make), 
        serialize(model), 
        serialize(year))

    for i, style in enumerate(available_styles):
        if verbose > 1: print(f'{i+1}. {style}')

    # Prompt user for the style number corresponding to the desired style
    style_index = int(input('Style number?: '))
    style = available_styles[style_index-1]

    # Print price ranges for trade-in and private party sales
    if verbose > 0: print(f'\nPrice ranges for a {year} {style} {model}...')
    trade_in_ranges = get_ranges(
        serialize(make), 
        serialize(model), 
        serialize(style), 
        serialize(year), 
        serialize(condition, replace_with=''), 
        serialize(mileage),
        trade_in=True)
    
    if verbose > 0: print(f"Trade in prices range from {trade_in_ranges['low']} to {trade_in_ranges['high']}")

    private_party_ranges = get_ranges(
        serialize(make), 
        serialize(model), 
        serialize(style), 
        serialize(year), 
        'good', 
        serialize(mileage),
        trade_in=False)
    
    if verbose > 0: print(f"Private party prices range from {private_party_ranges['low']} to {private_party_ranges['high']}")

    # Calculate potential profit range and average
    best_delta = dollar_to_int(private_party_ranges['high']) - dollar_to_int(trade_in_ranges['low'])
    worst_delta = dollar_to_int(private_party_ranges['low']) - dollar_to_int(trade_in_ranges['high'])
    avg_delta = dollar_to_int(private_party_ranges['value']) - dollar_to_int(trade_in_ranges['value'])

    # Print potential profit range and average
    if verbose > 0: print(f"The potential profit delta ranges from ${worst_delta} to ${best_delta} and averages around ${avg_delta}")