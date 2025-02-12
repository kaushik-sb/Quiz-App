from flask import render_template
from models import Score
from manage import app

@app.route('/charts')
def charts():
    scores = Score.query.all()
    return render_template('charts.html', scores=scores)
