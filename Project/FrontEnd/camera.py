import cv2 as cv
import os
from time import localtime, strftime
global timestamp


class Camera(object):
    """
    This is a class for managing the camera backend functions.
    """

    CAPTURES_DIR = "./Frontend/static/captures/"
    RESIZE_RATIO = 1.0

    def __init__(self):
        """
        A constructor for the Camera class, starts video capturing.
        """
        self.video = cv.VideoCapture(0)

    def __del__(self):
        """
        A constructor for the Camera class, stops video capturing.
        """
        self.video.release()

    def get_frame(self):
        """
        Gets the current frame and resizes it to the camera resize ratio.

        :returns The current frame.
        """
        success, frame = self.video.read()
        if not success:
            return None

        if Camera.RESIZE_RATIO != 1:
            frame = cv.resize(frame, None, fx=Camera.RESIZE_RATIO, fy=Camera.RESIZE_RATIO)
        return frame

    def get_feed(self):
        """
        Gets the current frame and encodes it to jpeg, then converts the image to bytes.

        :returns The current frame encoding.
        """
        frame = self.get_frame()
        if frame is not None:
            ret, jpeg = cv.imencode('.jpg', frame)
            return jpeg.tobytes()

    def capture(self):
        """
        Gets the current frame, creates a timestamp and saves the image
        to the static folder as a jpg.

        :returns The timestamp the image is named as.
        """
        global timestamp
        frame = self.get_frame()
        timestamp = strftime("%d-%m-%Y-%Hh%Mm%Ss", localtime())
        filename = Camera.CAPTURES_DIR + timestamp + ".jpg"

        if not cv.imwrite(filename, frame):
            raise RuntimeError("Unable to capture image " + timestamp)
        return timestamp


def remove_pic():
    """
    Removes the image from the directory after the program is finished with it.
    """
    global timestamp
    filename = Camera.CAPTURES_DIR + timestamp + ".jpg"
    os.remove(filename)
