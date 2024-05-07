from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import nltk
#pip install python-dotenv

nltk.download('punkt', quiet=True)

load_dotenv()

from blueprints.chatbot.chatbot import chatbot_bp
from blueprints.ai_calendar.ai_calendar import ai_calendar_bp
from blueprints.user_authentication.user_authentication import user_authentication_bp, init_app, db


app = Flask(__name__)

app.register_blueprint(user_authentication_bp)
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(ai_calendar_bp, url_prefix='/ai_calendar')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)