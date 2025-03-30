from models import db  # Import db from the __init__.py file of the models directory
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
from pytz import utc

# Define the User model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

    chapters = db.relationship('Chapter', backref='subject', lazy=True)  # This sets up a one-to-many relationship

    def __repr__(self):
        return f'<Subject {self.name}>'

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Chapter {self.name}>'


class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    chapter = db.relationship('Chapter', backref=db.backref('quizzes', lazy=True))
    questions = db.relationship('Question', backref='quiz', lazy=True)

    def is_before_deadline(self):
        """Check if current time is before the quiz deadline"""
        return datetime.utcnow() < self.date_of_quiz
        
    def calculate_remaining_time(self):
        """Calculate seconds remaining until deadline"""
        return (self.date_of_quiz - datetime.utcnow()).total_seconds()

    def __repr__(self):
        return f'<Quiz {self.id}>'


# Define the Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_statement = db.Column(db.Text)
    option1 = db.Column(db.String(100))
    option2 = db.Column(db.String(100))
    option3 = db.Column(db.String(100))
    option4 = db.Column(db.String(100))
    correct_option = db.Column(db.Integer)

    def __repr__(self):
        return f'<Question {self.id}>'

# Define the Score model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_score = db.Column(db.Integer)

    def __repr__(self):
        return f'<Score {self.total_score}>'

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempt'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='quiz_attempts_user', lazy=True)  # Renamed backref here
    quiz = db.relationship('Quiz', backref='attempts', lazy=True)