# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import date, datetime
import uuid

from apps import db, login_manager
from apps.authentication.util import hash_pass


class TimestampMixin:
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Users(db.Model, UserMixin, TimestampMixin):

    __tablename__ = 'Users_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)

    tasks: Mapped[List["Tasks"]] = relationship(back_populates="user")
    apikey = db.Column(db.String(80))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack its value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

        self.apikey = uuid.uuid4().hex

    def __repr__(self):
        summary = ["<Users.%i>" % self.id]
        summary.append("Created: %s" % self.created)
        summary.append("Last update: %s" % self.updated)
        summary.append("Username: %s" % self.username)
        summary.append("Email: %s" % self.email)
        summary.append("API key: %s" % self.apikey)
        summary.append("Tasks ID: %s" % (",".join([str(t.id) for t in self.tasks])))
        return "\n".join(summary)

    @classmethod
    def find_by_api_key(self, apikey):
        return self.query.filter_by(apikey=apikey).first()

    @classmethod
    def find_by_id(self, id):
        return self.query.filter_by(id=id).first()

    def to_dict(self):
        params = {}
        for k in ['id', 'created', 'updated', 'username', 'email', 'apikey']:
            params[k] = getattr(self, k)
        params['tasks'] = [t.id for t in self.tasks]
        return params



@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
