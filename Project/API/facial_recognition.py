import face_recognition
import pickle
import io
from base64 import b64encode
from bson.binary import Binary
from PIL import Image

"""
Encodes the image passed into a binary base64 array to be passed to the database.

Parameters:
    image(jpeg): Image to be encoded.

Returns:
    b64img(byte array): Image encoded as a binary array.
"""
def encodeByteToBase64(image):
    # Open img with PIL
    im = Image.open(image)
    # Create bytesio object and save image
    bytesio = io.BytesIO()
    im.save(bytesio, 'jpeg')
    # Encode image to base 64 and return.
    b64img = b64encode(bytesio.getvalue())

    return b64img


"""
Encodes the image passed into a numpy array used for facial recognition.
This numpy array is further encoded to a base64 array and stored in the database.

Parameters:
    image(jpeg): Image to be encoded.

Returns:
    binary_array(byte array): Numpy array encoded as a binary array.
"""
def encodeImageNumpy(image):
    # Opens image and converts to a numpy array
    image_file = face_recognition.load_image_file(image)
    # Converts numpy array to the array used by facial recognition
    encodings = face_recognition.face_encodings(image_file)
    if len(encodings) > 0:
        image_encoding = encodings[0]
    else:
        image_encoding = "error"
    # Encodes the array into a base64 binary array. Must be stored as a base64 array in MongoDB.
    if image_encoding is not "error":
        binary_array = Binary(pickle.dumps(image_encoding, protocol=2), subtype=128)
        return binary_array
    else:
        return "error"

"""
Encodes the image passed into a numpy array used for facial recognition.
Not stored in database. Is used for encoding the login image.

Parameters:
    image(jpeg): Image to be encoded.

Returns:
    image_encoding(numpy array): Numpy array to be compared to registry numpy array.
"""
def encodeImageFaceRec(image):
    # Carries out the same task as the function above, but doesn't encode the array into base64
    # This is used when encoding the login image.
    image_file = face_recognition.load_image_file(image)
    encodings = face_recognition.face_encodings(image_file)

    if len(encodings) > 0:
        image_encoding = encodings[0]
        return image_encoding
    else:
        return "error"

"""
Decodes the registry image's numpy array from binary back to numpy.

Parameters:
    binary_array(base64 array): Array to be decoded.

Returns:
    image_encoding(numpy array): Numpy array to be used for face comparison.
"""
def decodeBinaryToNumpy(binary_array):
    # Decodes the binary array in the database to a numpy array, to be used for comparing login image to register image.
    image_encoding = pickle.loads(binary_array)

    return image_encoding

"""
Compares two numpy arrays to eachother, returns True if it's a match, or false if not.

Parameters:
    image_encoding1(numpy array): Login numpy array.
    image_encoding2(numpy array): Registered numpy array.

Returns:
    result(list): A list of booleans returned depending on how many comparisons are made.
"""
def compareImages(image_encoding1, image_encoding2):
    # Compares two numpy arrays to each other, returns a list of booleans
    # depending on how many images you compare to the reference image.
    result = face_recognition.compare_faces([image_encoding1], image_encoding2)

    return result
