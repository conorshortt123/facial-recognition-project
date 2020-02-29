from flask import render_template, url_for, flash, redirect, request
from prototype import app, db, bcrypt
from prototype.forms import RegistrationForm, LoginForm
from prototype.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

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


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        #Add details to mongoDB database 
        post = {"userName":form.username.data,"password":form.password.data,"email":form.email.data}
        collection.insert_one(post)

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        results = collection.find({"email":form.email.data})

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')