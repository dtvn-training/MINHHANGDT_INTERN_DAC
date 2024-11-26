from assignment.phase1.code.process.logics.execute import main_android, main_ios
from process.database.database import init_db

def main():
    """Main function to start the crawlers for both Android and iOS apps."""
    try:
        # Crawl Android apps
        print("Starting Android data crawling...")
        main_android()
        print("Android data crawling completed.")
        # Crawl iOS apps
        print("Starting iOS data crawling...")
        main_ios()
        print("iOS data crawling completed.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        

if __name__ == "__main__":
    init_db()
    main()
