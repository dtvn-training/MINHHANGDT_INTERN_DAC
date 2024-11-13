**File main.py**

- Description:

This file serves as the entry point for initiating the data crawling process for both Android and iOS applications. It orchestrates the execution of crawlers for both platforms and ensures that the necessary database is initialized before starting the crawling operations.

* Components:

- main():
The main function that drives the crawling process for both Android and iOS apps. It first starts the Android app data crawling by calling the main_android() function, then follows with the iOS app data crawling by calling the main_ios() function. After each crawling process, it prints confirmation messages to indicate the completion of the respective tasks.
Error handling is implemented to catch any exceptions that may occur during the crawling processes, with a clear error message printed if an issue arises.

- init_db():
This function is called at the beginning of the script to initialize the database schema. It ensures that the database tables are created before any data is crawled and stored.
Purpose:

The primary purpose of this file is to serve as the main execution script for crawling app data from both the Google Play Store (Android) and the Apple App Store (iOS). It ensures the correct initialization of the database and triggers the crawling processes for both platforms.


This file is meant to be run directly, as it includes the check if __name__ == "__main__", which ensures that the database is initialized and the crawling tasks are executed when the script is run.

