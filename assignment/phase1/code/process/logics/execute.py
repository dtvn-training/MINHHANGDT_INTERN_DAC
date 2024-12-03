import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from ..models.android_app import AndroidApp
from ..models.ios_app import IosApp
from .app_service import AndroidService
from .app_service import IosService
from .android_data_collector import AndroidDataCollector
from .ios_data_collector import IosDataCollector
from .app_service import DataStore
from ..database.database import SessionLocal
import os
import logging
# from assignment.phase1.code.process.logics.android_service import AndroidService
# from assignment.phase1.code.process.logics.ios_service import IosService
# from process.logics.android_data_collector import AndroidDataCollector
# from process.logics.ios_data_collector import IosDataCollector
# from assignment.phase1.code.process.logics.data_store import DataStore
# from assignment.phase1.code.process.database.database import SessionLocal 


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
                    json.dumps([[None, [[None, [None, length + 50]], None, None, [113]], [2, chart_name, category_id]]])
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

    app_strings_return = app_strings[:length]

    return app_strings_return

def find_df_ios_app(url, DRYRUN):
    if DRYRUN:
            # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
            logging.info("[DRYRUN] Simulating find IOS data")
            ios_df = pd.DataFrame({
                'rank': [1],
                'title': ['ios_app1'],
                'subtitle': ['this is ios app 1'],
                'link': ['example1.com'],
                'img_links': ['img1.com']
            },
            {
                'rank': [2],
                'title': ['ios_app2'],
                'subtitle': ['this is ios app 2'],
                'link': ['example2.com'],
                'img_links': ['img2.com']
            },
            {
                'rank': [3],
                'title': ['ios_app3'],
                'subtitle': ['this is ios app 3'],
                'link': ['example3.com'],
                'img_links': ['img3.com']
            })
            return ios_df
    
    """find list of ios_app contain rank, title, subtitle, link, img_links"""

    response = requests.get(url, allow_redirects=False)
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

def crawl_android(language, country, chart_name, category_id, length):
    """Crawl Android apps data from Google Play Store"""

    try:
        collector = AndroidDataCollector()
        android_app_ids = find_list_android_app_ids(language, country, length, chart_name, category_id)
        collector.collect_android_data(android_app_ids)
        collected_android_apps = collector.get_collected_android_apps()


        data_to_store = [{
        "app_id": app.app_id,
        "app_name": app.app_name,
        "category": app.category,
        "price": app.price,
        "provider": app.provider,
        "description": app.description,
        "developer_email": app.developer_email,
        } for app in collected_android_apps]

        session = SessionLocal()
        store = DataStore(session)
        store.insert_values(data_to_store, 'android')

        print(f"Successfully crawled and stored {len(data_to_store)} Android apps.")
    except Exception as e:
        print(f"An error occurred while crawling Android data: {e}")
        return None

def main_android():
    """Main function for crawling Android apps"""
    length = 100
    crawl_android('en', 'vn', 'topselling_free', 'APPLICATION', length)  # top free
    print("Done crawling top free Android apps.")
    crawl_android('en', 'vn', 'topgrossing', 'APPLICATION', length)  # top grossing
    print("Done crawling top grossing Android apps.")
    crawl_android('en', 'vn', 'topselling_paid', 'APPLICATION', length)  # top paid
    print("Done crawling top selling paid Android apps.")

def crawl_ios(url):
    """crawl ios apps"""
    
    try:
        #crawl data android app from google play store
        collector = IosDataCollector()
        ios_df = find_df_ios_app(url)

        collector.collect_ios_data(ios_df)
        collected_ios_apps = collector.get_collected_ios_apps()
        
        data_to_store = [{
            "app_id": app.app_id,
            "app_name": app.app_name,
            "category": app.category,
            "price": app.price,
            "provider": app.provider,
            "description": app.description,
            "score": app.score,
            "cnt_rates": app.cnt_rates,
            "subtitle": app.subtitle,
            "link": app.link,
            "img_links": app.img_links,
        } for app in collected_ios_apps]

        # Save data to database

        # ios_service = IosService()
        # ios_service.insert_multiple_ios_apps(data_to_store)

        session = SessionLocal()
        store = DataStore(session)
        store.insert_values(data_to_store, 'ios')

        print(f"Successfully crawled and stored {len(data_to_store)} iOS apps.")

    except Exception as e:  # Catch all exceptions
        print(f"An error occurred: {e}")  # Log the error message
        return data_to_store  # Return the problematic data for further investigation

def main_ios():
    """Main function for crawling iOS apps"""
    url_top_free = 'https://apps.apple.com/vn/charts/iphone/top-free-apps/36'
    url_top_paid = 'https://apps.apple.com/vn/charts/iphone/top-paid-apps/36'

    crawl_ios(url_top_free)  # top free
    print("Done crawling iOS top free apps.")
    crawl_ios(url_top_paid)  # top paid
    print("Done crawling iOS top paid apps.")

def process_android_data(android_app_ids):
    collector = AndroidDataCollector()
    collector.collect_android_data(android_app_ids)
    collected_android_apps = collector.get_collected_android_apps()

    data_to_store = [{
        "app_id": app.app_id,
        "app_name": app.app_name,
        "category": app.category,
        "price": app.price,
        "provider": app.provider,
        "description": app.description,
        "developer_email": app.developer_email,
    } for app in collected_android_apps]

    # Lưu dữ liệu vào cơ sở dữ liệu
    session = SessionLocal()
    store = DataStore(session)
    store.insert_values(data_to_store, 'android')
    return data_to_store

def process_ios_data(ios_df):
    collector = IosDataCollector()
    collector.collect_ios_data(ios_df)
    collected_ios_apps = collector.get_collected_ios_apps()

    data_to_store = [{
        "app_id": app.app_id,
        "app_name": app.app_name,
        "category": app.category,
        "price": app.price,
        "provider": app.provider,
        "description": app.description,
        "score": app.score,
        "cnt_rates": app.cnt_rates,
        "subtitle": app.subtitle,
        "link": app.link,
        "img_links": app.img_links,
    } for app in collected_ios_apps]

    # Store data in database
    session = SessionLocal()  # Initialize your session correctly
    store = DataStore(session)
    store.insert_values(data_to_store, 'ios')

    return data_to_store

def get_android_ids(chart_name, length):
    language = "en"
    country = "vi"
    category_id = "APPLICATION"
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
                    json.dumps([[None, [[None, [None, int(length) + 50]], None, None, [113]], [2, chart_name, category_id]]])
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

    app_strings_return = app_strings[:int(length)]

    return app_strings_return

def run_find_android_data(output_file_path, chart_name, length, DRYRUN):
    if DRYRUN:
            # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
            logging.info("[DRYRUN] Simulating find android data")
            android_app_ids = ['com.example.app1', 'com.example.app2', 'com.example.app3']
            
            output_dir = os.path.dirname(output_file_path)
            os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu nó chưa tồn tại 

            target_file = output_file_path
            if os.path.exists(target_file):
                logging.warning(f"File {target_file} already exists. Renaming or deleting it.")
                os.remove(target_file)  # Or you can rename the file

            with open(output_file_path,'w') as f:
                for app_string in android_app_ids:
                    f.write(app_string + '\n')
            return
    
    # print("LINK FIND RUN_FIND_ANDROID_DATA: ", output_file_path)
    # Check if the file exists and remove it
    # Tạo thư mục nếu chưa tồn tại
    output_dir = os.path.dirname(output_file_path)
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu nó chưa tồn tại 
    
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    app_strings_return = get_android_ids(chart_name, length)
        
    with open(output_file_path, 'w') as file:
        for app_string in app_strings_return:
            file.write(app_string + '\n')

def run_process_android_data(input_file_path, output_file_path, DRYRUN):
    if DRYRUN:
            output_dir = os.path.dirname(output_file_path)
            os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu nó chưa tồn tại
            target_file = output_file_path
            if os.path.exists(target_file):
                os.remove(target_file)  # Or you can rename the file

            # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
            logging.info("[DRYRUN] Simulating data processing for iOS app")
            with open(input_file_path, 'r') as input_file:
                    android_app_ids = input_file.read().splitlines()
            with open(output_file_path,'w') as f:
                f.write('Simulated data processing completed: ' + ', '.join(android_app_ids))
            return
    
    # print("INPUT FILE ", input_file_path)
    with open(input_file_path, 'r') as input_file:
        android_app_ids = input_file.read().splitlines()  # ensure it's a list of app IDs
       
    data_to_store = process_android_data(android_app_ids)

    output_dir = os.path.dirname(output_file_path)
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu nó chưa tồn tại
    # Check if the file exists and remove it
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    with open(output_file_path, 'w') as output_file:
        import json
        json.dump(data_to_store, output_file)

def run_process_ios_data(input_file_path, output_file_path, DRYRUN):
    if DRYRUN:
            
        target_file = output_file_path
        if os.path.exists(target_file):
            logging.warning(f"File {target_file} already exists. Renaming or deleting it.")
            os.remove(target_file)  # Or you can rename the file
            
        # Chế độ dry-run: Chỉ log và không thực hiện hành động thật
        logging.info("[DRYRUN] Simulating data processing for iOS app")
        ios_df = pd.read_csv(input_file_path)
        processed_data_df = pd.DataFrame(ios_df)
        processed_data_df.to_csv(output_file_path, index=False)
        return
    
    ios_df = pd.read_csv(input_file_path)
    data_to_store = process_ios_data(ios_df)

    # Save processed data to output file
    processed_data_df = pd.DataFrame(data_to_store)
    processed_data_df.to_csv(output_file_path, index=False)
