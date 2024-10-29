from logics.services.android_service import AndroidService
from logics.services.ios_service import IosService
from logics.models.android_app import AndroidApp
from logics.models.ios_app import IosApp
from ..utils.utils import clean_data
from sqlalchemy.orm import Session

class DataStore:
    """Data Store class"""

    def __init__(self, session: Session):
        # Initialize services to manage data storage for Android and iOS
        self.android_service = AndroidService()
        self.ios_service = IosService()
        self.session = session

    def make_app(self, data, op_sys):
        """Tạo đối tượng app Android hoặc iOS dựa trên hệ điều hành"""
        if op_sys == 'ios':
            app_ = IosApp(
                app_id=data["app_id"],
                app_name=data["app_name"],
                category=data["category"],
                price=data["price"],
                provider=data["provider"],
                description=data["description"],
                score=data["score"],
                cnt_rates=data["cnt_rates"],
                subtitle=data["subtitle"],
                link=data["link"],
                img_links=','.join(data["img_links"])
            )
            return app_
        else:
            app_ = AndroidApp(
                app_id=data['app_id'],
                app_name=data['app_name'],
                category=data['category'],
                price=data['price'],
                provider=data['provider'],
                description=data['description'],
                developer_email=data['developer_email']
            )
            return app_

    def insert_values(self, data_list, op_sys):
        """Clean and insert values ​​into database for Android or iOS"""
        try:
            # Clean data
            cleaned_data = clean_data(data_list, self.session, op_sys)

            if op_sys == 'ios':
                ios_apps = [self.make_app(data, op_sys) for data in cleaned_data]
                # call service insert multiple ios apps
                self.ios_service.insert_multiple_ios_apps(ios_apps)
            else:
                android_apps = [self.make_app(data, op_sys) for data in cleaned_data]
                # call service insert multiple android apps
                self.android_service.insert_multiple_android_apps(android_apps)

        except Exception as e:
            print(f"Error while inserting values for {op_sys}: {e}")
