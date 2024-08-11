from pymongo import MongoClient
from bson.objectid import ObjectId
from config.database import (
    MongoDBClient,
)  # Ensure this file contains the MongoDBClient setup


def fetch_blueprint(camera_id):
    # Initialize MongoDB connection
    mongo_client = MongoDBClient()
    db = mongo_client.get_client()

    # Access the Camera collection and fetch the blueprint
    camera_collection = db["test"][
        "cameras"
    ]  # Update with the correct database name if different
    camera_doc = camera_collection.find_one({"_id": ObjectId(camera_id)})

    if not camera_doc:
        raise ValueError("Camera not found")

    blueprint = camera_doc.get("blueprint")

    if not blueprint:
        raise ValueError("Blueprint not found for the given Camera")

    # Return the prepared data
    return blueprint
