import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

myClient = MongoClient(os.getenv("MONGO_URI"))
myDB = myClient[os.getenv("DB_NAME")]