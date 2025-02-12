from flask import render_template, request, redirect, url_for, flash
from models import db, Subject, Chapter, Quiz, Question
from app import app

@app.route('/admin')
def admin_dashboard():
    subjects = Subject.query.all()
    return render_template('admin_dashboard.html', subjects=subjects)

@app.route('/add_subject', methods=['POST'])
def add_subject():
    name = request.form['name']
    new_subject = Subject(name=name)
    db.session.add(new_subject)
    db.session.commit()
    flash('Subject added successfully!')
    return redirect(url_for('admin_dashboard'))
