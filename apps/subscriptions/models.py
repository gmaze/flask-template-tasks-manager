from apps import db
import json
from datetime import date, datetime
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from dataclasses import dataclass


@dataclass
class SubscriptionPlans(db.Model):

    __tablename__ = 'SubscriptionPlans_table'

    id: Mapped[int] = mapped_column(primary_key=True)
    label = db.Column(db.String(64), unique=True)
    level = db.Column(db.Integer)
    quota_tasks = db.Column(db.Integer)
    quota_refresh = db.Column(db.Integer)

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
        summary = ["<SubscriptionPlans.%i>" % self.id]
        summary.append("Label: %s" % self.label)
        summary.append("Level: %i" % self.level)
        summary.append("Quota:")
        summary.append("\tNumber of tasks: %i" % self.quota_tasks)
        summary.append("\tQuota refreshing time frame (seconds): %i" % self.quota_refresh)
        return "\n".join(summary)

    def to_dict(self):
        params = {}
        for k in ['id', 'label', 'level', 'quota_tasks', 'quota_refresh']:
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
    def find_by_label(self, label):
        return self.query.filter_by(label=label).first()

    @classmethod
    def find_by_id(self, id):
        return self.query.filter_by(id=id).first()

    def plans(self) -> List[dict]:
        all_plans = self.query.order_by(self.level).all()
        return [self.to_dict(p) for p in all_plans]