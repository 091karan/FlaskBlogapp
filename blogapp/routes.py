
import os
import secrets
from PIL import Image
from blogapp.forms import RegistrationForm, LoginForm, UserAccountForm
from flask import render_template, url_for, flash, redirect,request
from blogapp import app,db,bcrypt
from blogapp.models import User, Post
from flask_login import login_user,current_user,logout_user,login_required

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been successfully created! You are now able to Log In.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(picture.filename)
    f_name = random_hex + f_ext

    saving_path = os.path.join(app.root_path, 'static/profile_pics',f_name)

    output_size = (125,125)
    i=Image.open(picture)
    i.thumbnail(output_size)
    i.save(saving_path)

    return f_name


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UserAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            f_name = save_picture(form.picture.data)
            current_user.image_file=f_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Account',image_file = image_file,
                            form=form)
