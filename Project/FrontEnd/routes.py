from flask import render_template, url_for, flash, redirect, request, Response, session
from flask_login import current_user, logout_user
from FrontEnd import app, bcrypt
from FrontEnd.forms import RegistrationForm, LoginForm, searchForm
from FrontEnd.camera import Camera, remove_pic
from Backend.server import add_new_user, verify_credentials, retrieveDetails, retrieveNumpy
from functools import wraps
import sys

sys.path.insert(1, './API')
from facial_recognition import encodeImageNumpy, encodeImageFaceRec, decodeBinaryToNumpy, \
    compareImages, encodeByteToBase64


# Global Variables
global path
camera = None
username = ""
CAPTURES_DIR = "./Frontend/static/"


# Retrieve the Camera
def get_camera():
    global camera
    if not camera:
        camera = Camera()

    return camera


# Check to see if you are logged in or not
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login or signup to view that.")
            return redirect(url_for('login'))

    return wrap


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    """Home Function
    Allows the user to search for other users
     in the system via username. If the user is not found
     it will return nothing and give you an error.
    """
    error = None
    if request.method == 'POST':
        username = request.form.get('UserName')
        username, firstName, secondName, address, email, mobileNumber, Image = retrieveDetails(username)
        print(username, firstName, secondName, address, email, mobileNumber)

        Data = [username, firstName, secondName, address, email, mobileNumber]

        if Image is not None:
            Image = Image.decode('utf-8')
            return render_template('home.html', user=Data, Image=Image)

    return render_template('home.html')


#Render the camera template
@app.route('/camera/')
def index():
    """
    Render the camera template
    """
    return render_template('camera.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    """Load registration form. Encrypt the image file.
     Send the entered data to the server to verify
     the username has not been taken.
     If its not taken create the user
     and return the user to the home page.
    """
    error = None
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':

        # Encoding image to face recognition array, and numpy array to be stored in database.
        imagefile = form.image.data
        binary_encoding = encodeByteToBase64(imagefile)
        numpy_encoding = encodeImageNumpy(imagefile)

        if numpy_encoding is not "error":
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
                flash('Username ' + form.username.data + ' already exists, Please try alternative Username', 'danger')
                error = 'Username already exists'
        else:
            flash('No face detected in image, please upload an clear, front-facing image of your face.', 'danger')
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Check if the username exists.
     If it does not exist return an error message
     and return them to the login page.
     If the username exists allow the user to login
     and return them to the home page.
    """
    global username

    if username:
        checkface(username)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        if verify_credentials(request.form['username'], request.form['password']):
            return render_template('camera.html')
        else:
            error = 'Invalid credentials. Please try again.'
            flash('Login Unsuccessful. Please check Email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/checkface", methods=['GET', 'POST'])
def checkface(user):
    """
    Checks the picture the user took when logging in against the face they registered with.

    :param user: The username of the person logging in.
    :return: Home.html if the login is successful, else they stay on the login page.
    """
    try:
        # Open image taken while logging in.
        img = CAPTURES_DIR + path

        # Encode login image
        img1 = encodeImageFaceRec(img)
        if img1 is not "error":

            # Get registered image from database and decode from binary encoding to numpy
            known_face = retrieveNumpy(user)
            img2 = decodeBinaryToNumpy(known_face)

            # Compare two numpy arrays
            result = compareImages(img1, img2)

            if result[0]:
                session['logged_in'] = True
                session['current_user'] = user
                remove_pic()
                flash('Welcome ' + user + '. You are now logged in!', 'success')
                return redirect(url_for('home'))
            else:
                flash("Faces didn't match, please log in again.", 'danger')
                return redirect(url_for('login'))
        else:
            flash('No face detected in login, please take a clear, front-facing photo.', 'danger')
            return redirect(url_for('login'))
    except IOError:
        print("Couldn't open image")


# Log the user out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    return redirect(url_for('home'))


# Retrieve the current users details and display them
@app.route("/account")
@login_required
def account():
    request.method == 'GET'
    username = session['current_user']
    username, firstName, secondName, address, email, mobileNumber, Image = retrieveDetails(username)

    Data = [username, firstName, secondName, address, email, mobileNumber]

    Image = Image.decode('utf-8')
    return render_template('account.html', title='Account', user=Data, Image=Image)


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
    return redirect(url_for('show_capture', timestamp=stamp))


@app.route('/capture/image/<timestamp>', methods=['POST', 'GET'])
def show_capture(timestamp):
    global path
    path = "captures/" + timestamp + ".jpg"

    return render_template('capture.html',
                           stamp=timestamp, path=path)
