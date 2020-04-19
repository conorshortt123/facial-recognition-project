from datetime import datetime
from bcrypt import hashpw, gensalt
from flask import flash
import pymongo
from pymongo import MongoClient
from FrontEnd import login_manager
from FrontEnd import bcrypt
import sys
sys.path.insert(1, './API')
    

"""Connecting to the MongoDB server.

 Set the MongoClient ,DB and collection 
 in order to connect to the mongoDB database

"""
try:
    conn=MongoClient('mongodb+srv://admin:admin@users-qtiue.mongodb.net/test?retryWrites=true&w=majority')
except pymongo.errors.ConnectionFailure as e:
    print ("Could not connect to MongoDB: {0}".format(e))
    sys.exit(1)

db = conn.get_default_database()
collection = db.users


#Load user 
@login_manager.user_loader
def load_user(user_id):
    return add_new_user.collection.find(int(user_id))


"""Add new user to the MongoDB database

Parameters:
 username : String
 firstName : String
 secondName : String
 address : String
 mobileNumber : String
 password : String
 email : String
 Image : binary_encoding
 npArray : numpy_encoding

:returns 
If True:
    Adds the user to the database
    Returns a success message
else:
    Returns an error message
"""
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


"""Verify the entered username and password are correct

Parameters:
 username : String
 password_attempt : String

:returns 
If True:
    Allows the user Access
else:
    Returns an error message
"""
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


"""retrieve a users Details from the database

Parameters:
 searchusername : String

:returns 
If User Found:
    Return all user details
else:
    Returns an error message
"""
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

        flash("User Not Found!", 'danger')
        userName = None
        firstName = None
        secondName = None
        address = None
        email = None
        mobileNum = None
        Image = None
        return userName,firstName,secondName,address,email,mobileNum,Image


"""Retrieve Numpy Data for use in facial recognition

Parameters:
 searchusername : String

:Returns
    Return the numpyArray
"""
def retrieveNumpy(searchusername):
    results = collection.find({"username": searchusername})
    for result in results:
        print(result['username'])

    numpy = result['NumpyArray']

    return numpy