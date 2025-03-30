from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Initialize LoginManager
login_manager = LoginManager()

# Import models here so they are available for the app
from models.models import User, Subject, Chapter, Quiz, Question, Score, QuizAttempt


# Function to load the user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
