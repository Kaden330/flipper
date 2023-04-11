from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils import searalize, dollar_to_int, search_a_in_b, calc_simalarity, StyleException
import pandas as pd

custom_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        
# get styles
def get_styles(make, model, year, body_type=None):
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument(f'user-agent={custom_user_agent}')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    browser.get(f'https://www.kbb.com/{make}/{model}/{year}/styles/?intent=buy-used')  # navigate to URL
    print(f'https://www.kbb.com/{make}/{model}/{year}/styles/?intent=buy-used')


    styles = []
    try:

        styles_obj = WebDriverWait(browser, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'toggle')))

        for style in styles_obj:
            style_str = style.text
            split = style_str.split('\n')
            styles.append(split[0])
    
    except:
        cattegories = WebDriverWait(browser, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'css-v9y0wd')))

        catt_scores = {}

        for catt in cattegories:
            catt_scores[catt.text] = [calc_simalarity(body_type, catt.text), catt]

        cattegory = max(catt_scores, key=lambda dict: dict[0])
        catt_scores[cattegory][1].click()
        new_url = browser.current_url
        
        browser.quit()
        del browser

        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        browser.get(new_url)
        final_url = browser.current_url
        browser.quit()

        styles.append(final_url.split('/')[6])

    break_list = ['Price New/Used', 'Search by Price', 'Cars For Sale']

    if search_a_in_b(styles, break_list):
        print(styles)
        raise StyleException('function was not supplied with real values.`make` `model` or `year` are invalid vehicle parameters')
    
    else:
        return styles


# get price ranges
def get_ranges(make, model, style, year, condition, mileage, trade_in=True):

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

    if trade_in:
        price_type = 'trade-in'
        parser = _trade_in_parser
    else:
        price_type = 'private-party'
        parser = _private_party_parser
                    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument(f'user-agent={custom_user_agent}')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    browser.get(f'https://www.kbb.com/{make}/{model}/{year}/{style}/?condition={condition}&intent=trade-in-sell&mileage={mileage}&pricetype={price_type}')  # navigate to URL

    ranges = browser.find_element(By.CLASS_NAME, 'css-je8g23')
    values = ranges.get_attribute("aria-label")

    browser.quit()
    time.sleep(5)

    return parser(values)

if __name__ == '__main__':
    import json

    # Prompt user for make, model, year, condition, and mileage of the car
    make = input('make?: ')
    model = input('model?: ')
    year = input('year?: ')
    condition = input('condition? (Poor, Fair, Good, Very Good, or Excellent): ')
    mileage = input('mileage?: ')

    # Print available styles for the car and their corresponding number
    print(f'\nAvailable styles for a {year} {model}...')
    available_styles = get_styles(
        searalize(make), 
        searalize(model), 
        searalize(year))

    for i, style in enumerate(available_styles):
        print(f'{i+1}. {style}')

    # Prompt user for the style number corresponding to the desired style
    style_index = int(input('Style number?: '))
    style = available_styles[style_index-1]

    # Print price ranges for trade-in and private party sales
    print(f'\nPrice ranges for a {year} {style} {model}...')
    trade_in_ranges = get_ranges(
        searalize(make), 
        searalize(model), 
        searalize(style), 
        searalize(year), 
        searalize(condition, replace_with=''), 
        searalize(mileage),
        trade_in=True)
    
    print(f"Trade in prices range from {trade_in_ranges['low']} to {trade_in_ranges['high']}")

    private_party_ranges = get_ranges(
        searalize(make), 
        searalize(model), 
        searalize(style), 
        searalize(year), 
        'good', 
        searalize(mileage),
        trade_in=False)
    
    print(f"Private party prices range from {private_party_ranges['low']} to {private_party_ranges['high']}")

    # Calculate potential profit range and average
    best_delta = dollar_to_int(private_party_ranges['high']) - dollar_to_int(trade_in_ranges['low'])
    worst_delta = dollar_to_int(private_party_ranges['low']) - dollar_to_int(trade_in_ranges['high'])
    avg_delta = dollar_to_int(private_party_ranges['value']) - dollar_to_int(trade_in_ranges['value'])

    # Print potential profit range and average
    print(f"The potential profit delta ranges from ${worst_delta} to ${best_delta} and averages around ${avg_delta}")