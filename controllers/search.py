from flask import Blueprint, render_template, request
from models import Quiz, Subject

# Create a Blueprint for search routes
search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.id.ilike(f"%{query}%")).all()
    return render_template("search_results.html", subjects=subjects, quizzes=quizzes)
