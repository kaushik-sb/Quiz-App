from flask import render_template
from models import db, Score, Quiz, User
from manage import app

@app.route('/quiz_results')
def quiz_results():
    scores = Score.query.all()
    return render_template('quiz_results.html', scores=scores)
