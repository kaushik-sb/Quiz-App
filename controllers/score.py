from flask import Blueprint, render_template
from models import db, Score

# Create a Blueprint for score routes
score_bp = Blueprint('score', __name__)

@score_bp.route('/quiz_results')
def quiz_results():
    scores = Score.query.all() or []
    return render_template("quiz_results.html", scores=scores)
