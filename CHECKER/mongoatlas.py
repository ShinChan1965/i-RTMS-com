from pymongo import MongoClient
import certifi

#  uri = "mongodb+srv://USER:PASSWORD@cluster0.s5wpvyj.mongodb.net/?retryWrites=true&w=majority"
uri =  "mongodb+srv://shin104051_db_user:uaIrqrgzc061Jc5v@cluster1.cawpy2t.mongodb.net/?appName=Cluster1"
client = MongoClient(uri, tlsCAFile=certifi.where())

db = client["iRTMS"]
col = db["test"]

col.insert_one({"status": "connected", "source": "python"})

print("Inserted test document")
# print(db)
