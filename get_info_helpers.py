import numpy as np
from difflib import SequenceMatcher, get_close_matches
from utils import dollar_to_int, thousands
from page import Page

def mileage_level(mileage:int) -> str:
    """
    Return a string describing the level of a given mileage.
    """
    if mileage < 25000: # If mileage is less than 25,000
        return 'very low mileage' # Return a string describing it as "very low mileage"
    if mileage < 50000: # If mileage is less than 50,000 (and not less than 25,000, due to previous if-statement)
        return 'low mileage' # Return a string describing it as "low mileage"
    elif mileage < 100000: # If mileage is less than 100,000 (and not less than 50,000, due to previous if-statement)
        return 'mid mileage' # Return a string describing it as "mid mileage"
    elif mileage < 150000: # If mileage is less than 150,000 (and not less than 100,000, due to previous if-statement)
        return 'high mileage' # Return a string describing it as "high mileage"
    elif mileage < 200000: # If mileage is less than 200,000 (and not less than 150,000, due to previous if-statement)
        return 'very high mileage' # Return a string describing it as "very high mileage"
    else: # If mileage is greater than or equal to 200,000
        return 'unbelievably high mileage' # Return a string describing it as "unbelievably high mileage"

def style_from_description(available_styles: list, description: str) -> str:
    """
    Returns the closest style option from the list of available_styles based on the description provided.

    Arguments:
    - available_styles (list): A list of style options to choose from.
    - description (str): The description from the listing to compare against the available styles.

    Returns:
    - A string representing the closest style option from the available_styles list based on the description.
    """
    try:
        print("[INFO] Extrapolating style from description")

        # Remove all non-alphanumeric and non-whitespace characters from description
        description = ''.join([ c if (c.isalnum() or c.isspace()) else '' for c in description ])
        words = description.split(' ')

        # Calculate the average length of a style option
        average_len_of_style = int(np.floor(np.mean([len(style.split(' ')) for style in available_styles])))

        # Generate pairs of words from the description
        pairs = []
        for i in range(len(words)-average_len_of_style):
            pair = ' '.join(words[i:i+average_len_of_style])
            pairs.append(pair)

        # Score each pair of words against each style option
        scored_pairs = {}
        for style in available_styles:
            pair_scores = []
            for pair in pairs:
                pair_scores.append(SequenceMatcher(None, style, pair).ratio())
            
            scored_pairs[style] = np.max(pair_scores)

        # Return the style option with the highest score
        return max(scored_pairs, key=scored_pairs.get)

    except:
        # If no matching style option is found, return the middle option
        print("[INFO] Couldn't extrapolate style level from listing. Picking middle option (median expense)")
        
        size = len(available_styles)
        middle_index = size//2
        return available_styles[middle_index]
    
    
def style_from_specs(available_styles, listing_specs):
    # Use trim from listing to pick the closest option from kbb
    return get_close_matches(listing_specs['Trim'], available_styles, cutoff=0)[0]

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