from apps import db
import json
from datetime import date, datetime
from typing import List
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import func
from dataclasses import dataclass


class TimestampMixin:
    created: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Monitor_proto:

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    value = db.Column(db.Float)

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
        summary = ["<Monitor>"]
        summary.append("Label: %s" % self.label)
        summary.append("Unit: %i" % self.unit)
        return "\n".join(summary)

    @classmethod
    def time_range(self):
        max = self.query(self.timestamp, func.max(self.timestamp))
        min = self.query(self.timestamp, func.min(self.timestamp))
        return min, max

    @classmethod
    def value_range(self):
        max = self.query(self.value, func.max(self.value))
        min = self.query(self.value, func.min(self.value))
        return min, max


@dataclass
class Monitor_CPU(db.Model, TimestampMixin, Monitor_proto):
    __tablename__ = 'Monitor_CPU_table'
    label = "System CPU"
    unit = "%"

@dataclass
class Monitor_VMEM(db.Model, TimestampMixin, Monitor_proto):
    __tablename__ = 'Monitor_VMEM_table'
    label = "Virtual Memory"
    unit = "Mb"
    total = db.Column(db.Float)
    available = db.Column(db.Float)

@dataclass
class Monitor_DISK(db.Model, TimestampMixin, Monitor_proto):
    __tablename__ = 'Monitor_DISK_table'
    label = "Disk Usage"
    unit = "Mb"
    total = db.Column(db.Float)
    available = db.Column(db.Float)
