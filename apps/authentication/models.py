# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import date, datetime, timedelta
import uuid

from apps import db, login_manager
from apps.authentication.util import hash_pass
from apps.subscriptions.models import SubscriptionPlans


class UsersRole(db.Model):

    __tablename__ = 'UsersRole_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    label = db.Column(db.String(64), unique=True)
    level = db.Column(db.Integer)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack its value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        summary = ["<UsersRole.%i>" % self.id]
        summary.append("Label: %s" % self.label)
        summary.append("Level: %i" % self.level)
        return "\n".join(summary)

    def to_dict(self):
        return {'label': self.label, 'level': self.level}

    @classmethod
    def find_by_label(self, label):
        return self.query.filter_by(label=label).first()



class TimestampMixin:
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Users(db.Model, UserMixin, TimestampMixin):

    __tablename__ = 'Users_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    apikey = db.Column(db.String(80))

    role_id: Mapped[int] = mapped_column(ForeignKey("UsersRole_table.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("SubscriptionPlans_table.id"))

    tasks: Mapped[List["Tasks"]] = relationship(back_populates="user")

    def __init__(self, **kwargs):
        plan_set = False
        role_set = False
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

            if property == 'plan_id':
                plan_set = True

            if property == 'role_id':
                role_set = True

        self.apikey = uuid.uuid4().hex

        if not role_set:
            default_role_user = db.session.query(UsersRole).filter_by(level=0).first()
            self.role_id = default_role_user.id

        if not plan_set:
            default_plan = db.session.query(SubscriptionPlans).filter_by(level=0).first()
            self.plan_id = default_plan.id

    def __repr__(self):
        summary = ["<Users.%i>" % self.id]
        summary.append("Created: %s" % self.created)
        summary.append("Last update: %s" % self.updated)
        summary.append("Username: %s" % self.username)
        summary.append("Email: %s" % self.email)
        summary.append("Role ID: %i" % self.role_id)
        summary.append("Plan ID: %i" % self.plan_id)
        summary.append("API key: %s" % self.apikey)
        if self.tasks:
            summary.append("Tasks ID: %s" % (",".join([str(t.id) for t in self.tasks])))
        return "\n".join(summary)

    @classmethod
    def find_by_api_key(self, apikey):
        return self.query.filter_by(apikey=apikey).first()

    @classmethod
    def find_by_id(self, id):
        return self.query.filter_by(id=id).first()

    @property
    def role(self):
        return db.session.query(UsersRole).filter_by(id=self.role_id).first()

    @property
    def role_level(self):
        return db.session.query(UsersRole).filter_by(id=self.role_id).first().level

    @property
    def plan(self):
        return db.session.query(SubscriptionPlans).filter_by(id=self.plan_id).first()

    @property
    def tasks_desc_to_dict(self):
        summary = {}

        # Get the list of tasks ever submitted:
        summary['history'] = [t.id for t in self.tasks]

        # Count how many tasks were submitted over the last quota refreshing window:
        now, count, count_running, accounted, results = datetime.utcnow(), 0, 0, {}, {'success': 0, 'failed': 0, 'cancelled': 0}
        for t in self.tasks:
            age_seconds = (now - t.created).total_seconds()
            if age_seconds <= self.plan.quota_refresh:
                accounted[count] = t
                count += 1
            if t.status == 'running':
                count_running += 1

            if t.final_state == 'success':
                results['success'] += 1
            elif t.final_state == 'failed':
                results['failed'] += 1
            else:
                results['cancelled'] += 1

        # Compute the retry-after header parameter to return in case quota is reached:
        if len(accounted) > 0:
            oldest_accounted = min([t.created for t in accounted.values()])
            retry_after = timedelta(seconds=self.plan.quota_refresh)-(now-oldest_accounted)
            retry_after = int(retry_after.total_seconds())
        else:
            retry_after = self.plan.quota_refresh

        # print("%i tasks over the last %i seconds, and counting..." % (count, self.plan.quota_refresh))
        summary['quota_count'] = count
        summary['quota_left'] = self.plan.quota_tasks - count
        summary['running'] = count_running
        summary['results'] = results
        summary['retry-after'] = retry_after
        return summary

    def to_dict(self):
        params = {}
        for k in ['id', 'created', 'updated', 'username', 'email', 'apikey']:
            params[k] = getattr(self, k)
        params['role'] = self.role.to_dict()
        params['subscription_plan'] = self.plan.to_dict()
        # params['tasks'] = [t.id for t in self.tasks]
        params['tasks'] = self.tasks_desc_to_dict
        return params



@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
