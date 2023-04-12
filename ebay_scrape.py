import json
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from ebay_scrubber import Scrubber
from utils import DescriptionError, clean_strings, dollar_to_int, remove_items_between_strings, search_a_in_b

def get_item_specs(url):
    """
    Get item specifications from a given URL.

    Parameters:
    url (str): A string representing the URL of the webpage containing the item specifications.

    Returns:
    dict: A dictionary containing the cleaned and scrubbed specifications of the item, such as the condition, VIN, options, and power options.

    Note:
    This function uses the requests library to send an HTTP request to the given URL, and then uses the BeautifulSoup library to parse the HTML content of the response. It then extracts the relevant specifications from the HTML using certain HTML tags and classes.

    This function also makes use of the Scrubber class to clean and scrub the extracted specifications before returning them in a dictionary format.
    """

    # Sends an HTTP request to the URL and obtains the response
    with requests.get(url) as page:

        # Parses the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(page.text, 'html.parser')

        # Extracts the HTML content for the item's specifications
        stats = soup.find_all(class_='vim x-about-this-item')[0]

        # Creates an empty list to store the extracted data
        data = []

        # Iterates through each span tag with the 'ux-textspans' class in the HTML content of the item's specifications
        for stat in stats.find_all('span', 'ux-textspans'):
            # Appends the text content of the span tag to the data list
            data.append(stat.text)
        
        # Removes duplicate 'Used' strings
        caught_values = []
        for i, string in enumerate(data):
            if 'Used' in string:
                if 'Used' in caught_values: del data[i]
                else: caught_values.append('Used')

        # Extracts the range of data between the 'Year' or 'Seller Notes' and 'Used' keys
        prev_string = data[0]
        range_start = data[0]
        range_end = data[-1]
        data = data[1:]

        for i, string in enumerate(data):
            if 'used' in string: range_start = data[i+1]
            if 'Seller Notes' in string: range_end = prev_string
            elif 'Year' in string: range_end = prev_string

            prev_string = string

        data = remove_items_between_strings(data, range_start, range_end)
        
        # Removes the final unwanted strings from the data
        new_data = []
        search_list = ['definitionsopens']
        for string in data:
            catches = 0
            for search in search_list:
                if search in string: 
                    catches += 1

            if catches == 0: new_data.append(string)

        data = new_data

        # Initializes an empty dictionary to store the extracted and cleaned specifications
        parsed_stats = {}

        # Iterates through the data list and extracts the key-value pairs for the specifications
        for i in range(1, len(data)):
            value = data[i-1]
            # Extracts the key as the string before the last character in the previous element of the data list
            if value[-1] == ':': key = value[:-1]
            else: key = value

            # Extracts the value as the cleaned string from the current element of the data list
            value = clean_strings(data[i])

            # Checks if the current element is a value and its index in the data list is odd
            if (i+1) % 2 == 0.0 and value != '':
                # Adds the key-value pair to the parsed_stats dictionary
                parsed_stats[key] = value
        
        # Initializes a Scrubber object to clean and scrub the parsed specifications
        s = Scrubber()
        # Cleans and scrubs the parsed specifications using the Scrubber object and stores the cleaned specifications and cleaning log
        cleaned_stats, cleaning_log = s.scrub(parsed_stats)

    # make sure that there is a body type option=
    if 'Body Type' not in cleaned_stats:
        cleaned_stats['Body Type'] = 'Null'

    # Returns the cleaned specifications dictionary
    return cleaned_stats


def get_listing_price(url):
    """
    Get the listing price of an item from a given URL.

    Parameters:
    url (str): A string representing the URL of the webpage containing the listing price.

    Returns:
    int: An integer representing the listing price in dollars, converted from the string format.

    Note:
    This function uses the requests library to send an HTTP request to the given URL, and then uses the BeautifulSoup library to parse the HTML content of the response. It then extracts the relevant listing price from the HTML using the find method with the attrs parameter to search for the HTML tag with the specified attributes.

    This function also makes use of the dollar_to_int function to convert the extracted listing price from a string format to an integer representing the number of dollars.
    """
    
    # Sends an HTTP request to the URL and obtains the response
    with requests.get(url) as page:

        # Parses the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(page.text, 'html.parser')

        # Extract the HTML tag containing the item price using the 'soup.find()' method, and pass in the 'attrs' parameter
        # to search for the HTML tag with the 'itemprop' attribute set to 'price'.
        price = soup.find('span', attrs={'itemprop':'price'})

        # Extract the text content of the price tag, and split it by whitespace to obtain the price value in a string format.
        price = price.text.split(' ')[-1]

    # Return the extracted price value as an integer by passing it to the 'dollar_to_int()' function.
    return dollar_to_int(price)


# get description
def get_description(url):
    
    custom_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument(f'user-agent={custom_user_agent}')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    browser.get(url)  # navigate to URL
    browser.switch_to.frame('desc_ifr')
    html = browser.page_source

    browser.quit()
    time.sleep(1)

    soup = BeautifulSoup(html, 'html.parser')

    try:
        desc = soup.find('div', id='vehicleDescription')
        desc_parsed = re.sub('\s+',' ',desc.text).strip()
    except:
        try:
            desc = soup.find('div', id='ds_div')
            desc_parsed = re.sub('\s+',' ',desc.text).strip()
        except:
            raise DescriptionError
        
    return desc_parsed

if __name__ == '__main__':
    urls = [
        'https://www.ebay.com/itm/225513444321?hash=item3481a613e1%3Ag%3A9g4AAOSwmgJkLb6m&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
        'https://www.ebay.com/itm/185842538842?hash=item2b4514195a%3Ag%3AwBsAAOSwd2lkLD8w&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
        'https://www.ebay.com/itm/204293191994?hash=item2f90d2b93a%3Ag%3AVO4AAOSwknBkKfm3&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049',
        'https://www.ebay.com/itm/115755211999?hash=item1af38c5cdf%3Ag%3A7-4AAOSwITBkKcBz&mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5337650957&customid=&toolid=10049'
    ]


    for url in urls:
        print(get_item_specs(url))
        print('\n\nPrepareing for next car\n\n\n')
