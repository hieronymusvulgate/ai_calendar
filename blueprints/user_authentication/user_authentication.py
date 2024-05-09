from flask import Blueprint, request, session, render_template, redirect, url_for, current_app, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import secrets
import string
import random
from datetime import datetime, timezone, timedelta
import json
from datetime import date
from functools import wraps
#pip install flask flask_sqlalchemy flask_login flask_bcrypt flask_wtf wtforms email_validator

# Email reset


user_authentication_bp = Blueprint('user_authentication', __name__, template_folder='templates')

db = SQLAlchemy()

bcrypt = Bcrypt()

login_manager = LoginManager()

mail = Mail()


def init_app(app):
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'user_authentication.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_otp():
    characters = string.ascii_letters + string.digits + string.punctuation
    length = random.randint(6, 10)
    return ''.join(secrets.choice(characters) for _ in range(length))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    pro_token = db.Column(db.Float, default=0, nullable=False)
    optimizer = db.Column(db.Integer, default=4, nullable=True)
    last_generated = db.Column(db.Date, default=date(1999, 1, 1), nullable=True)
    tokens_earned_today = db.Column(db.Float, default=0, nullable=False)
    subjects = db.relationship('Subject', backref='user', lazy=True)
    freetime = db.relationship('Freetime', backref='user', lazy=True)
    assignments = db.relationship('Assignments', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

class Freetime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    freetime = db.Column(db.String(100), nullable=False)

class Assignments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_slot = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

# Forum start
# class ForumPost(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String, nullable=False)
#     description = db.Column(db.String)

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String, nullable=False)    
#     forum_post_id = db.Column(db.String)
# Forum End

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = StringField(validators=[
                           InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError('That email already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('Username does not exist.')

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError('Password is incorrect.')

@user_authentication_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('user_authentication.dashboard'))
    return render_template('login.html', form=form)


@user_authentication_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    with open('static/json/motivational_quotes.json', 'r') as file:
        quotes = json.load(file)
        random_quote = random.choice(quotes['quotes'])
    username = current_user.username
    current_hour = datetime.now(timezone(timedelta(hours=8))).hour
    if 5 <= current_hour < 12:
        time_of_day = "☀️Good Morning "
    elif 12 <= current_hour < 18:
        time_of_day = "🌞Good Afternoon "
    else:
        time_of_day = "🌙Good Evening "
    users = User.query.order_by(User.pro_token.desc()).all()
    return render_template('dashboard.html', time_of_day=time_of_day, username=username, users=users, quote=random_quote, enumerate=enumerate)


@user_authentication_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_authentication.login'))


@user_authentication_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data, rounds=12).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_authentication.login'))
    return render_template('register.html', form=form)

@user_authentication_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            otp = generate_otp()
            session['reset_email'] = email
            session['otp'] = otp
            msg = Message('Password Reset OTP', sender='orcinusbiz@gmail.com', recipients=[email])
            msg.body = f"Your OTP for password reset is: {otp}"
            mail.send(msg)
            flash('An OTP has been sent to your email address.', 'success')
            return redirect(url_for('user_authentication.verify_otp'))
        else:
            flash('Invalid email address.', 'error')
    return render_template('forgot_password.html')

@user_authentication_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session or 'otp' not in session:
        return redirect(url_for('user_authentication.forgot_password'))

    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session['otp']:
            return redirect(url_for('user_authentication.reset_password'))
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify_otp.html')

@user_authentication_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        return redirect(url_for('user_authentication.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        user = User.query.filter_by(email=session['reset_email']).first()
        if user:
            hashed_password = bcrypt.generate_password_hash(new_password, rounds=12).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been reset successfully.', 'success')
            session.pop('reset_email')
            session.pop('otp')
            return redirect(url_for('user_authentication.login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('user_authentication.login'))

    return render_template('reset_password.html')

def token_required_forum(min_pro_token):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                if current_user.pro_token >= min_pro_token:
                    return f(*args, **kwargs)
                else:
                    flash('Minimum tokens required is 24, you have insufficient tokens.')
                    return redirect(url_for('user_authentication.dashboard'))
            else:
                flash('Please login to access this page.')
                return redirect(url_for('user_authentication.login'))
        return decorated_function
    return decorator

