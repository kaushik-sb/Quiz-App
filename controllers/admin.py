from flask import render_template, request, redirect, url_for, flash
from models import db, Quiz, Chapter
from manage import app
from flask import current_app as app
from datetime import datetime

@app.route('/admin')
def admin_dashboard():
    quizzes = Quiz.query.all()
    return render_template('admin_dashboard.html', quizzes=quizzes)


@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d %H:%M')
        duration = int(request.form['duration'])

        new_quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, duration=duration)
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz added successfully with time scheduling!')
        return redirect(url_for('admin_dashboard'))
    
    chapters = Chapter.query.all()
    return render_template('add_quiz.html', chapters=chapters)
