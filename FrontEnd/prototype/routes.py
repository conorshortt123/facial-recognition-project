from flask import render_template, url_for, flash, redirect, request, Response, Flask
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
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        found = False
        searchEmail = form.email.data
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
            post = {"userName":form.username.data,"password":form.password.data,"email":form.email.data}
            collection.insert_one(post)
            flash('Your account has been created! You are now able to log in', 'success')
            # if it is successful you are returned home
            return redirect(url_for('home'))
        else:
            flash('email already Taken!', 'error')

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

@app.route("/upload_image", methods=["GET", "POST"])
def upload_image():
    upload_file()
    return render_template("file_upload.html")