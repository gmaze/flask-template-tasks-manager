#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 28/11/2023

from abc import abstractmethod
from subprocess import Popen, PIPE
from flask_restx.errors import abort
from flask import request
from functools import wraps
import os
from signal import SIGKILL
import psutil
from typing import Union, List
from sqlalchemy.orm.scoping import scoped_session

from apps.apis.models import Tasks as dbTasks
from apps.application import read_data_for_pid
from apps.authentication.models import Users


BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class TasksManager_proto:
    """Proto with DB registry of tasks"""

    def __init__(self, db_session: scoped_session):
        self.db_session = db_session

    @abstractmethod
    def update_tasks_status(self, obj: Union[dbTasks, List[dbTasks]]):
        """This method will be executed on each GET request to all or one task"""
        raise NotImplementedError("Not implemented")

    @property
    def tasks(self) -> List[dict]:
        all_tasks = dbTasks.query.order_by(dbTasks.id.desc()).all()
        self.update_tasks_status(all_tasks)
        return [self.to_dict(t) for t in all_tasks]

    def get(self, id, raw=False) -> dict:
        a_task = dbTasks.query.filter_by(id=id).first()
        if a_task:
            a_user = Users.query.filter_by(id=a_task.user_id).first()
            a_task.username = a_user.username
            self.update_tasks_status(a_task)
            return self.to_dict(a_task) if not raw else a_task
        else:
            abort(404, "Task {} doesn't exist".format(id))

    def tasks_by_user_id(self, user_id) -> List[dict]:
        all_tasks = dbTasks.query.filter_by(user_id=user_id).order_by(dbTasks.id.desc()).all()
        # all_tasks = dbTasks.find_by_user_id(user_id=user_id)
        self.update_tasks_status(all_tasks)
        return [self.to_dict(t) for t in all_tasks]

    def tasks_by_apikey(self, apikey) -> List[dict]:
        user = Users.find_by_api_key(apikey)
        return self.tasks_by_user_id(user.id)

    def _register(self, data) -> dbTasks:
        default_data = {'label': None, 'nfloats': 1000, 'status': 'queue'}
        params = {**default_data, **data}

        a_task = dbTasks(**params)
        self.db_session.add(a_task)
        self.db_session.commit()
        return a_task

    @abstractmethod
    def _launch(self, dbTasks) -> (dbTasks, Union[bool, Exception]):
        """Executed on self.create(data) calls
        It is expected that this method returns a tuple (dbTasks, result) where result is either True or an Exception
        """
        raise NotImplementedError("Not implemented")

    def create(self, data: dict) -> dict:
        # print('Create new task with:', data)
        a_task = self._register(data)
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

        return self.to_dict(a_task)

    @abstractmethod
    def _delete(self, obj: dbTasks):
        raise NotImplementedError("Not implemented")

    def delete(self, id: int) -> dict:
        a_task = self.get(id)
        try:
            self._delete(a_task)
        except:
            raise
        finally:
            self.db_session.delete(a_task)
            self.db_session.commit()
        return self.to_dict(a_task)

    @abstractmethod
    def _cancel(self, obj: dbTasks):
        raise NotImplementedError("Not implemented")

    def cancel(self, id: int) -> dict:
        a_task = self.get(id, raw=True)
        try:
            self._cancel(a_task)
            # Update status:
            a_task.status = 'cancelled'
            self.db_session.commit()
        except:
            raise
        return self.to_dict(a_task)

    def check_pid(self, pid):
        """ Check For the existence of a unix pid. """
        return psutil.pid_exists(pid)

    def kill_pid(self, pid):
        if self.check_pid(pid):
            os.kill(pid, SIGKILL)

        if self.check_pid(pid):
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()

    def to_dict(self, obj: dbTasks) -> dict:
        """Unravel a Task model instance to a nested dictionary matching the api model response"""

        def task2dict(obj) -> dict:
            task_core = {'id': None, 'created': None, 'updated': None}
            task_user = {'user_id': None, 'username': None}
            task_params = {'nfloats': None, 'label': None}
            task_run = {'status': None, 'progress': None, 'final_state': None}

            for key in task_core.keys():
                task_core[key] = getattr(obj, key)

            for key in task_user.keys():
                # task_user[key] = getattr(obj, key)
                if key == 'username':
                    task_user[key] = getattr(obj.user, key)
                else:
                    task_user[key] = getattr(obj, key)

            for key in task_params.keys():
                task_params[key] = getattr(obj, key)
                # if key == 'username':
                #     task_params[key] = getattr(obj.user, key)
                # else:
                #     task_params[key] = getattr(obj, key)

            for key in task_run.keys():
                task_run[key] = getattr(obj, key)

            task_core['user'] = task_user
            task_core['params'] = task_params
            task_core['run'] = task_run

            return task_core

        return task2dict(obj)


class TasksManager(TasksManager_proto):
    """Applicative part"""

    def update_tasks_status(self, obj: Union[dbTasks, List[dbTasks]]):
        """This method is executed on each GET request or list of tasks objects
        For this application, will call on the worker `read_data_for_pid` function to read info from log file
        and commit to database
        """

        def update(a_task):
            pid = a_task.pid

            # Read PID data (eg: scanning the worker log file)
            data = read_data_for_pid(pid)
            a_task.status = data['status']
            a_task.progress = data['progress']
            a_task.final_state = data['result']

            # If PID no longer exists:
            if not self.check_pid(pid):
                if a_task.status == 'running' and a_task.final_state == '?':
                    # Looks like the process has been killed before reaching the end of the execution
                    # So that we don't have the final state
                    a_task.status = 'cancelled'

            # But if PID exists, it could be a zombie:
            elif self.check_pid(pid) and psutil.Process(pid).status() == psutil.STATUS_ZOMBIE:
                if a_task.final_state in ['success', 'failed']:
                    # it was zombie, but went through the end of the job (because we have a final_state),
                    # so, we rescue this status:
                    a_task.status = 'done'
                else:
                    # this is really a zombie job that didn't go through the end before being killed:
                    a_task.status = 'cancelled'

            # Update db
            self.db_session.commit()

        if isinstance(obj, dbTasks):
            if obj.pid is not None:
                update(obj)
        elif isinstance(obj, list):
            for a_task in obj:
                if a_task.pid is not None:
                    update(a_task)
        else:
            raise ValueError("Unexpected object type %s" % type(obj))

        return self

    def _launch(self, a_task: dbTasks):
        # Do something to launch the script

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
        # (Basically we kill the process and its child using its PID)
        if a_task.pid is not None:
            try:
                self.kill_pid(a_task.pid)
                # os.kill(a_task.pid, SIGKILL)

                a_task.final_state = '?'
                self.db_session.commit()
                return a_task
            except:
                raise
        else:
            abort(403, "This task has not been executed and cannot be cancelled")


    def _delete(self, a_task: dbTasks):
        # Do something to delete this task
        print("Do something to delete a task")
        pass


class APIkey:
    """API key helper class"""
    def __init__(self, key=None):
        if key is None:
            if 'X-Api-Key' in request.headers:
                self.key = request.headers['X-Api-Key']
            elif 'apikey' in request.args:
                self.key = request.headers['apikey']
            else:
                abort(400, "You must provide a valid API key with the 'X-Api-Key' header parameter in your request")
        else:
            self.key = key

    @property
    def is_valid(self):
        if self.user:
            return True

    @property
    def user(self):
        return Users.find_by_api_key(self.key)

    @property
    def user_id(self):
        if self.is_valid:
            return self.user.id
        else:
            abort(401, "Invalid API key")

    @property
    def user_role_level(self):
        if self.is_valid:
            return self.user.role.level
        else:
            abort(401, "Invalid API key")


def apikey_required(view_function):
    """A Decorator ensuring we're passing in a valid APIkey"""
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if APIkey().is_valid:
            return view_function(*args, **kwargs)
        else:
            abort(401, "Invalid API key")
    return decorated_function

def apikey_admin_required(view_function):
    """A Decorator ensuring API-key corresponds to an Admin role level"""
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if APIkey().is_valid:
            if APIkey().user_role_level >= 100:
                return view_function(*args, **kwargs)
            else:
                abort(401, "Insufficient privilege")
        else:
            abort(401, "Invalid API key")
    return decorated_function
