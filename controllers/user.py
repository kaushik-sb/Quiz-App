from flask import render_template, request, redirect, url_for, flash
from models import db, User, Quiz, Score, Question
from manage import app

@app.route('/user_dashboard')
def user_dashboard():
    quizzes = Quiz.query.all()
    return render_template('user_dashboard.html', quizzes=quizzes)

@app.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += 1
        new_score = Score(quiz_id=quiz_id, user_id=1, total_score=score)  # Replace 1 with actual user ID
        db.session.add(new_score)
        db.session.commit()
        flash(f'Quiz completed! Your Score: {score}/{len(questions)}')
        return redirect(url_for('user_dashboard'))
    return render_template('quiz_attempt.html', quiz=quiz, questions=questions)
