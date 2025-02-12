from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db

# Initialize Flask App
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create the application context before importing controllers
with app.app_context():
    import controllers.admin
    import controllers.auth
    import controllers.user
    import controllers.score
    import controllers.search
    import controllers.charts

# Define Home Route
@app.route('/')
def home():
    return "Welcome to Quiz Master App!"

if __name__ == "__main__":
    app.run(debug=True)
