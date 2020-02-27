from flask import render_template, url_for, flash, redirect, request, Response, Flask
from imutils.video import VideoStream
from prototype import app, db, bcrypt
from prototype.forms import RegistrationForm, LoginForm
from prototype.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import time
import numpy as np
import datetime
import cv2
import threading
import face_recognition
import imutils
#from prototype.facerecog import recognize_face

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("./prototype/trained/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file("./prototype/trained/biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Load my own picture and learn how to recognize it.
my_image = face_recognition.load_image_file("./prototype/trained/image.jpg")
my_face_encoding = face_recognition.face_encodings(my_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
	my_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden",
	"Conor Shortt"
]

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

# Initialize some variables
outputFrame = None
lock = threading.Lock()
vs = VideoStream(src=0).start()
time.sleep(2.0)

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
		db.session.add(user)
		db.session.commit()
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
	if user and bcrypt.check_password_hash(user.password, form.password.data):
		login_user(user, remember=form.remember.data)
		next_page = request.args.get('next')
		return redirect(next_page) if next_page else redirect(url_for('home'))
	else:
		flash('Login Unsuccessful. Please check username and password', 'danger')
		return render_template('login.html', title='Login', form=form)


@app.route("/face_recognition", methods=['GET', 'POST'])
def facerecognition():
	return render_template('videofeed.html', title='Facial Recognition')


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
	return render_template('account.html', title='Account')


def recognize_face():
	global vs, outputFrame, lock
	face_locations = []
	face_encodings = []
	face_names = []
	process_this_frame = 1

	# loop over frames from the video stream
	while True:
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		# Resize frame to 1/4 size for faster processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
		rgb_small_frame = small_frame[:, :, ::-1]

		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
					cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		if process_this_frame == 4:
			process_this_frame = 0
			# Find all the faces and face encodings in the current frame of video
			face_locations = face_recognition.face_locations(rgb_small_frame)
			face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

			face_names = []
			for face_encoding in face_encodings:
				# See if the face is a match for the known face(s)
				matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
				name = "Unknown"
				face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
				best_match_index = np.argmin(face_distances)
				if matches[best_match_index]:
					name = known_face_names[best_match_index]

				face_names.append(name)

		process_this_frame += 1

		# Display the results
		for (top, right, bottom, left), name in zip(face_locations, face_names):
			# Scale back up face locations since the frame we detected in was scaled to 1/4 size
			top *= 4
			right *= 4
			bottom *= 4
			left *= 4

			# Draw a box around the face
			cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

			# Draw a label with a name below the face
			cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
			font = cv2.FONT_HERSHEY_DUPLEX
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()


def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock

	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
			   bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

