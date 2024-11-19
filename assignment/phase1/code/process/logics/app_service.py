# app/services/app_service.py
from ..database.database import SessionLocal
from ..models.android_app import AndroidApp
from ..models.ios_app import IosApp
from sqlalchemy.orm import Session

class AppService:
    def __init__(self):
        self.session = SessionLocal()

    def insert_app(self, app_obj):
        try:
            self.session.add(app_obj)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error inserting app: {e}")
        finally:
            self.session.close()

    def get_app_by_id(self, app_id, op_sys):
        try:
            if op_sys == 'android':
                return self.session.query(AndroidApp).filter(AndroidApp.app_id == app_id).first()
            else:
                return self.session.query(IosApp).filter(IosApp.app_id == app_id).first()
        finally:
            self.session.close()

class AndroidService(AppService):
    def get_android_apps(self):
        return self.session.query(AndroidApp).all()
    
    def insert_multiple_android_apps(self, android_apps):
        """
        Insert multiple Android apps into the database.
        Only inserts apps that are not already in the database.
        """

        # Initialize a session to interact with the database
        with SessionLocal() as session:
            # print("1")
            for app in android_apps:
                # Check if app exists in DB
                # print(type(app))
                # print("app in android service: ", app)
                if not self.app_exists(session, app.app_id):
                    try:
                        # If not exists, add new app to DB
                        session.add(app)
                        session.commit()
                    except Exception as e:
                        session.rollback()  # Rollback if has error
                        print(f"Failed to insert Android app {app.app_id}: {e}")
    
    def app_exists(self, session: Session, app_id: str) -> bool:
        """
        Check if an Android app with the given app_id already exists in the database.
        """
        # Query DB to check if app_id exists or not
        return session.query(AndroidApp).filter(AndroidApp.app_id == app_id).first() is not None

class IosService(AppService):
    def get_ios_apps(self):
        return self.session.query(IosApp).all()
    
    def insert_multiple_ios_apps(self, ios_apps):
        """
        Insert multiple Ios apps into the database.
        Only inserts apps that are not already in the database.
        """

        # Initialize a session to interact with the database
        with SessionLocal() as session:
            for app in ios_apps:
                # Check if app exists in DB
                if not self.app_exists(session, app.app_id):
                    try:
                        # If not exists, add new app to DB
                        session.add(app)
                        session.commit()
                    except Exception as e:
                        session.rollback()  # Rollback if has error
                        print(f"Failed to insert Android app {app.app_id}: {e}")
    
    def app_exists(self, session: Session, app_id: str) -> bool:
        """
        Check if an Ios app with the given app_id already exists in the database.
        """
        # Query DB to check if app_id exists or not
        return session.query(IosApp).filter(IosApp.app_id == app_id).first() is not None
    

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
