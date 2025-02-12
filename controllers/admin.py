from flask import render_template, request, redirect, url_for, flash
from models import db, Subject, Chapter, Quiz, Question
from manage import app

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

@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully!')
    return redirect(url_for('admin_dashboard'))
