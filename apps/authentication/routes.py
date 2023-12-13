# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, jsonify
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from apps.subscriptions.models import SubscriptionPlans

from apps.authentication.util import verify_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

def ValidateUsername(field):
    if Users.find_by_username(field.data) is not None:
        return ("Username '%s' already registered" % field.data),
    else:
        return None

def ValidateEmail(field):
    print('ValidateEmail data:', field.data)
    if Users.find_by_email(field.data) is not None:
        return ("An account with this email '%s' is already registered" % field.data),
    else:
        return None

def ValidatePlanId(field):
    print('ValidatePlanId data:', field.data)
    if SubscriptionPlans.find_by_id(field.data) is None:
        return ("Invalid Subscription Plan '%s'" % str(field.data)),
    else:
        return None

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user, remember=True)
            # print(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():

    list_plans = SubscriptionPlans.query.order_by(SubscriptionPlans.level).all()
    list_plans = [p.to_dict() for p in list_plans]

    if 'register' in request.form:
        this_form = CreateAccountForm(request.form)

        errors = []
        if ValidateEmail(this_form.email) is not None:
            errors += ValidateEmail(this_form.email)
        if ValidateUsername(this_form.username) is not None:
            errors += ValidateUsername(this_form.username)
        if ValidatePlanId(this_form.plan_id) is not None:
            errors += ValidatePlanId(this_form.plan_id)
        if len(errors) > 0:
            return render_template('accounts/register.html',
                                   success=False, errors=errors,
                                   form=this_form, list_plans=list_plans)

        # Else we can create the user:
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()
        
        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=CreateAccountForm(), plans=None)

        # Automatically Login user and redirect to the default landing page:
        # user = Users.query.filter_by(username=username).first()
        # login_user(user, remember=True)
        # return redirect(url_for('authentication_blueprint.route_default'))

    else:
        this_form = CreateAccountForm()
        return render_template('accounts/register.html', form=this_form, list_plans=list_plans)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
