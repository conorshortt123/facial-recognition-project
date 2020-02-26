# Imports =======================================
import pymongo
from pymongo import MongoClient

# Connect to the Database =======================================

cluster = MongoClient("mongodb+srv://admin:admin@users-qtiue.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["test"]
collection = db["test"]

# Variables =======================================
addUser = 1
name = "conor"


# FUNCTIONS =======================================
def AddUser():
    if addUser == 1:
        post = {"_id":4,"firstName":"John"}
        collection.insert_one(post)
        print("Added User")
    else:
        print("error")

def DisplayUsers():
    results = collection.find({})
    for result in results:
        print(result)

def DeleteUsers():
    results = collection.delete_one({"_id":0})



# Body =======================================
AddUser()
DisplayUsers()