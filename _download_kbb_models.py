import os
import sys
import pandas as pd
from bs4 import BeautifulSoup
import requests
  
path = 'html.html'
url = 'https://www.kbb.com/car-make-model-list/used/view-all/model/'

with requests.get(url) as page:
    # for getting the header from
    # the HTML file
    list_header = []
    soup = BeautifulSoup(page.text, 'html.parser')
    header = soup.find_all("table")[0].find("tr")
    
    for items in header:
        try:
            list_header.append(items.get_text())
        except:
            continue
    list_header = list_header[-4:-1]
    
    # for getting the data
    HTML_data = soup.find_all("table")[0].find_all("tr")[1:]

    # empty list
    count = 0
    data = []
    for row in HTML_data:
        sub_data = []
        for element in row:
            try:
                sub_data.append(element.get_text())

            except:
                continue
        data.append(sub_data[-4:-1])
        
    # Storing the data into Pandas
    # DataFrame
    dataFrame = pd.DataFrame(data = data, columns = list_header)

    dataFrame.to_csv('models_years_db.csv')
