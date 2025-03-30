from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Quiz, QuizAttempt, Question, Chapter, Subject, Score, User

user_bp = Blueprint('user', __name__)

@user_bp.route('/user_dashboard')
@login_required
def user_dashboard():
    # Fetch available quizzes that the user has not attempted yet
    available_quizzes = Quiz.query.all()
    past_attempts = current_user.quiz_attempts_user

    # Include additional information like subject and chapter for each quiz
    quizzes_details = []
    for quiz in available_quizzes:
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id) if chapter else None
        quizzes_details.append({
            'quiz': quiz,
            'chapter': chapter,
            'subject': subject
        })

    # Prepare data for subject-wise performance (only for existing subjects)
    subject_performance = {}
    current_subjects = {subject.id: subject.name for subject in Subject.query.all()}
    
    for attempt in past_attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        if quiz and quiz.chapter and quiz.chapter.subject:
            # Only include subjects that still exist
            if quiz.chapter.subject.id in current_subjects:
                subject_name = quiz.chapter.subject.name
                # Calculate percentage score
                percentage_score = (attempt.score / len(quiz.questions)) * 100 if len(quiz.questions) > 0 else 0

                if subject_name not in subject_performance:
                    subject_performance[subject_name] = []

                subject_performance[subject_name].append(percentage_score)

    # Calculate average percentage score for each subject
    average_scores = {subject: sum(scores)/len(scores) for subject, scores in subject_performance.items()}

    # Convert subject_performance to lists (for chart rendering)
    subject_labels = list(subject_performance.keys())
    subject_avg_scores = [sum(scores)/len(scores) for scores in subject_performance.values()]

    return render_template(
        'user_dashboard.html', 
        quizzes_details=quizzes_details, 
        past_attempts=past_attempts,
        subject_performance=average_scores,
        subject_labels=subject_labels,
        subject_avg_scores=subject_avg_scores
    )

@user_bp.route('/view_quiz_result/<int:attempt_id>', methods=['GET'])
@login_required
def view_quiz_result(attempt_id):
    # Fetch the quiz attempt based on attempt_id
    quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
    quiz = Quiz.query.get(quiz_attempt.quiz_id)
    score = quiz_attempt.score
    attempt_date = quiz_attempt.attempt_date

    return render_template('view_quiz_result.html', 
                           quiz=quiz, 
                           score=score, 
                           attempt_date=attempt_date)


@user_bp.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if deadline has passed
    if not quiz.is_before_deadline():
        flash('The deadline for this quiz has passed', 'danger')
        return redirect(url_for('user.user_dashboard'))
    
    if request.method == 'POST':
        # Process quiz submission
        score = 0
        for question in quiz.questions:
            answer = request.form.get(f'question_{question.id}')
            if answer and int(answer) == question.correct_option:
                score += 1
        
        # Record attempt
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz.id,
            score=score
        )
        db.session.add(attempt)
        db.session.commit()
        
        flash(f'Quiz submitted! Your score: {score}/{len(quiz.questions)}', 'success')
        return redirect(url_for('user.user_dashboard'))
    
    # Calculate remaining time for the timer
    remaining_time = quiz.calculate_remaining_time()
    
    return render_template(
        'attempt_quiz.html', 
        quiz=quiz,
        remaining_time=remaining_time
    )