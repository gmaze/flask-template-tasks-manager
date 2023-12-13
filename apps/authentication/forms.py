# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import Email, DataRequired



# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):

    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])

    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])

    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])

    plan_id = HiddenField('Subscription Plan',
                          id='subscription_plan',
                          validators=[DataRequired()])
