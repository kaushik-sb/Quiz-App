from flask import render_template, request
from models import Subject, Quiz
from manage import app

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.id.ilike(f"%{query}%")).all()
    return render_template('search_results.html', subjects=subjects, quizzes=quizzes)
