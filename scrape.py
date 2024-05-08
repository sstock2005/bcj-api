from bs4 import BeautifulSoup
from constants import URL, HEADERS
import urllib3
import datetime
import requests
import json

def scrape(local):

    last_remote_time = "NA"
    timestamp = datetime.datetime.now(datetime.UTC)
    
    inmate_list = []

    if not local:
        last_remote_time = timestamp
        urllib3.disable_warnings()
        response = requests.get(url=URL, headers=HEADERS, verify=False) # cannot verify because their SSL is broken
        soup = BeautifulSoup(response.text, 'html.parser')
        response.close()
    else:
        with open('local.htm', 'r') as file:
            soup = BeautifulSoup(file, 'html.parser')

    class Inmate:
        def __init__(self, name, age, offenses):
            self.name = name
            self.age = age
            self.offenses = offenses

    for inmate in soup.select('tr[class^="inmate"]'):
        name_data = inmate.find_all('td', class_ = 'col1')
        age_data = inmate.find_all('td', class_ = 'col3')

        if name_data:
            name = name_data[0].text
        
        if age_data:
            age = age_data[0].text

        name_parts = name.split(', ')
        first_middle_name = name_parts[1].split(' ')
        first_name = first_middle_name[0]
        middle_initial = first_middle_name[1][0] if len(first_middle_name) > 1 else ''
        last_name = name_parts[0]

        name = f"{first_name} {middle_initial} {last_name}" if middle_initial else f"{first_name} {last_name}"

        inmate_expanded = inmate.find_next_sibling('tr')
        if inmate_expanded is not None and 'showhide' in inmate_expanded['class']:
            offenses = inmate_expanded.find_all('li')
            offense_list = []
            if offenses:
                for offense in offenses:
                    offense_list.append(offense.text)
            
            inmate_list.append(Inmate(name, age, offense_list))


    inmate_dict = []
    for list_item in inmate_list:
        i = {
            "name": list_item.name,
            "age": int(list_item.age),
            "offenses": list_item.offenses
        }
        inmate_dict.append(i)

    json_data = {
        "last_updated": str(last_remote_time),
        "inmates": inmate_dict
    }

    json_str = json.dumps(json_data, indent=4)

    return json_str