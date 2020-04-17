from flask import render_template, url_for, flash, redirect, request, Response, Flask, session
from flask_login import login_user, current_user, logout_user, login_required
from FrontEnd import app, bcrypt
from FrontEnd.forms import RegistrationForm, LoginForm
from FrontEnd.camera import Camera
from Backend.server import add_new_user, verify_credentials
import sys
import os
import shutil
from functools import wraps
sys.path.insert(1, './API')
from facial_recognition import encodeImageBinary, encodeImageNumpy

camera = None
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

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
@app.route("/home")
def home():
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
        print(form.image.data)
        imagefile = request.files['image']
        print(imagefile)
        binary_encoding = encodeImageBinary(imagefile)

        success = add_new_user(form.username.data,
                               form.firstName.data,
                               form.secondName.data,
                               form.address.data,
                               form.MobileNum.data,         
                               request.form['password'],                                                    
                               form.email.data,         
                               binary_encoding)
        if success:
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Username ' + form.username.data + ' already exists, Please try alternative Username')
            error = 'Username already exists'
    return render_template('register.html', title='Register', form=form)


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
    #path = stamp_file(timestamp)
    path = "captures/" + timestamp + ".jpg"
    print("PATH = " + path)

    return render_template('capture.html',
        stamp=timestamp, path=path)

@app.route('/training/face/upload', methods=['POST'])
def face_upload():
    target = os.path.join(APP_ROOT, 'face-images/')  #folder path
    if not os.path.isdir(target):
            os.mkdir(target)     # create folder if not exits
    face_db_table = d.mongo.db.faces  # database table name
    if request.method == 'POST':
        for upload in request.files.getlist("face_image"): #multiple image handel
            filename = secure_filename(upload.filename)
            destination = "/".join([target, filename])
            upload.save(destination)
            face_db_table.insert({'face_image': filename})   #insert into database mongo db

        return 'Image Upload Successfully'

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