import os
from flask import flash, request, redirect
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '../API/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file():
    # Check if request has post method.
    if request.method == 'POST':
        # Check if the post request contains the image file.
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        image = request.files['image']
        # If user doesn't select a file, output error message and return to the request URL.
        if image.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # Check if there's an image and it has an allowed extension, then save the image to the upload folder.
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))