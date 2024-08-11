from pymongo import MongoClient
import os

class MongoDBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance

    def initialize(self, username, password, host):
        username = username or os.getenv('DB_USERNAME')
        password = password or os.getenv('DB_PASSWORD')
        host = host or os.getenv('DB_HOST')

        if not all([username, password, host]):
            raise ValueError("Database credentials are not fully set. Please check your environment variables.")

        uri = f"mongodb+srv://{username}:{password}@{host}?retryWrites=true&w=majority"
        self._client = MongoClient(uri)
        print("Connected to database")

    def get_client(self):
        return self._client
    
