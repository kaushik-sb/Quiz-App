from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime


auth_bp = Blueprint('auth', __name__)

# Hardcoded admin credentials (no hashing)
ADMIN_USERNAME = 'admin@example.com'
ADMIN_PASSWORD = 'adminpassword'

@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch the admin user from the database
        admin_user = User.query.filter_by(username=ADMIN_USERNAME).first()

        if admin_user and admin_user.password == password:  # Compare password directly (no hashing)
            login_user(admin_user)  # Log the user in
            return redirect(url_for('admin.admin_dashboard'))  # Redirect to Admin Dashboard
        else:
            flash("Invalid Admin credentials. Please try again.", "danger")
            return redirect(url_for('auth.admin_login'))  # Stay on login page if credentials are wrong

    return render_template('admin_login.html')


# User Registration Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']  # Email as username
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob_str = request.form['dob']  # Date as string from the form

        # Convert dob (date of birth) to datetime.date object
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()  # Convert string to date
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('auth.register'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Email already exists.", "danger")
            return redirect(url_for('auth.register'))

        # Create new user
        new_user = User(username=username, password=hashed_password, full_name=full_name, 
                        qualification=qualification, dob=dob)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('auth.login'))  # Redirect to login page after registration

    return render_template('register.html')

# User Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find user by username
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('user.user_dashboard'))  # Redirect to user dashboard on login
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  # Logs out the user
    return redirect(url_for('auth.login'))  # Redirect to the login page
