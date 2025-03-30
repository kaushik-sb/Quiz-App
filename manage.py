from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager  # Import LoginManager
from models import db, User  # Import the db and User model


# Initialize the LoginManager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize Database and Migrations
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize LoginManager with the app
    login_manager.init_app(app)

    # Set the login view for when a user is not logged in
    login_manager.login_view = 'auth.login'  # This points to the login route in the 'auth' blueprint

    # Add the user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)

    # Import and register blueprints
    from controllers.auth import auth_bp
    from controllers.admin import admin_bp
    from controllers.user import user_bp
    from controllers.score import score_bp
    from controllers.search import search_bp
    from controllers.charts import charts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(score_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(charts_bp)

    # Home route
    @app.route('/')
    def home():
        return render_template("index.html")

    return app

# To run the app
if __name__ == "__main__":
    app = create_app()  # Create the app instance
    app.run(debug=True)