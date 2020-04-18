from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES
from werkzeug.utils import secure_filename

images = UploadSet('images', IMAGES)


class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    firstName = StringField('First name', 
                        validators=[DataRequired()])
    secondName = StringField('Second name', 
                    validators=[DataRequired()])
    address = StringField('Address', 
                validators=[DataRequired()])
    MobileNum = StringField('Mobile Number', 
            validators=[DataRequired()])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                            validators=[DataRequired(), EqualTo('password')])
    image = FileField('Image',validators=[FileRequired(),
                                FileAllowed(images, 'Images only!')])
    submit = SubmitField('Sign up')


class searchForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])


class LoginForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')     
