from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models import User, db
from manage import app

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('user_dashboard'))
        flash("Invalid credentials!", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
