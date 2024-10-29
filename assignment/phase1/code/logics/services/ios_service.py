# app/services/ios_service.py
from ..models.ios_app import IosApp
from .app_service import AppService
from logics.database import SessionLocal
from sqlalchemy.orm import Session

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
