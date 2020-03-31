from flask import render_template, url_for, flash, redirect, request, Response, Flask, session
from flask_login import login_user, current_user, logout_user, login_required
from prototype import app, db, bcrypt
from prototype.forms import RegistrationForm, LoginForm
from prototype.models import User, Post
import sys
sys.path.insert(1, '../API')
from facial_recognition import generate
from upload_picture import upload_file


# MONGODB Imports
import pymongo
from pymongo import MongoClient

# Connect to server
cluster = MongoClient("mongodb+srv://admin:admin@users-qtiue.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["test"]
collection = db["test"]

def registerUser(username,email,password):

    found = False
    searchEmail = email
    print("searchEmail " + searchEmail)
    #Search database for the entered username 
    results = collection.find({"email":searchEmail})
    for result in results:
        print(result)

        # If found the 'found' variable becomes true it fails the 
        # registration attempt as the username is taken
        if result["email"] == searchEmail:
            found = True
            print("User Found")
            print(result["email"])

    # If not found the 'found' variable remains false and 
    # the registration succeeds as the username isn't taken
    if found == False:
        #Add details to mongoDB database 
        post = {"userName":username,"password":password,"email":email}
        collection.insert_one(post)
        
    return found
    
