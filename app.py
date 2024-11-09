from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import AddQuestionForm, EvaluateForm, LoginForm, SignupForm
from models import db, Question, Answer, User
from string_similarity import evaluate_answer
import random
from models import UserResponse, User, Question, Answer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Signup successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash('User already exists.', 'danger')
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('add_question'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def add_question():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if session.get('username') != 'admin':
        return redirect(url_for('mock_form'))
    form = AddQuestionForm()
    if form.validate_on_submit():
        question = Question(question_text=form.question.data)
        db.session.add(question)
        db.session.commit()
        answer = Answer(question_id=question.id, answer_text=form.ideal_answer.data)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('add_question'))
    return render_template('add.html', form=form)

@app.route('/mock_form', methods=['GET', 'POST'])
def mock_form():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Fetch all questions and sample 3 random ones
    questions = Question.query.all()
    selected_questions = random.sample(questions, min(3, len(questions)))

    if request.method == 'POST':
        user_answers = []
        results = []

        # Retrieve answers using question IDs in the POST data
        for question in selected_questions:
            user_answer = request.form.get(f'answers_{question.id}', '')  # Get the answer for the question
            ideal_answer = Answer.query.filter_by(question_id=question.id).first().answer_text

            # Evaluate the answer
            final_score, keyword_score, semantic_score = evaluate_answer(ideal_answer, user_answer)
            results.append({
                'question': question.question_text,
                'user_answer': user_answer,
                'final_score': final_score,
                'keyword_score': keyword_score,
                'semantic_score': semantic_score
            })

        return render_template('mock_results.html', results=results)

    return render_template('mock_form.html', questions=selected_questions)


@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if session.get('username') != 'admin':
        return redirect(url_for('mock_form'))
    form = EvaluateForm()
    questions = Question.query.all()
    return render_template('evaluate.html', form=form, questions=questions)

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    data = request.json
    question_id = data.get('question_id')
    user_answer = data.get('user_answer')

    answer = Answer.query.filter_by(question_id=question_id).first()
    if not answer:
        return jsonify({'error': 'Question not found'}), 404

    ideal_answer = answer.answer_text
    final_score, keyword_score, semantic_score = evaluate_answer(ideal_answer, user_answer)

    return jsonify({
        'final_score': final_score,
        'keyword_score': keyword_score,
        'semantic_score': semantic_score
    })

@app.route('/questions', methods=['GET'])
def view_questions():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if session.get('username') != 'admin':
        return redirect(url_for('mock_form'))
    questions = Question.query.all()
    answers = Answer.query.all()
    return render_template('questions.html', questions=questions, answers=answers)

@app.route('/view_results')
def view_results():
    # Query the User and UserResponse tables
    results = db.session.query(User.username, UserResponse.final_score, UserResponse.keyword_score, UserResponse.semantic_score).join(UserResponse, User.id == UserResponse.user_id).all()
    
    # Check if there are no results and set an empty list if none are found
    if not results:
        results = []  # Set an empty list if no results are found

    return render_template('view_results.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
