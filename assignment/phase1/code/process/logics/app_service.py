# app/services/app_service.py
from ..database.database import SessionLocal
from ..models.android_app import AndroidApp
from ..models.ios_app import IosApp

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
