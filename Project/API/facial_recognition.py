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
import io
from base64 import b64encode


def encodeByteToBase64(image):
	# Open img with PIL
	im = Image.open(image)

	# Create bytesio object and save image
	bytesio = io.BytesIO()
	im.save(bytesio, 'jpeg')

	# Encode image to base 64 and return.
	b64img = b64encode(bytesio.getvalue())

	return b64img

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
	image_encoding = face_recognition.face_encodings(image_file)[0]
	bArray = Binary(pickle.dumps(image_encoding, protocol=2), subtype=128)

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

	result = face_recognition.compare_faces([image_encoding1], image_encoding2)

	return result