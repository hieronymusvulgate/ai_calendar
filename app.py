from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import nltk
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, timedelta
#pip install python-dotenv

nltk.download('punkt', quiet=True)

load_dotenv()

from blueprints.chatbot.chatbot import chatbot_bp
from blueprints.ai_calendar.ai_calendar import ai_calendar_bp
from blueprints.user_authentication.user_authentication import user_authentication_bp, init_app, db, User
from blueprints.forum.forum import forum_bp


app = Flask(__name__)

app.register_blueprint(user_authentication_bp)
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(ai_calendar_bp, url_prefix='/ai_calendar')
app.register_blueprint(forum_bp, url_prefix='/forum')

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

def demerit_pro_tokens():
    with app.app_context():
        current_date = date.today()
        users_to_update = User.query.filter(User.last_generated < (current_date - timedelta(days=3))).all()
        for user in users_to_update:
            user.pro_token = (user.pro_token // 4) * 3
            db.session.commit()
            print(f"Updated user {user.id}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(demerit_pro_tokens, 'interval', days=1)
    scheduler.start()

with app.app_context():
    db.create_all()
start_scheduler()

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     start_scheduler()
#     app.run(debug=True)