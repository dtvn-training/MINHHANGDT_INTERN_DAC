from google_play_scraper import app
from ..models.android_app import AndroidApp

class AndroidDataCollector:
    def __init__(self):
        self.android_apps = []

    def collect_android_data(self, app_ids):
        for app_id in app_ids:
            try:
                result = app(app_id, lang='en', country='vi')
                android_app = AndroidApp(
                    app_id=app_id,
                    app_name=result.get("title", "Unknown"),
                    category=result.get("genre", "Unknown"),
                    price=float(result.get("price", "0")),
                    provider=result.get("developer", "Unknown"),
                    description=result.get("description", "Unknown"),
                    developer_email=result.get("developerEmail", "Unknown"),
                )
                self.android_apps.append(android_app)
            except Exception as e:
                print(f"Failed to crawl app {app_id}: {e}")

    def get_collected_android_apps(self):
        return self.android_apps

