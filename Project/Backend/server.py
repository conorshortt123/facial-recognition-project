from datetime import datetime
from bcrypt import hashpw, gensalt
from flask import flash
import pymongo
from pymongo import MongoClient
from FrontEnd import login_manager
from FrontEnd import bcrypt
import sys
sys.path.insert(1, './API')
from facial_recognition import decodeNumpyToImage
    

#Connect to Mongo Database
try:
    conn=MongoClient('mongodb+srv://admin:admin@users-qtiue.mongodb.net/test?retryWrites=true&w=majority')
except pymongo.errors.ConnectionFailure as e:
    print ("Could not connect to MongoDB: {0}".format(e))
    sys.exit(1)

db = conn.get_default_database()
collection = db.users


#Load User
@login_manager.user_loader
def load_user(user_id):
    return add_new_user.collection.find(int(user_id))

#Add new user to the MongoDB database
def add_new_user(username,firstName,secondName,address,mobileNumber,password, email, Image,npArray):
    print(password)

    #If username not found add user.
    if not collection.find_one({'username': username}):
        #hashed = hashpw(password.encode('utf8'),gensalt(12))
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = {
            "username": username,
            "firstName": firstName,
            "secondName": secondName,
            "address": address,
            "mobileNumber": mobileNumber,
            "hash": hashed,
            "email": email,
            "b64Array":Image,
            "NumpyArray":npArray
        }
        collection.insert(user);
        return True
    else:
        print ("Username {0} signup attempted: taken".format(username))
        return False


#Verifiy entered username and password are correct
def verify_credentials(username,password_attempt):
    try:
        hsh = collection.find_one({'username': username},{'_id':0,'hash':1})['hash']
        print(hsh)
    except TypeError:
        print ("No such username")
        return False
    #if hashpw(password_attempt.encode('utf-8'),hsh) == hsh:
    if bcrypt.check_password_hash(hsh, password_attempt):
        print ("Creds verified")
        return True
    else:
        print ("Password Mismatch")
        return False


def retrieveDetails(searchusername):
    #Initialize result 
    result = []
    
    #Search the Database for the user
    results = collection.find({"username":searchusername})
    
    #Change results from cursor and put into result list
    for result in results:
        print(result['username'])

    #If details are found return details
    if len(result) > 1:

        userName = result['username']
        firstName = result['firstName']
        secondName = result['secondName']
        address = result['address']
        email = result['email']
        mobileNum = result['mobileNumber']
        Image = result['b64Array']
        print(userName,firstName,secondName,address,email,mobileNum)
        
        return userName,firstName,secondName,address,email,mobileNum,Image

    else:    
        #If nothing is found return set all to None
        # and return error message

        flash("User Not Found!", 'danger')
        userName = None
        firstName = None
        secondName = None
        address = None
        email = None
        mobileNum = None
        Image = None
        return userName,firstName,secondName,address,email,mobileNum,Image

#Retrieve Numpy Data for use in facial recognition
def retrieveNumpy(searchusername):
    results = collection.find({"username": searchusername})
    for result in results:
        print(result['username'])

    numpy = result['NumpyArray']

    return numpy