from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
# Secret key used for encrypting password.
app.config['SECRET_KEY'] ='3f1ab8d8edf5e53674d724badd29bf70'
# Password hashing for security.
bcrypt = Bcrypt(app)
#LoginManager provides user session management for Flask
login_manager = LoginManager(app)

from FrontEnd import routes