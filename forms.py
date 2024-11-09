from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class AddQuestionForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    ideal_answer = TextAreaField('Ideal Answer', validators=[DataRequired()])
    submit = SubmitField('Add Question and Answer')

class EvaluateForm(FlaskForm):
    user_answer = TextAreaField('Your Answer', validators=[DataRequired()])
    ideal_answer = TextAreaField('Ideal Answer', validators=[DataRequired()])
    submit = SubmitField('Evaluate')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class UserNameForm(FlaskForm):
    user_name = StringField('Your Name', validators=[DataRequired()])
    submit = SubmitField('Start Test')

class TestForm(FlaskForm):
    user_name = StringField('Your Name', validators=[DataRequired()])
    answers = TextAreaField('Answers', validators=[DataRequired()])  # This will hold answers to 5 questions
    submit = SubmitField('Submit Test')
