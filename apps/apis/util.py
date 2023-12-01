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
from signal import SIGKILL
import psutil
from typing import Union, List
from sqlalchemy.orm.scoping import scoped_session

from apps.apis.models import Tasks as dbTasks
from apps.application import read_data_for_pid


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
    def tasks(self) -> dbTasks:
        all_tasks = dbTasks.query.order_by(dbTasks.id.desc()).all()
        self.update_tasks_status(all_tasks)
        return all_tasks

    def get(self, id) -> dbTasks:
        a_task = dbTasks.query.filter_by(id=id).first()
        if a_task:
            self.update_tasks_status(a_task)
            return a_task
        else:
            abort(404, "Task {} doesn't exist".format(id))

    def _register(self, data) -> dbTasks:
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
    def _launch(self, dbTasks) -> (dbTasks, Union[bool, Exception]):
        """Executed on self.create(data) calls
        It is expected that this method returns a tuple (dbTasks, result) where result is either True or an Exception
        """
        raise NotImplementedError("Not implemented")

    def create(self, data: dict) -> dbTasks:
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

        return a_task

    @abstractmethod
    def _delete(self, obj: dbTasks):
        raise NotImplementedError("Not implemented")

    def delete(self, id: int) -> dbTasks:
        a_task = self.get(id)
        try:
            self._delete(a_task)
        except:
            raise
        finally:
            self.db_session.delete(a_task)
            self.db_session.commit()
        return a_task

    @abstractmethod
    def _cancel(self, obj: dbTasks):
        raise NotImplementedError("Not implemented")

    def cancel(self, id: int) -> dbTasks:
        a_task = self.get(id)
        try:
            self._cancel(a_task)
            # Update status:
            a_task.status = 'cancelled'
            self.db_session.commit()
        except:
            raise
        return a_task

    def check_pid(self, pid):
        """ Check For the existence of a unix pid. """
        # try:
        #     os.kill(pid, 0)
        # except OSError:
        #     return False
        # else:
        #     return True
        return psutil.pid_exists(pid)

    def kill_pid(self, pid):
        if self.check_pid(pid):
            os.kill(pid, SIGKILL)

        if self.check_pid(pid):
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()


class TasksManager(TasksManager_proto):
    """Applicative part"""

    def update_tasks_status(self, obj: Union[dbTasks, List[dbTasks]]):
        """This method is executed on each GET request one one or list of tasks objects
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

            return (a_task, True)

        except Exception as e:
            return (a_task, e)

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
