import re
from difflib import SequenceMatcher
import pandas as pd
import json

def dollar_to_int(str):
    if '.' in str:
        str = str.split('.')[:-1]
        str = ''.join(str)
        
    val = serialize(str, replace_with='')
    return float(val)

def thousands(input):
    if type(input) != int or type(input) != float:
        input = int(input)
    
    return f'{input:,}'

def serialize(str, replace_with='-'):
    # lowercase
    lowercase = str.lower()

    #replace all non alpabet chars with a -
    replaced = ''.join([ c if c.isalnum() else replace_with for c in lowercase ])

    return replaced

def title_case(s):
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), s)

def clean_strings(str:str):
    str = str.strip()
    str = str.strip('~`\{\}[]!%^*-=+_|\/@:;<>?.,#&$()')
    str = title_case(str)
    return str

def search_a_in_b(list_a, list_b):
    for a in list_a:
        if a in list_b:
            return True
    return False

def remove_items_between_strings(my_list, start_string, end_string):
    i = 0
    while i < len(my_list):
        if start_string in my_list[i]:
            j = i + 1
            while j < len(my_list) and end_string not in my_list[j]:
                j += 1
            if j < len(my_list):
                del my_list[i:j+1]
        else:
            i += 1
    return my_list

def calc_simalarity(a:str, b:str):
    return SequenceMatcher(None, a, b).ratio()

def get_best_pair(a:list, b:list):
    data = []

    for a_item in a:
        for b_item in b:
            data.append([a_item, b_item, calc_simalarity(a_item, b_item)])
    
    data = pd.DataFrame(data, columns=['a', 'b', 'ratio'])
    best = data[data['ratio']==data['ratio'].max()]

    return best

def dict_format(dict):
    return json.dumps(dict, indent=4)


class StyleException(Exception):
    pass

class DescriptionError(Exception):
    pass

if __name__ == '__main__':
    print(thousands('1000'))
    print(thousands(1000))
    print(thousands(1000.0))