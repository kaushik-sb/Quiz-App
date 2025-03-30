from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, Subject, Chapter, Quiz, Question, User, Score, QuizAttempt
from forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
from flask_wtf import FlaskForm  # Import FlaskForm
from wtforms.validators import DataRequired  # Validator
from wtforms import StringField, IntegerField, TextAreaField
from datetime import datetime
from wtforms.fields import DateTimeField
from forms import QuestionForm  # assuming you have a QuestionForm

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    # Existing code (keep all existing functionality)
    search_query = request.args.get('search', '')
    users_query = User.query.order_by(User.id)
    if search_query:
        users_query = users_query.filter(
            User.username.ilike(f'%{search_query}%') |
            User.full_name.ilike(f'%{search_query}%') |
            User.qualification.ilike(f'%{search_query}%')
        )
    subjects = Subject.query.all()
    users = users_query.all()

    # NEW: Performance analysis data for charts (excluding admin@example.com)
    ADMIN_USERNAME = 'admin@example.com'
    
    # User-wise performance data (excluding admin)
    user_labels = []
    user_scores = []
    for user in users:
        if user.username == ADMIN_USERNAME:
            continue  # Skip admin user
            
        attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
        if attempts:
            total_score = sum(attempt.score for attempt in attempts)
            total_possible = sum(len(attempt.quiz.questions) for attempt in attempts if attempt.quiz)
            avg_score = (total_score / total_possible * 100) if total_possible else 0
            user_labels.append(user.full_name or user.username)
            user_scores.append(round(avg_score, 1))

    # Subject-wise performance data (excluding admin attempts)
    subject_labels = []
    subject_scores = []
    for subject in subjects:
        quizzes = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject.id).all()
        quiz_ids = [quiz.id for quiz in quizzes]
        
        # Get attempts excluding those from admin user
        attempts = QuizAttempt.query.filter(
            QuizAttempt.quiz_id.in_(quiz_ids),
            QuizAttempt.user_id != User.query.filter_by(username=ADMIN_USERNAME).first().id
        ).all()
        
        if attempts:
            total_score = sum(attempt.score for attempt in attempts)
            total_possible = sum(len(attempt.quiz.questions) for attempt in attempts if attempt.quiz)
            avg_score = (total_score / total_possible * 100) if total_possible else 0
            subject_labels.append(subject.name)
            subject_scores.append(round(avg_score, 1))

    return render_template('admin_dashboard.html', 
                         subjects=subjects, 
                         users=users,
                         search_query=search_query,
                         user_labels=user_labels,
                         user_scores=user_scores,
                         subject_labels=subject_labels,
                         subject_scores=subject_scores)

# Add New Subject
@admin_bp.route('/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    form = SubjectForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('add_subject.html', form=form)


# Edit Subject
@admin_bp.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('edit_subject.html', form=form, subject=subject)


# Delete Subject
@admin_bp.route('/delete_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully!', 'success')

    return redirect(url_for('admin.admin_dashboard'))


# Admin Dashboard to view all subjects
@admin_bp.route('/view_subjects', methods=['GET'])
@login_required
def view_subjects():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))  # Redirect if not admin

    subjects = Subject.query.all()  # Get all subjects from the database
    return render_template('view_subjects.html', subjects=subjects)


# View a specific subject and its chapters
@admin_bp.route('/view_subject/<int:subject_id>', methods=['GET'])
@login_required
def view_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))  # Redirect if not admin

    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()  # Get all chapters for this subject
    return render_template('view_subject.html', subject=subject, chapters=chapters)



@admin_bp.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def add_chapter(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))  # Redirect if not admin

    subject = Subject.query.get_or_404(subject_id)
    form = ChapterForm()  # Create the form object

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('admin.view_subject', subject_id=subject_id))  # Redirect after chapter is added

    return render_template('add_chapter.html', form=form, subject=subject)  # Pass form to the template

# View a Chapter and Add Quiz
@admin_bp.route('/view_chapter/<int:id>', methods=['GET', 'POST'])
@login_required
def view_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()

    # Handle Quiz Creation
    if request.method == 'POST':
        # Print the form data for debugging
        print("Form data received:", request.form)

        # Ensure 'duration' key exists in the form
        if 'duration' not in request.form:
            print("Duration is missing from the form")

        date_of_quiz = request.form.get('date_of_quiz')
        duration = request.form.get('duration')

        if not date_of_quiz or not duration:
            flash('Please fill all fields correctly.', 'danger')
            return redirect(url_for('admin.view_chapter', id=chapter.id))

        # Convert the date and create the quiz
        try:
            date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format. Please use the correct format.', 'danger')
            return redirect(url_for('admin.view_chapter', id=chapter.id))

        new_quiz = Quiz(
            chapter_id=chapter.id,
            date_of_quiz=date_of_quiz,
            duration=duration
        )

        try:
            # Add to the session and commit the transaction
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
        except Exception as e:
            # Handle any exceptions during the commit
            flash(f'Error adding quiz: {str(e)}', 'danger')
            db.session.rollback()  # Rollback any changes if there is an error

        return redirect(url_for('admin.view_chapter', id=chapter.id))

    return render_template('view_chapter.html', chapter=chapter, quizzes=quizzes)


# Edit Chapter
@admin_bp.route('/edit_chapter/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    chapter = Chapter.query.get_or_404(id)
    form = ChapterForm(obj=chapter)

    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.view_subject', id=chapter.subject_id))

    return render_template('edit_chapter.html', form=form, chapter=chapter)


@admin_bp.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('auth.login'))

    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    
    try:
        # Delete all questions in all quizzes of this chapter
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        for quiz in quizzes:
            Question.query.filter_by(quiz_id=quiz.id).delete()
        
        # Delete all quizzes in this chapter
        Quiz.query.filter_by(chapter_id=chapter_id).delete()
        
        # Finally delete the chapter
        db.session.delete(chapter)
        db.session.commit()
        
        flash('Chapter and all associated content deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting chapter: {str(e)}', 'danger')
    
    return redirect(url_for('admin.view_subject', subject_id=subject_id))

class QuizForm(FlaskForm):
    name = StringField('Quiz Name', validators=[DataRequired()])
    date_of_quiz = StringField('Date of Quiz (YYYY-MM-DD)', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired()])

# Add New Quiz under Chapter
@admin_bp.route('/add_quiz/<int:chapter_id>', methods=['GET', 'POST'])
def add_quiz(chapter_id):
    # Fetch the chapter using the chapter_id
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        # Capture the form data
        date_of_quiz = request.form.get('date_of_quiz')
        duration = request.form.get('duration')

        # Check if the data is coming through correctly
        print(f"Received data: date_of_quiz={date_of_quiz}, duration={duration}")

        # Handle the case where the form fields might be empty or missing
        if not date_of_quiz or not duration:
            flash('Please fill all fields correctly.', 'danger')
            return redirect(url_for('admin.add_quiz', chapter_id=chapter_id))  # Stay on the form page if data is missing

        # Convert the string to a datetime object
        try:
            date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format. Please use the correct format.', 'danger')
            return redirect(url_for('admin.add_quiz', chapter_id=chapter_id))

        # Create the quiz
        new_quiz = Quiz(
            chapter_id=chapter.id,
            date_of_quiz=date_of_quiz,
            duration=duration
        )

        try:
            # Add to the session and commit the transaction
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
        except Exception as e:
            # Handle any exceptions during the commit
            flash(f'Error adding quiz: {str(e)}', 'danger')
            db.session.rollback()  # Rollback any changes if there is an error

        # Redirect to the view chapter page
        return redirect(url_for('admin.view_chapter', id=chapter.id))

    return render_template('add_quiz.html', chapter=chapter)


# This should match the URL pattern used in your route.
@admin_bp.route('/view_quiz/<int:quiz_id>', methods=['GET'])
@login_required
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('view_quiz.html', quiz=quiz, questions=questions)


# Add Question to a Quiz
class QuestionForm(FlaskForm):
    question_statement = TextAreaField('Question Statement', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct_option = IntegerField('Correct Option (1-4)', validators=[DataRequired()])

# Add question route
@admin_bp.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))  # Ensure only admins can add questions

    quiz = Quiz.query.get_or_404(quiz_id)  # Get the quiz to which the question will be added

    if request.method == 'POST':
        # Get form data
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']

        # Create a new question and add it to the database
        new_question = Question(
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            quiz_id=quiz_id  # Make sure this is linked to the correct quiz
        )
        db.session.add(new_question)
        db.session.commit()

        # Redirect back to the quiz page after saving the question
        return redirect(url_for('admin.view_quiz', quiz_id=quiz_id))

    return render_template('add_question.html', quiz=quiz)



# Search for subjects, quizzes, and users
@admin_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    subjects = None
    quizzes = None
    users = None

    if request.method == 'POST':
        search_term = request.form['search_term']
        subjects = Subject.query.filter(Subject.name.contains(search_term)).all()
        quizzes = Quiz.query.filter(Quiz.name.contains(search_term)).all()
        users = User.query.filter(User.username.contains(search_term)).all()

    return render_template('search_results.html', subjects=subjects, quizzes=quizzes, users=users)

# Define the form to edit a quiz
class EditQuizForm(FlaskForm):
    date_of_quiz = DateTimeField('Date of Quiz', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired()])

# Edit Quiz Route
@admin_bp.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))  # Ensure only admins can edit quizzes

    quiz = Quiz.query.get_or_404(quiz_id)
    form = EditQuizForm(obj=quiz)  # Bind the form with quiz data

    if form.validate_on_submit():
        # Update quiz with form data
        quiz.date_of_quiz = form.date_of_quiz.data
        quiz.duration = form.duration.data
        db.session.commit()  # Save changes to the quiz
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin.view_quiz', quiz_id=quiz_id))  # Redirect back to the quiz view

    return render_template('edit_quiz.html', form=form, quiz=quiz)  # Pass form and quiz to the template




# Delete Quiz
@admin_bp.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    quiz = Quiz.query.get_or_404(quiz_id)
    chapter_id = quiz.chapter_id
    
    # First delete all questions in this quiz
    Question.query.filter_by(quiz_id=quiz_id).delete()
    
    # Now delete the quiz
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz and all associated questions deleted successfully!', 'success')
    return redirect(url_for('admin.view_chapter', id=chapter_id))


# Edit Question
@admin_bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))  # Ensure only admins can edit questions

    # Retrieve the question to be edited
    question = Question.query.get_or_404(question_id)
    
    # Create a form instance with the request data
    form = QuestionForm(request.form)

    # On form submission, process the POST data
    if form.validate_on_submit():
        # Update the question with new data from the form
        question.question_statement = form.question_statement.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = form.correct_option.data

        # Commit the changes to the database
        db.session.commit()

        # Flash a success message and redirect back to the quiz view
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.view_quiz', quiz_id=question.quiz_id))  # Redirect to the quiz view

    # If GET request or form not validated, pre-populate the form fields
    if request.method == 'GET':
        form.question_statement.data = question.question_statement
        form.option1.data = question.option1
        form.option2.data = question.option2
        form.option3.data = question.option3
        form.option4.data = question.option4
        form.correct_option.data = question.correct_option

    # Render the template and pass the form
    return render_template('edit_question.html', form=form, question=question)

# Delete Question
@admin_bp.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    # Delete the question
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.view_quiz', quiz_id=quiz_id))