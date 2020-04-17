from imutils.video import VideoStream
import threading
import datetime
import imutils
import time
import cv2
import numpy as np
import face_recognition
from bson.binary import Binary
import pickle
from PIL import Image

# Initialize some variables
outputFrame = None
lock = threading.Lock()
time.sleep(2.0)
vs = VideoStream(src=0).start()

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("./API/trained/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
biden_image = face_recognition.load_image_file("./API/trained/biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# Load my own picture and learn how to recognize it.
#my_image = face_recognition.load_image_file("./API/trained/image.jpg")
#my_face_encoding = face_recognition.face_encodings(my_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden"
]

# Initialize some variables
outputFrame = None
frame = None
lock = threading.Lock()
# vs = VideoStream(src=0).start()
time.sleep(2.0)


def recognize_face():
	global vs, outputFrame, lock, frame
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


def encodeImageBinary(image):

	image_file = face_recognition.load_image_file(image)
	image_encoding = face_recognition.face_encodings(image_file)[0]

	bArray = Binary(pickle.dumps(image_encoding, protocol=2), subtype=128)

	return bArray


def encodeImageFaceRec(image):

	image_file = face_recognition.load_image_file(image)
	image_encoding = face_recognition.face_encodings(image_file)[0]

	return image_encoding

def encodeImageNumpy(image):

	image_file = face_recognition.load_image_file(image)
	bArray = Binary(pickle.dumps(image_file, protocol=2), subtype=128)

	return bArray

def decodeNumpyToImage(encoded_image):

	numpy = decodeBinaryToNumpy(encoded_image)
	image = Image.fromarray(numpy)

	return image


def decodeBinaryToNumpy(bArray):

	image_encoding = pickle.loads(bArray)
	return image_encoding

	return image_encoding


def compareImages(image_encoding1, image_encoding2):

	result = face_recognition.compare_faces([image_encoding1, image_encoding2])

	return result