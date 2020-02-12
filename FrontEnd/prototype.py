from flask import Flask, escape, request, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] ='3f1ab8d8edf5e53674d724badd29bf70'

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

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'mark@gmail.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
           flash('Login Unsuccessful. Please check username and password', 'danger') 
    return render_template('login.html', title='Logim', form=form)

if __name__ == '__main__':
    app.run(debug=True) 