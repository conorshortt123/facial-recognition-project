from flask import render_template, url_for, flash, redirect, request, Response, Flask, session
from flask_login import login_user, current_user, logout_user, login_required
from prototype import app, db, bcrypt
from prototype.forms import RegistrationForm, LoginForm #,searchForm
from prototype.models import User, Post
import sys
sys.path.insert(1, '../API')
from facial_recognition import generate
from upload_picture import upload_file

import sys
sys.path.insert(1, '../Backend')
from server import *


# MONGODB Imports
import pymongo
from pymongo import MongoClient

# Connect to server
cluster = MongoClient("mongodb+srv://admin:admin@users-qtiue.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["test"]
collection = db["test"]

posts = [
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

#_______________________________________________________________________________________________________________

@app.route("/search")
def search():
    return render_template('search.html', title='Search')

#_______________________________________________________________________________________________________________

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #Get registration form 
    form = RegistrationForm()
    
    #Validate Form Username to ensure no username is the same
    #Therefore making usernames a primary Key for the database
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        imagefile = request.form.get('Profile_pic')
        
        found = registerUser(form.username.data,form.email.data,form.password.data,imagefile)  
        
        if found == True:
            # if it is unsuccessful you are not moved
            return render_template('register.html', title='Register', form=form)
        elif found == False:
            flash('Your account has been created! You are now able to log in', 'success')
            # if it is successful you are returned home
            return redirect(url_for('home'))  
   # if it is unsuccessful you are not moved
    return render_template('register.html', title='Register', form=form)

  
#_______________________________________________________________________________________________________________

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        found = SignInUser(form.email.data,form.password.data)
        
        if found == True:
            flash('You are now logged in!', 'success')
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check Email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#_______________________________________________________________________________________________________________

@app.route("/face_recognition", methods=['GET', 'POST'])
def facerecognition():
   return render_template('videofeed.html', title='Facial Recognition')

#_______________________________________________________________________________________________________________

@app.route("/logout")
def logout():
    logout_user()
    session['logged_in'] = False
    return redirect(url_for('home'))

#_______________________________________________________________________________________________________________

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

#_______________________________________________________________________________________________________________

@app.route("/video_feed")
def video_feed():
   # return the response generated along with the specific media
   return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

#_______________________________________________________________________________________________________________

@app.route("/file_upload", methods=["GET", "POST"])
def file_upload():
    upload_file()
    return render_template("file_upload.html", title='File Upload')

#_______________________________________________________________________________________________________________

# @app.route("/about", methods=["GET", "POST"])
# def search():
    
    
#     print("DEBUGGING:1")
#     if request.method == 'POST':
#         email = request.form['text']
#         userName , userEmail , profilePic = retrieveDetails(email)
#         print("DEBUGGING:4")
#         return render_template('search.html',userName,userEmail,profilePic)
    
#     print("DEBUGGING:3")
#     return render_template('search.html')