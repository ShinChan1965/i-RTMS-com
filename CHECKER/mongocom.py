
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")


# Database
db = client["bus_management"]

# Collections
passenger_collection = db["passenger_counts"]
print(list(passenger_collection.find()))