from flask import render_template, url_for, flash, redirect, request, Response, Flask, session
from flask_login import login_user, current_user, logout_user, login_required
from FrontEnd import app, bcrypt
from FrontEnd.forms import RegistrationForm, LoginForm
from Backend.server import add_new_user, verify_credentials
import sys
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("You need to login or signup to view that.")
            return redirect(url_for('login'))
    return wrap

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
    error = None
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        success = add_new_user(form.username.data, 
                               request.form['password'],
                               form.email.data,
                               form.image.data)
        if success:
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username ' + form.username.data + ' already exists, Please try alternative Username')
            error = 'Username already exists'
    return render_template('register.html', title='Register', form=form)

  
#_______________________________________________________________________________________________________________

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        if verify_credentials(request.form['username'], request.form['password']):
            session['logged_in'] = True
            session['current_user'] = form.username.data
            flash('You are now logged in!', 'success')
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials. Please try again.'
            flash('Login Unsuccessful. Please check Email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#_______________________________________________________________________________________________________________

@app.route("/face_recognition", methods=['GET', 'POST'])
def facerecognition():
   return render_template('videofeed.html', title='Facial Recognition')

#_______________________________________________________________________________________________________________

@app.route("/logout")
@login_required
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