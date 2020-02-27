from flask import Flask, json, Response, render_template
from imutils.video import VideoStream
import threading
import datetime
import imutils
import time
import cv2
import numpy as np
import face_recognition

app = Flask(__name__)

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("./trained/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file("./trained/biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Load my own picture and learn how to recognize it.
my_image = face_recognition.load_image_file("./trained/image.jpg")
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

# Initialize some variables
outputFrame = None
lock = threading.Lock()

vs = VideoStream(src=0).start()
time.sleep(2.0)


def success_handle(output, status=200, mimetype='application/json'):
	return Response(output, status=status, mimetype=mimetype)


def error_handle(error_message, status=500, mimetype='application/json'):
	return Response(json.dumps({"error": {"message": error_message}}), status=status, mimetype=mimetype)


@app.route('/', methods=['GET'])
def index():
	# Return the rendered html template
	return render_template("index.html")


@app.route('/api/train', methods=['POST'])
def train():
	output = json.dumps({"success": True})
	return success_handle(output)


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
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
	
	# start a thread that will perform face recognition
	t = threading.Thread(target=recognize_face)
	t.daemon = True
	t.start()

	# start the flask app
	app.run(debug=True, threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()