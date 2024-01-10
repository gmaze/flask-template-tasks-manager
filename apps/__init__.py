# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    from .apis import blueprint as api  # Cannot be imported before db.init_app
    app.register_blueprint(api, url_prefix='/api/1')

    for module_name in ('authentication', 'home', 'tasks', 'subscriptions', 'admin', 'monitors'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def start_monitors(app):
    from .monitors.src import SysTemMonitor
    SysTemMonitor(app=app, db=db, refresh_rate=app.config['REFRESH_MONITORS']).start()


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

        start_monitors(app)

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def insert_in_database(app):

    @app.before_first_request
    def insert_initial_values():
        """ Use this function to insert default or initial values in DB tables

        USERS ROLE:
        Admin: Users with this role have complete access rights, allowing them to manage all aspects of the application, such as adding new users, modifying settings, viewing and editing all content in the system.

        Supervisor: This role might be responsible for managing content created by other users, but may not have full administrative privileges like creating new accounts or changing global settings.

        User: This role might be able to create content and view their own content, but not view or modify content created by others.

        """
        try:
            from apps.authentication.models import UsersRole
            if UsersRole.query.count() == 0:
                db.session.add(UsersRole(label='Admin', level=100))
                db.session.add(UsersRole(label='Supervisor', level=50))
                db.session.add(UsersRole(label='User', level=0))
                db.session.commit()

            from apps.subscriptions.models import SubscriptionPlans
            if SubscriptionPlans.query.count() == 0:
                db.session.add(SubscriptionPlans(label='Gold', level=100, quota_tasks=100, quota_refresh=86400))
                # db.session.add(SubscriptionPlans(label='Silver', level=75, quota_tasks=500, quota_refresh=86400))
                db.session.add(SubscriptionPlans(label='Bronze', level=50, quota_tasks=50, quota_refresh=86400))
                db.session.add(SubscriptionPlans(label='Free', level=0, quota_tasks=10, quota_refresh=86400))
                db.session.commit()

            from apps.authentication.models import Users
            if Users.query.count() == 0:
                db.session.add(Users(username='admin',
                                     email='a@dm.in',
                                     password='pl',
                                     role_id=UsersRole.find_by_label(label='Admin').id))
                db.session.add(Users(username='pro',
                                     email='p@r.o',
                                     password='pl',
                                     plan_id=SubscriptionPlans.find_by_label(label='Gold').id))
                db.session.add(Users(username='student',
                                     email='st@ud.ent',
                                     password='pl'))
                db.session.commit()

        except Exception as e:
            print('> Error: DBMS Exception: ' + str(e))



def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    insert_in_database(app)
    return app
