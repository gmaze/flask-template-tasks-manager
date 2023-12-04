#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 28/11/2023

from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from apps import db
import json
from datetime import date, datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship



class TimestampMixin:
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tasks(db.Model, TimestampMixin):

    __tablename__ = 'Tasks_table'

    # id = db.Column(db.Integer, primary_key=True)
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("Users_table.id"))
    # username: Mapped[str] = mapped_column(ForeignKey("Users_table.username"))
    user: Mapped["Users"] = relationship(back_populates="tasks")

    label = db.Column(db.String(64))
    nfloats = db.Column(db.Integer)
    status = db.Column(db.String(64))
    pid = db.Column(db.Integer)
    progress = db.Column(db.Float, default=0)
    final_state = db.Column(db.String(64), default='?')

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
        summary = ["<Tasks>"]
        summary.append("Username: %s" % self.user.username)
        summary.append("Status: %s" % self.status)
        summary.append("PID: %s" % self.pid)
        summary.append("Progress: %s" % self.progress)
        summary.append("Final state: %s" % self.final_state)
        summary.append("Parameters:")
        summary.append("\tN-floats: %s" % self.nfloats)
        summary.append("\tlabel: %s" % self.label)
        return "\n".join(summary)
        # return str("%s: %s (%s): %s" % (self.username, self.nfloats, self.status, self.label))

    def to_dict(self):
        params = {}
        for k in ['id', 'username', 'label', 'nfloats', 'status', 'created', 'updated', 'pid', 'final_state', 'progress']:
            params[k] = getattr(self, k)
        return params

    def _json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    def to_json(self):
        data = self.to_dict()
        return json.dumps(data, default=self._json_serial, ensure_ascii=False)