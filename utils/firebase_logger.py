import firebase_admin
from firebase_admin import credentials, firestore
import os
import datetime

class FirebaseLogger:
    def __init__(self):
        self.cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.cred = credentials.Certificate(self.cred_path)
        self.app = firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

    def log_to_firebase(self, collection, document, data):
        try:
            self.db.collection(collection).document(document).set(data)
            print(f"Logged to Firebase: {data}")
        except Exception as e:
            print(f"Error logging to Firebase: {e}")

    def log_message(self, message, level='INFO'):
        log_data = {
            'message': message,
            'level': level,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        self.log_to_firebase('logs', f"log-{datetime.datetime.utcnow().isoformat()}", log_data)

# Initialize FirebaseLogger instance
firebase_logger = FirebaseLogger()

def log_message(message, level='INFO'):
    firebase_logger.log_message(message, level)

