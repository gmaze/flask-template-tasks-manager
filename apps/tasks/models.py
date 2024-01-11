from datetime import datetime, timedelta
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from apps import db
import json
from datetime import date, datetime
from typing import List
from flask import current_app
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TimestampMixin:
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Tasks(db.Model, TimestampMixin):

    __tablename__ = 'Tasks_table'

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("Users_table.id"))
    user: Mapped["Users"] = relationship(back_populates="tasks")

    pid = db.Column(db.Integer)
    status = db.Column(db.String(64))
    progress = db.Column(db.Float, default=0)
    final_state = db.Column(db.String(64), default='?')

    label = db.Column(db.String(64))
    nfloats = db.Column(db.Integer)

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
        summary = ["<Tasks.%i>" % self.id]
        summary.append("Created: %s" % self.created)
        summary.append("Last update: %s" % self.updated)
        summary.append("User:")
        summary.append("\t%s" % self.user)
        summary.append("Parameters:")
        summary.append("\tUsername: %s" % self.user.username)
        summary.append("\tN-floats: %s" % self.nfloats)
        summary.append("\tlabel: %s" % self.label)
        summary.append("\tstorage: %s" % self.storage_path)
        summary.append("Run:")
        summary.append("\tPID: %s" % self.pid)
        summary.append("\tStatus: %s" % self.status)
        summary.append("\tProgress: %s" % self.progress)
        summary.append("\tFinal state: %s" % self.final_state)
        return "\n".join(summary)

    def to_dict(self):
        params = {}
        for k in ['id', 'user_id',
                  'label', 'nfloats',
                  'status', 'created', 'updated', 'pid', 'final_state', 'progress', 'storage_path']:
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

    @classmethod
    def find_by_user_id(self, user_id):
        return self.query.filter_by(user_id=user_id).order_by(self.id.desc()).all()

    def get_oldest_over_period(self, period: int=86400):
        """Return the oldest task created over the last 'period' in seconds"""
        stamp = datetime.utcnow() - timedelta(seconds=period)
        return self.query.filter(self.created >= stamp).all()

    @property
    def storage_path(self):
        # Define path:
        p = os.path.join(self.user.storage_path, str(self.id))

        # Make sure this task has a storage path:
        Path(p).mkdir(exist_ok=True)

        return p