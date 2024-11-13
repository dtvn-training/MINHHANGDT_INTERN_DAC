**File main.py**

- Description:

This file serves as the entry point for initiating the data crawling process for both Android and iOS applications. It orchestrates the execution of crawlers for both platforms and ensures that the necessary database is initialized before starting the crawling operations.

- Components:

    - main(): The main function that drives the crawling process for both Android and iOS apps. It first starts the Android app data crawling by calling the main_android() function, then follows with the iOS app data crawling by calling the main_ios() function. After each crawling process, it prints confirmation messages to indicate the completion of the respective tasks.
    - Error handling is implemented to catch any exceptions that may occur during the crawling processes, with a clear error message printed if an issue arises.

    - init_db(): This function is called at the beginning of the script to initialize the database schema. It ensures that the database tables are created before any data is crawled and stored.

- Purpose: The primary purpose of this file is to serve as the main execution script for crawling app data from both the Google Play Store (Android) and the Apple App Store (iOS). It ensures the correct initialization of the database and triggers the crawling processes for both platforms.

This file is meant to be run directly, as it includes the check if __name__ == "__main__", which ensures that the database is initialized and the crawling tasks are executed when the script is run.

**File database.py**

- Description:

This file manages the connection to the database and contains the logic for initializing and managing SQLAlchemy sessions. It provides the necessary components for establishing a connection to the database, handling session management, and initializing the database schema.

- Components:

    - Base: An instance of declarative_base() from SQLAlchemy, which is used as the base class for all models. It is essential for the class-based table mapping in the database.
    - engine: Created using the create_engine() function from SQLAlchemy, this represents the connection to the database. It uses the database URI provided in the Config.SQLALCHEMY_DATABASE_URI configuration variable, which stores the connection string to the database.
    - SessionLocal: This is a session maker bound to the engine, created using sessionmaker(). It is used to generate database sessions, which are necessary for interacting with the database in a transactional context.

- Function:

    - init_db(): Initializes the database by creating all the tables defined by the SQLAlchemy models. It uses Base.metadata.create_all() to generate the schema based on the models' definitions. This ensures that the necessary tables are created in the database if they don't already exist.

**File models/app.py**
- Description:

This file defines an abstract base class AppData, which serves as a foundational model for storing common attributes of app data in the database. The class is designed to be extended by specific app models such as Android or iOS apps.

- Class: AppData (Base): This is an abstract class that inherits from SQLAlchemy's Base class, allowing it to be used as a database model.
    - The class defines common fields that are shared by both Android and iOS app models, including:

        - app_id (String): A unique identifier for the app.
        - app_name (String): The name of the app.
        - category (String): The category the app belongs to (e.g., games, utilities).
        - price (Float): The price of the app.
        - provider (String): The developer or company that provides the app.
        - description (Text): A description of the app.
  
    - Constructor: The __init__ method is used to initialize instances of the class. It takes parameters for app_id, app_name, category, price, provider, and description to assign values to the corresponding attributes of the model.

- Purpose: The AppData class is intended to serve as a base class for app-related models, encapsulating the common attributes that apply to different types of apps. By making it abstract, it ensures that this class will not be directly instantiated but rather extended by other concrete models.

**File models/android_app.py**
- Description:

This file defines the AndroidApp class, which represents the data model for Android apps in the database. The class inherits from the abstract AppData class and is specifically tailored to store Android app information.

- Class: AndroidApp (AppData): This class inherits from AppData, a base class that defines common app attributes such as app_id, app_name, category, price, provider, and description. The AndroidApp class extends this by adding a specific field for developer_email, which is unique to Android apps.

  
    - The __tablename__ attribute specifies the name of the table in the database where Android app data will be stored ('app_android').
    - The class contains the following fields:
  
        - app_id (String): The unique identifier for the Android app (primary key).
        - app_name (String): The name of the Android app.
        - category (String): The category to which the app belongs.
        - price (Float): The price of the app.
        - provider (String): The company or developer providing the app.
        - description (Text): A detailed description of the app.
        - developer_email (String): The email address of the app's developer.

  - Constructor:
  
    The __init__ method initializes an AndroidApp object by calling the constructor of the parent AppData class to initialize the common attributes (app_id, app_name, category, price, provider, description) and sets the developer_email specific to the Android app.
    Purpose:

The AndroidApp class models Android app data in the application. It stores detailed information about each Android app and is mapped to the app_android table in the database.
By extending AppData, it inherits common attributes for both Android and iOS apps, while also defining Android-specific fields like developer_email.

**File models/ios_app.py**
- Description:

This file defines the IosApp class, which represents the data model for iOS apps in the database. The class extends the abstract AppData class and is specifically designed to store detailed information about iOS apps.

- Class: IosApp (AppData): Inherits from the AppData base class, which includes common attributes such as app_id, app_name, category, price, provider, and description. The IosApp class adds iOS-specific fields, including score, cnt_rates, subtitle, link, and img_links.

    - The __tablename__ attribute specifies the name of the table in the database where iOS app data will be stored ('app_ios').
  
    - The class contains the following fields:
        - app_id (String): The unique identifier for the iOS app (primary key).
        - app_name (String): The name of the iOS app.
        - category (String): The category to which the app belongs.
        - price (Float): The price of the app.
        - provider (String): The company or developer providing the app.
        - description (Text): A detailed description of the app.
        - score (Float): The average user rating score of the app.
        - cnt_rates (Integer): The number of ratings the app has received.
        - subtitle (String): A brief subtitle or tagline for the app.
        - link (Text): The URL link to the app on the App Store.
        - img_links (Text): Links to the images associated with the app (e.g., screenshots).

  - Constructor:

    The __init__ method initializes an IosApp object by calling the parent constructor (AppData) to initialize the common attributes (app_id, app_name, category, price, provider, description) and adds iOS-specific fields such as score, cnt_rates, subtitle, link, and img_links.

- Purpose:

The IosApp class models iOS app data in the system. It stores detailed information about each iOS app and is mapped to the app_ios table in the database.
By extending the AppData class, it benefits from shared attributes used by both Android and iOS apps, while also including iOS-specific data like rating information (score, cnt_rates) and links to the app and images.

**File collectors/ios_data_collector.py**

- Description: This Python file defines the IosDataCollector class, which is responsible for scraping and collecting data about iOS apps from the App Store. 
It uses BeautifulSoup to parse HTML and extract relevant app information from the provided URLs.

- Dependencies: 
    The script imports BeautifulSoup for HTML parsing, requests for making HTTP requests, and the IosApp model to store the collected app data. 
    Additionally, sqlalchemy.Integer is used for managing numeric fields, and re is employed for regular expression operations.

- Class:

    IosDataCollector: This class is designed to fetch and store iOS app information, 
    such as the app's description, rating, number of reviews, price, category, and provider.

- Methods:

    - __init__: Initializes an empty list ios_apps to store the collected app data.
    - collect_ios_data(df_ids): This method takes in a DataFrame of app IDs and associated URLs. 
        It scrapes the app details from each provided URL and populates the list of IosApp objects with relevant information, 
        including the description, score, number of ratings, category, provider, and price.
    - get_collected_ios_apps(): Returns the list of collected iOS apps.


**File collectors/android_data_collector.py**

- Description:

This Python file implements the AndroidDataCollector class, which is responsible for scraping and collecting data from the Google Play Store. The class leverages the google_play_scraper library to extract app information based on provided app IDs.

- Dependencies: The script imports the app function from the google_play_scraper library to fetch app details, and uses the AndroidApp model to store and manage the collected data.

- Class: AndroidDataCollector: A class designed to gather metadata about Android apps from the Google Play Store.
- Methods:

    - __init__: Initializes an empty list android_apps to store the collected Android app data.
    - collect_android_data(app_ids): Accepts a list of app IDs, fetches the details for each app using google_play_scraper, and stores the results in the android_apps list. For each app, it retrieves information such as the app name, category, price, provider (developer), description, and developer email. If an error occurs during the scraping process, it logs the app ID and the error message.
    - get_collected_android_apps(): Returns the list of AndroidApp objects that have been collected.
    This class simplifies the process of obtaining structured Android app data from the Play Store, which can then be used for further analysis or application-specific tasks.

**File services/app_service**
- Description:

This Python file defines the AppService class, which provides an interface for interacting with the database to insert and retrieve app data for both Android and iOS apps. The class handles database operations such as adding new app records and querying app details based on app ID.

- Dependencies:

    SessionLocal: Provides the database session used for querying and committing data.
    AndroidApp and IosApp: Data models representing Android and iOS apps in the database.
- Class:

    - AppService: This class serves as a service layer for database interactions related to mobile apps.
    - Methods:

        - __init__: Initializes a new database session using SessionLocal().
        - insert_app(app_obj): Inserts a given app object (either an AndroidApp or IosApp) into the database. It commits the transaction if successful, or rolls it back and prints an error message in case of failure.
        - get_app_by_id(app_id, op_sys): Retrieves an app record from the database based on the app_id and the operating system (op_sys). It queries either the AndroidApp or IosApp table depending on the provided OS type.
This class abstracts away direct database operations, making it easier to manage app-related data in a clean and reusable manner. It also ensures safe handling of transactions with proper rollback mechanisms in case of errors.


**File services/android_service.py**
- Description:

This Python file defines the AndroidService class, which extends the AppService class to provide Android-specific database operations. It enables batch insertion of Android apps while ensuring no duplicates are added, and includes methods for retrieving all Android apps and checking if an app already exists in the database.

- Dependencies:

    - AndroidApp: The model representing Android apps in the database.
    - AppService: The base service class for common database operations.
    - SessionLocal: Used to establish a session with the database.
    - sqlalchemy.orm.Session: Used for typing database sessions in method signatures.
- Class:

    - AndroidService: A service class specialized in handling operations related to Android apps in the database.
    - Methods:

        - get_android_apps(): Retrieves all Android apps from the database.
        - insert_multiple_android_apps(android_apps): Inserts multiple Android app objects into the database, but only if they do not already exist. It iterates through the list of apps and performs a check for each app ID. If the app is not found in the database, it inserts the app; otherwise, it skips it. In case of an error, the transaction is rolled back.
        - app_exists(session, app_id): A helper method that checks if an Android app with the given app_id exists in the database by querying the AndroidApp model.
    This class streamlines the process of adding Android app data to the database, ensuring data integrity by avoiding duplicates and handling exceptions during batch inserts.

**File services/ios_service.py**
- Description
This Python file defines the IosService class, which extends the AppService class to provide iOS-specific operations for interacting with the database. It includes methods for inserting multiple iOS apps into the database while preventing duplicate entries, retrieving all iOS apps, and checking if an app already exists based on its app ID.

- Dependencies:

    - IosApp: The model representing iOS apps in the database.
    - AppService: The base service class that provides common database operations.
    - SessionLocal: Manages database session creation.
    - sqlalchemy.orm.Session: Used for typing database sessions in method signatures.
- Class:

    - IosService: A specialized service class for handling database operations related to iOS apps.
    - Methods:
          - get_ios_apps(): Fetches all iOS apps from the database.
          - insert_multiple_ios_apps(ios_apps): Inserts multiple iOS apps into the database. It first checks if each app is already present by querying the app_id. If the app is not found, it inserts it into the database. In case of an error during insertion, the transaction is rolled back to prevent partial data insertion.
          - app_exists(session, app_id): A helper method that checks whether an iOS app with a specific app_id exists in the database by querying the IosApp model.
This class simplifies bulk iOS app insertion and retrieval while ensuring data consistency by preventing duplicate entries.

**File service/data_store.py**
- Description:

This Python file defines the DataStore class, which is responsible for managing the data storage and insertion process for both Android and iOS apps. It interacts with the Android and iOS service layers to clean and insert app data into the database.

- Dependencies:

    - AndroidService, IosService: Service classes that handle the database operations for Android and iOS apps, respectively.
    - AndroidApp, IosApp: Models representing Android and iOS apps in the database.
    - clean_data: A utility function that cleans and validates app data before insertion.
    - sqlalchemy.orm.Session: Used for managing the database session passed to the DataStore class.
- Class: DataStore: A class that centralizes the logic for creating app objects and inserting them into the database for both Android and iOS platforms.
    - Methods:

        - __init__(session): Initializes the DataStore class by setting up the database session and service classes for Android and iOS apps.
        - make_app(data, op_sys): Creates an instance of either AndroidApp or IosApp based on the op_sys (operating system) parameter, populating the app object with the provided data.
        - insert_values(data_list, op_sys): Cleans the incoming app data using clean_data and then inserts multiple app records into the database. The method delegates to either insert_multiple_android_apps or insert_multiple_ios_apps based on the operating system (op_sys). It handles any exceptions that occur during the insertion process, logging errors as needed.
This class abstracts the process of handling Android and iOS app data, including the necessary cleaning, object creation, and database insertion steps. By centralizing these operations, DataStore ensures that app data is managed consistently across both platforms.

**File utils/crawl_util.py**
- Description:

This file defines a set of functions that handle the crawling, data collection, and storage of Android and iOS apps from their respective app stores. The file primarily utilizes two services, AndroidService and IosService, along with data collectors (AndroidDataCollector and IosDataCollector) to scrape app information and save it to the database.

- Dependencies:

    - AndroidService, IosService: Manage database operations for Android and iOS apps.
    - AndroidDataCollector, IosDataCollector: Handle the crawling and scraping of Android and iOS app data.
    - DataStore: Facilitates the storage of collected app data into the database.
    - SessionLocal: Manages database session interactions.
    - find_list_android_app_ids: Utility function to retrieve Android app IDs from the Google Play Store.
    - find_df_ios_app: Utility function to retrieve iOS app data from a given URL.
- Functions:

    - crawl_android(language, country, chart_name, category_id, length): Crawls the Google Play Store for Android apps based on the specified language, country, chart name (e.g., top free, top paid), and category ID. It collects app data using the AndroidDataCollector, processes it, and stores it in the database via the DataStore.
    - main_android(): Main function for executing Android app crawling. It calls crawl_android() to retrieve top free, top grossing, and top paid Android apps from the Google Play Store in Vietnam.
    - crawl_ios(url): Crawls iOS apps from the Apple App Store using a given URL (for charts like top free or top paid). It utilizes IosDataCollector to scrape app data and stores it using DataStore.
    - main_ios(): Main function for executing iOS app crawling. It calls crawl_ios() to retrieve top free and top paid apps from the Apple App Store in Vietnam.
    - Error Handling: Both crawl_android() and crawl_ios() include error handling to catch and log any exceptions that occur during the crawling and data storage process, ensuring robustness and aiding debugging.

**File utils/utils.py**
- Description:

This file contains utility functions to support the collection and processing of Android and iOS app data. It includes methods for retrieving app IDs from Google Play, parsing app details from the Apple App Store, and handling data cleaning before inserting it into the database.

- Dependencies:

    - requests, BeautifulSoup: For web scraping and making HTTP requests.
    - json, re, pandas: For handling JSON data, regular expressions, and tabular data.
    - AndroidApp, IosApp: ORM models representing Android and iOS apps.
    - Session: For interacting with the database.
- Functions:

    - list_to_string(data):

        Recursively converts a list, dictionary, or other data types into a string representation. It is primarily used to handle deeply nested data structures extracted from web requests.

    - extract_quoted_strings(data):
    
        Extracts substrings that are enclosed in double quotes from a given text. This is useful for isolating relevant pieces of data, such as app IDs, from a larger JSON-like structure.

    - find_list_android_app_ids(language, country, length, chart_name, category_id):

        Sends a POST request to the Google Play Store’s backend to retrieve app IDs based on specific criteria like language, country, chart type (e.g., top free), and category. The function cleans the response and extracts Android app IDs for further processing.

    - find_df_ios_app(url):
    
        Scrapes the Apple App Store’s top apps list from a given URL. The function parses the HTML response using BeautifulSoup to extract details such as rank, title, subtitle, link, and image links. The data is returned as a pandas DataFrame for easy manipulation.

    - is_record_exists(session, app_id, op_sys):

        Checks whether a record with a given app ID already exists in the database, based on the operating system (iOS or Android). It queries the respective database table to prevent duplicate entries.

    - clean_data(data_list, session, op_sys):
    
        Filters and removes duplicate app records from a list of scraped data. It ensures that only unique and non-duplicated records (based on app ID) are included, making it efficient for bulk inserts into the database. Uses is_record_exists() to verify if the app is already stored.
