from logics.services.android_service import AndroidService
from logics.services.ios_service import IosService
from .utils import find_df_ios_app, find_list_android_app_ids
from logics.collectors.android_data_collector import AndroidDataCollector
from logics.collectors.ios_data_collector import IosDataCollector
from logics.services.data_store import DataStore
from logics.database import SessionLocal 

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