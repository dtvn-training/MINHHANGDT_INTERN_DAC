import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from ..models.android_app import AndroidApp
from ..models.ios_app import IosApp

def list_to_string(data):
    """turn list into list"""
    if isinstance(data, list):
        return ' '.join(map(list_to_string, data))  # deque turn element to string
    elif isinstance(data, dict):
        return str(data)  # dictionary to string
    else:
        return str(data)  # other element to string

def extract_quoted_strings(data):
    """extract string inside quote sign"""

    # Regular expression finds all strings within double quotes
    quoted_strings = re.findall(r'"com(.*?)"', data)
    return quoted_strings

def find_list_android_app_ids(language, country, length, chart_name, category_id):
    """find list of android_app's id"""

    url = f'https://play.google.com/_/PlayStoreUi/data/batchexecute?hl={language}&gl={country}'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }

    # Prepare the body similar to the f.req structure in the original request
    body = {
        'f.req': json.dumps([
            [
                [
                    'vyAe2',
                    json.dumps([[None, [[None, [None, length]], None, None, [113]], [2, chart_name, category_id]]])
                ]
            ]
        ])
    }

    response = requests.post(url, headers=headers, data=body)
    response_text = response.text
    if response_text.startswith(")]}'"):
        response_text = response_text[4:]

    # Now try to load the cleaned string
    try:
        json_str = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")

    string_result = list_to_string(json_str)
    quoted_strings = extract_quoted_strings(string_result)
    app_strings = ['com' + link for link in quoted_strings]

    return app_strings

def find_df_ios_app(url):
    """find list of ios_app contain rank, title, subtitle, link, img_links"""

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    top_list = soup.find('ol', role='feed')

    df = pd.DataFrame(columns=['rank', 'title', 'subtitle', 'link', 'img_links'])
    apps_data = top_list.find_all('li')

    for app_data in apps_data:  
        link_tag = app_data.find('a')
        
        # if 'a' tag was founded
        if link_tag:  
            link = link_tag.get('href')
            
            # get images lnk
            images = app_data.find('div').find('picture').find_all('source')
            image_link = [img.get('srcset') for img in images]

            # get rank
            rank = link_tag.find('p', class_='we-lockup__rank').get_text()
            
            # get title
            title = link_tag.find('div', class_='we-lockup__text').find('div', class_='we-lockup__title').find(
                'div',  class_='we-truncate we-truncate--multi-line targeted-link__target'
            ).find('p').get_text()
            
            # get subtitle
            sub_title = link_tag.find('div', class_='we-lockup__text').find('div', class_='we-truncate we-truncate--single-line we-lockup__subtitle').get_text()

            # add data into DataFrame
            temp_df = pd.DataFrame({
                'rank': [rank],
                'title': [title],
                'subtitle': [sub_title],
                'link': [link],
                'img_links': [image_link]
            })
            
            # combine to main data frame
            df = pd.concat([df, temp_df], ignore_index=True)
        else:
            print("Không tìm thấy thẻ <a> với class 'we-lockup  targeted-link'")

    return df

def is_record_exists(session, app_id, op_sys):
    """Check if the record already exists in the database."""
    if op_sys == 'ios':
        app = session.query(IosApp).filter(IosApp.app_id == app_id).first()
    else:
        app = session.query(AndroidApp).filter(AndroidApp.app_id == app_id).first()
    
    return app is not None

def clean_data(data_list, session, op_sys):
    """Filter data, remove duplicate records before inserting."""
    cleaned_data = []
    seen_ids = set()

    for data in data_list:
        app_id = data["app_id"]
        # Check if the record already exists in the database
        if app_id not in seen_ids and not is_record_exists(session, app_id, op_sys):
            cleaned_data.append(data)  # Add to cleaned_data if not already present
            seen_ids.add(app_id)  # Mark app_id as encountered
    return cleaned_data

