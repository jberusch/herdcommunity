from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SignupForm(FlaskForm):
    username = StringField('Username (no spaces)', validators=[DataRequired()])
    name = StringField('First and Last Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SearchForm(FlaskForm):
    # dq for destination query
    dq = StringField('Search Destinations', validators=[DataRequired()])