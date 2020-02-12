import sys
import cv2
import numpy as np


# Get user supplied values
#imagePath = sys.argv[1]
cascPath = sys.argv[1]

cap = cv2.VideoCapture(0)

while(True):
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)

    ret, frame = cap.read()
    # Read the image
    #image = cv2.imread(imagePath)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=7,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    print("Found {0} faces!".format(len(faces)))

    # Draw a rectangle around the faces
    for(x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Found face!", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()