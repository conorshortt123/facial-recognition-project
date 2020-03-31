from flask import render_template, url_for, flash, redirect, request, Response, Flask, session
from flask_login import login_user, current_user, logout_user, login_required
from prototype import app, db, bcrypt
from prototype.forms import RegistrationForm, LoginForm
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
    {
        'author': 'Tim Smith',
        'title': 'Blog Post',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Mark Reilly',
        'title': 'Facial Recognition',
        'content': 'First post content',
        'date_posted': 'February 12, 2020'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

#_______________________________________________________________________________________________________________

@app.route("/about")
def about():
    return render_template('about.html', title='About')

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
         
        found = registerUser(form.username.data,form.email.data,form.password.data)  
        
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

        found = False
        searchEmail = form.email.data
        searchPass = form.password.data
        print("searchEmail " + searchEmail)
        #Search database for the entered username
        results = collection.find({"email":searchEmail})
        for result in results:
            print(result)

            if result["email"] == searchEmail:
                print("Email Found")
                if result["password"]==searchPass:
                    found = True

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

@app.route("/file_upload", methods=["GET", "POST"])
def file_upload():
    upload_file()
    return render_template("file_upload.html", title='File Upload')