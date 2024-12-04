from bs4 import BeautifulSoup
import requests
from ..models.ios_app import IosApp
from sqlalchemy import Integer
import re

class IosDataCollector:
    """Ios data collector Class"""
    def __init__(self):
        self.ios_apps = []

    def collect_ios_data(self, df_ids):
        """
        Crawl app data from Google Play Store base on app_ids
        """
        for index, row in df_ids.iterrows():
            url = row['link']
            resp = requests.get(url, allow_redirects=False)
            bs_soup = BeautifulSoup(resp.text, 'html.parser')

            secs_list = bs_soup.find_all('section', class_='l-content-width section section--bordered')

            try:
                secs_des = secs_list[1]
                description = secs_des.find('p').get_text()
            except:
                description = ""
            
            if len(secs_list) >= 3:
                try:
                    secs = secs_list[2]
                    score = secs.find('div', class_='we-customer-ratings lockup').find(
                        'div', class_='we-customer-ratings__stats l-column small-4 medium-6 large-4'
                    ).find('div', class_='we-customer-ratings__averages').find('span').get_text()

                    cnt_rates = secs.find('div', class_='we-customer-ratings lockup').find(
                        'div', class_='we-customer-ratings__stats l-column small-4 medium-6 large-4'
                    ).find('div', class_='we-customer-ratings__count small-hide medium-show').get_text()
                    
                except:
                    score = 0
                    cnt_rates = 0
            else:
                score = 0
                cnt_rates = 0

            cater_ls = bs_soup.find_all('section', class_='l-content-width section section--bordered section--information')

            try: 
                cate = cater_ls[0]
                try: 
                    siz = cate.find('div', class_="information-list__item l-column small-12 medium-6 large-4 small-valign-top").find(
                        'dd', class_="information-list__item__definition"
                    ).get_text()
                except:
                    siz = 0
                
                try:
                    category = cate.find('dl', class_="information-list information-list--app medium-columns l-row").find_all(
                        'dd', class_="information-list__item__definition"
                    )[2].get_text()
                except:
                    category = ""

                try:
                    provider = cate.find('dl', class_="information-list information-list--app medium-columns l-row").find_all(
                    'dd', class_="information-list__item__definition"
                    )[0].get_text()
                except:
                    provider = ""

                try:
                    price = cate.find('dl', class_="information-list information-list--app medium-columns l-row").find_all(
                    'dd', class_="information-list__item__definition")[7].get_text()
                except:
                    price = "Free"

            except:
                continue

            if price == "Free":
                price = 0
                # Xóa ký tự không phải số
                # price = re.sub(r'[^\d]', '', price)
                # price = float(price) if price else 0


            ios_app = IosApp(
                    app_id=row['title'],
                    app_name=row['title'],
                    category=category,
                    price = price,
                    provider = provider,
                    description=description,
                    score = score,
                    cnt_rates = cnt_rates,
                    subtitle = row['subtitle'],
                    link = row['link'],
                    img_links = ','.join(row['img_links'])
                )
            
            self.ios_apps.append(ios_app)

    def get_collected_ios_apps(self):
        return self.ios_apps
    