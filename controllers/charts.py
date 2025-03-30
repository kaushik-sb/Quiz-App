from flask import Blueprint, render_template
from models import Score

# Create a Blueprint for charts routes
charts_bp = Blueprint('charts', __name__)

@charts_bp.route('/charts')
def charts():
    scores = Score.query.all() or []
    return render_template("charts.html", scores=scores)
