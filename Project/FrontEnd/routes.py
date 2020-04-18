from flask import render_template, url_for, flash, redirect, request, Response, Flask, session
from flask_login import login_user, current_user, logout_user, login_required
from FrontEnd import app, bcrypt
from FrontEnd.forms import RegistrationForm, LoginForm ,searchForm
from FrontEnd.camera import Camera
from Backend.server import add_new_user, verify_credentials,retrieveDetails, retrieveNumpy
import sys
import os
import shutil
from PIL import Image
from functools import wraps
sys.path.insert(1, './API')
from facial_recognition import encodeImageBinary, encodeImageNumpy, encodeImageFaceRec, decodeBinaryToNumpy, compareImages, encodeByteToBase64

from PIL import Image

camera = None
credsVerified = False
username = ""
CAPTURES_DIR = "./Frontend/static/captures/"

def get_camera():
    global camera
    if not camera:
        camera = Camera()

    return camera

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
@app.route("/home",methods=['GET','POST'])
def home():
    error = None
    if request.method == 'POST':
        username = request.form.get('UserName')
        username,firstName,secondName,address,email,mobileNumber,Image = retrieveDetails(username)
        print(username,firstName,secondName,address,email,mobileNumber)
        
        Data = [username,firstName,secondName,address,email,mobileNumber]
        
        Image = Image.decode('utf-8')
        
        return render_template('home.html',user = Data,Image = Image)
    return render_template('home.html')



@app.route('/camera/')
def index():
    return render_template('camera.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    error = None
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':

        # Encoding image to face recognition array, and numpy array to be stored in database.
        imagefile = form.image.data
        binary_encoding = encodeByteToBase64(imagefile)
        numpy_encoding = encodeImageNumpy(imagefile)

        success = add_new_user(form.username.data,
                               form.firstName.data,
                               form.secondName.data,
                               form.address.data,
                               form.MobileNum.data,         
                               request.form['password'],                                                    
                               form.email.data,         
                               binary_encoding,
                               numpy_encoding)
        if success:
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username ' + form.username.data + ' already exists, Please try alternative Username')
            error = 'Username already exists'
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    global credsVerified
    global username

    if username:
        print(username)
        checkface(username)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        if verify_credentials(request.form['username'], request.form['password']):

            if not credsVerified:
                return render_template('camera.html')
        else:
            error = 'Invalid credentials. Please try again.'
            flash('Login Unsuccessful. Please check Email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/checkface", methods=['GET', 'POST'])
def checkface(user):
    try:
        # Open image taken while logging in.
        img_name = 'test.jpg'
        img = CAPTURES_DIR + img_name

        # Encode login image
        img1 = encodeImageFaceRec(img)
        print(img1)

        # Get registered image from database and decode from binary to numpy
        knownFace = retrieveNumpy(user)

        img2 = decodeBinaryToNumpy(knownFace)
        print(img2)

        # Compare two numpy arrays
        result = compareImages(img1, img2)

        if result:
            session['logged_in'] = True
            session['current_user'] = user
            flash('You are now logged in!', 'success')
        else:
            flash("Faces didn't match", 'error')

        return redirect(url_for('home'))

    except IOError:
        print("Couldn't open image")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


def gen(camera):
    while True:
        frame = camera.get_feed()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed/')
def video_feed():
    camera = get_camera()
    return Response(gen(camera),
        mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/capture/')
def capture():
    camera = get_camera()
    stamp = camera.capture()
    print("STAMP = " + stamp)
    return redirect(url_for('show_capture', timestamp=stamp))


@app.route('/capture/image/<timestamp>', methods=['POST', 'GET'])
def show_capture(timestamp):
    path = "captures/" + timestamp + ".jpg"
    print("PATH = " + path)

    return render_template('capture.html',
        stamp=timestamp, path=path)

#_______________________________________________________________________________________________________________
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