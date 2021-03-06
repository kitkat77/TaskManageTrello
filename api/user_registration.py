from flask import Blueprint, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, BooleanField
from wtforms.fields.html5 import DateField
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms.validators import Email, EqualTo, Length, Required, InputRequired
from models import db, User


user_blueprint = Blueprint('user_blueprint', __name__)


# class RegisterForm(FlaskForm):
#     username = StringField('Username', validators=[
#                            InputRequired(), Length(max=32)])
#     password = PasswordField('Password', validators=[
#                              Required(), EqualTo('confirm', message='Passwords must match')])
#     confirm = PasswordField('Retype Password', validators=[
#                             Required(), Length(min=8, max=80)])
#     dob = DateField('Date Of Birth', validators=[InputRequired()])
#     email = StringField('Email', validators=[InputRequired(), Email()])
#     name = StringField('Name', validators=[InputRequired(), Length(max=64)])
#
#
# class LoginForm(FlaskForm):
#     username = StringField('username', validators=[
#                            InputRequired(), Length(max=20)])
#     password = PasswordField('password', validators=[
#                              InputRequired(), Length(min=8, max=40)])
#     remember = BooleanField('Remember Me')
#
#
# @user_blueprint.route('/user/registration', methods=['POST', 'GET'])
# def register_user():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         hashed_password = generate_password_hash(form.password.data, method = 'sha256')
#         new_user = User(username=form.username.data, name=form.name.data, dob=form.dob.data, password_hash=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect("/"+new_user.username+"/home")
#     return render_template('register.html', form=form)
#
# @user_blueprint.route('/user/login', methods = ['POST', 'GET'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         print('validated')
#         user = User.query.filter_by(username = form.username.data).first()
#         print(user)
#         if user:
#             if check_password_hash(user.password_hash,form.password.data):
#                 login_user(user, remember=form.remember.data)
#                 return redirect('/dashboard')
#         return '<h1>Invalid Username/Password</h1>'
#     return render_template('login.html',form=form)
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=32)])
    password = PasswordField('Password', validators=[Required(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Retype Password', validators=[Required(),Length(min=8, max=80)])
    dob = DateField('Date Of Birth', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    name = StringField('Name', validators=[InputRequired(), Length(max=64)])

@user_blueprint.route('/user/registration', methods = ['POST', 'GET'])
def register_user():

    if current_user.is_authenticated:
        return redirect("/"+current_user.username+"/home")

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method = 'sha256')
        new_user = User(username=form.username.data, name=form.name.data, dob=form.dob.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/"+new_user.username+"/home")
    return render_template('register.html',form=form)


class LoginForm(FlaskForm):
    username = StringField('username',validators=[InputRequired(), Length(max=20)])
    password = PasswordField('password',validators=[InputRequired()])
    remember = BooleanField('Remember Me')

@user_blueprint.route('/user/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect("/"+current_user.username+"/home")
    form = LoginForm()
    if form.validate_on_submit():
        print('validated')
        user = User.query.filter_by(username = form.username.data).first()
        print(user)
        if user:
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect("/"+user.username+"/home")
        flash('Invalid username or password')
        return render_template('login.html',form=form)
    return render_template('login.html',form=form)

@user_blueprint.route('/dashboard')
@login_required
def dashboard():
    return '<h1>you are registered</h1>'

@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('index.html')
