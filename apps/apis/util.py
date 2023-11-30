#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 28/11/2023

from abc import abstractmethod
import time
from threading import Thread
from subprocess import Popen, PIPE
from flask_restx.errors import abort
from flask import current_app as app
import json
import os

from apps.apis.models import Tasks as dbTasks
from apps import db
from apps.application import read_data_for_pid

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))



class TasksManager_proto:
    """Proto with DB registry of tasks"""

    def __init__(self, db_session):
        # print("apis.TasksManager_proto")
        # print(db_session)
        # print(type(db_session))

        # OK:
        # <sqlalchemy.orm.scoping.scoped_session object at 0x10cb60910>
        # <class 'sqlalchemy.orm.scoping.scoped_session'>

        # Not OK:
        # <flask_sqlalchemy.session.Session object at 0x10d7cd640>
        # <class 'flask_sqlalchemy.session.Session'>

        self.db_session = db_session

    @property
    def tasks(self) -> dbTasks:
        return dbTasks.query.order_by(dbTasks.id.desc()).all()

    def get(self, id) -> dbTasks:
        task = dbTasks.query.filter_by(id=id).first()
        if task:
            return task
        else:
            abort(404, "Task {} doesn't exist".format(id))

    def __register(self, data) -> dbTasks:
        if 'username' not in data:
            abort(403, "You must be authenticated to create a new task")

        params = {'label': None, 'nfloats': 1000, 'status': 'queue'}
        for key in ['username', 'label', 'nfloats']:
            if key in data:
                params[key] = data[key]

        a_task = dbTasks(**params)
        self.db_session.add(a_task)
        self.db_session.commit()
        return a_task

    @abstractmethod
    def _launch(self, dbTasks) -> bool:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def _cancel(self, dbTasks):
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def _delete(self, dbTasks):
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def update_job_status(self, dbTasks):
        raise NotImplementedError("Not implemented")

    def create(self, data) -> dbTasks:
        a_task = self.__register(data)
        a_task, result = self._launch(a_task)
        if result:
            # Update status:
            # print("Task is submitted")
            a_task.status = 'submitted'
            self.db_session.commit()
        else:
            # Update status:
            a_task.status = 'error'
            self.db_session.commit()
            print("An error occurred when submitting this Task !", a_task)
            raise(result)

        return a_task

    def delete(self, id) -> dbTasks:
        a_task = self.get(id)
        try:
            self._delete(a_task)
        except:
            raise
        finally:
            self.db_session.delete(a_task)
            self.db_session.commit()
        return a_task

    def cancel(self, id) -> dbTasks:
        a_task = self.get(id)
        try:
            self._cancel(a_task)
        except:
            raise
        finally:
            # Update status:
            a_task.status = 'cancelled'
            self.db_session.commit()
        return a_task


class TasksManager(TasksManager_proto):
    """Applicative part"""

    def update_job_status(self, id: int = None):

        def update(pid):
            # task.status = read_status_for_pid(pid)
            data = read_data_for_pid(pid)
            task.status = data['status']
            task.progress = data['progress']
            self.db_session.commit()

        if id is not None:
            task = self.get(id)
            if task.pid is not None:
                update(task.pid)
        else:
            for task in self.tasks:
                if task.pid is not None:
                    update(task.pid)
        return self

    def _launch(self, a_task: dbTasks):
        # Do something to launch the script
        # print("Do something to launch this task:")
        # print(a_task)

        try:
            params = a_task.to_json()
            # print(params)

            worker_script = os.path.sep.join([BASEDIR, "application", "worker.py"])
            # print(worker_script)

            p = Popen(['python', worker_script, params], stdout=PIPE, stderr=PIPE, text=True)
            # output, errors = p.communicate()
            # print('output', output)
            # print('errors', errors)
            # print("Task submitted with PID: %i" % p.pid)
            a_task.pid = p.pid
            self.db_session.commit()

            return a_task, True

        except Exception as e:
            return a_task, e


    def _cancel(self, a_task: dbTasks):
        # Do something to cancel this task
        print("Do something to cancel a task")
        pass

    def _delete(self, a_task: dbTasks):
        # Do something to delete this task
        print("Do something to delete a task")
        pass


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

