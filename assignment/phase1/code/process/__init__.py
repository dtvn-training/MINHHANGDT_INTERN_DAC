from .database.database import init_db

def create_app():
    init_db()