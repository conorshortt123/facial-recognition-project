from datetime import datetime
import pymongo
from FrontEnd import bcrypt
from bcrypt import hashpw, gensalt
from pymongo import MongoClient
from FrontEnd import login_manager

try:
    conn=MongoClient('mongodb+srv://admin:admin@users-qtiue.mongodb.net/test?retryWrites=true&w=majority')
except pymongo.errors.ConnectionFailure as e:
    print ("Could not connect to MongoDB: {0}".format(e))
    sys.exit(1)

db = conn.get_default_database()
u_coll = db.users
@login_manager.user_loader
def load_user(user_id):
    return add_new_user.u_coll.find(int(user_id))

def add_new_user(username,firstName,secondName,address,mobileNumber,password, email, Image,npArray):
    print(password)
    if not u_coll.find_one({'username': username}):
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
            "FaceRecArray":Image,
            "NumpyArray":npArray
        }
        u_coll.insert(user)
        return True
    else:
        print ("Username {0} signup attempted: taken".format(username))
        return False

def verify_credentials(username,password_attempt):
    try:
        hsh = u_coll.find_one({'username': username},{'_id':0,'hash':1})['hash']
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

def retrieveDetails(searchEmail):
    found = False
        
    results = collection.find({"email":searchEmail})
    for result in results:
        print(result)

        if result["email"] == searchEmail:
            #User Found
            print("Email Found")
            
            username = result["userName"]
            email = result["email"]
            profilePic = result["Image"]
            
            return username,email,profilePic