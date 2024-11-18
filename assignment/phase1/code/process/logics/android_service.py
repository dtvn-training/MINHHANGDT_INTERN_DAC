# app/services/android_service.py
from ..models.android_app import AndroidApp
from .app_service import AppService
from ..database.database import SessionLocal
from sqlalchemy.orm import Session

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
