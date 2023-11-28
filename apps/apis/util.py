#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 28/11/2023

from apps.apis.models import Tasks as dbTasks
from apps import db

class TasksManager:
    status_code = {'queue': 0, 'running': 1, 'done': 2, 'cancelled': 3}

    def __init__(self, api):
        self.api = api
        self.counter = 0

    @property
    def tasks(self):
        return dbTasks.query.order_by(dbTasks.id.desc()).all()

    def get(self, id):
        task = dbTasks.query.filter_by(id=id).first()
        if task:
            return task
        else:
            self.api.abort(404, "Task {} doesn't exist".format(id))

    def _register(self, data):
        if 'username' not in data:
            self.api.abort(403, "You must be authenticated to create a new task")

        params = {'label': None, 'nfloats': 1000}
        for key in ['username', 'label', 'nfloats']:
            if key in data:
                params[key] = data[key]

        a_task = dbTasks(**params)
        db.session.add(a_task)
        db.session.commit()
        return a_task

    def _launch(self, data):
        # Do something to launch the script
        print("Do something to launch the script")
        pass

    def create(self, data):
        a_task = self._register(data)
        self._launch()
        return a_task

    # def update(self, id, data):
    #     a_task = self.get(id)
    #     a_task.update(data)
    #     return a_task

    def delete(self, id):
        a_task = self.get(id)
        db.session.delete(a_task)
        db.session.commit()
        return a_task


class TaskDAO:
    status_code = {'queue': 0, 'running': 1, 'done': 2, 'cancelled': 3}

    def __init__(self, api):
        self.api = api
        self.counter = 0
        self.tasks = []

    def get(self, id):
        for t in self.tasks:
            if t['id'] == int(id):
                return t
        self.api.abort(404, "Task {} doesn't exist".format(id))

    def create(self, data):
        a_task = data
        a_task['id'] = self.counter = self.counter + 1
        if 'label' in data:
            a_task['label'] = data['label']

        if 'nfloats' in data:
            a_task['nfloats'] = data['nfloats']

        if 'status' in data:
            a_task['status'] = data['status']

        self.tasks.append(a_task)
        return a_task

    def update(self, id, data):
        a_task = self.get(id)
        a_task.update(data)
        return a_task

    def delete(self, id):
        a_task = self.get(id)
        self.tasks.remove(a_task)

