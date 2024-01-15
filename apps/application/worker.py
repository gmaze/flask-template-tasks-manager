#!/usr/bin/env python
# -*coding: UTF-8 -*-
#
# This is the code that receive parameters to execute a simulation
#
# Created by gmaze on 29/11/2023

import os
import sys
import json
import time
import logging
import warnings
from datetime import timezone
from datetime import date, datetime
import fcntl


log = logging.getLogger("worker")
BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class PoolHelper:
    """Worker Pool manager helper

    Example
    -------
    Execute a task within the Pool context, to make sure the limited amount of concurrent running workers
    is respected:
    >>> with PoolHelper(job_id=12) as P:
    >>>     execute_task()

    Manually Register a new worker in the Pool:
    >>> PoolHelper().checkin(job_id)

    Manually Remove a worker from the pool:
    >>> PoolHelper().checkout(job_id)


    """
    lockfile = os.path.sep.join([BASEDIR, "logs", "worker_pool.json"])
    _default_data = {'version': '1.0',
                     'created': datetime.now(timezone.utc),
                     'last_update': None,
                     'max_worker': 1,
                     'workers': [],
                     }

    def __init__(self, job_id: int = None, max: int = -1):
        if max == -1:
            # max = app.config['MAX_CONCURRENT_TASKS']
            max = 5
        self.max_concurrent = max
        self._init()
        self.job_id = job_id
        log.info("Pool instantiated")

    def _json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    def _init(self):
        # If lockfile does not exist, initiate it:
        if not os.path.exists(self.lockfile):
            data = self._default_data
            data['max_worker'] = self.max_concurrent
            self._write(data)
            # log.info("Pool initiated")
        # else:
            # log.info("Pool already initiated")

    def _read(self):
        with open(self.lockfile, "r") as f:
            data = json.loads(f.read())
        return data

    def _write(self, data):
        with open(self.lockfile, 'w') as fp:
            fcntl.flock(fp, fcntl.LOCK_EX)
            data['last_update'] = datetime.now(timezone.utc)
            json.dump(data, fp, default=self._json_serial, ensure_ascii=False, indent=4)
            fcntl.flock(fp, fcntl.LOCK_UN)

    @property
    def concurrent(self):
        """Return the nb of concurrent running workers"""
        return len(self._read()['workers'])

    def checkin(self, job_id: int):
        log.debug("Pool checking-in job_id=%i" % job_id)
        data = self._read()
        if self.concurrent < self.max_concurrent:
            data['workers'].append(job_id)
            self._write(data)
        else:
            warnings.warn("This Pool has reached its maximum number of concurrent worker, try again later")
        # log.info("Pool check-in")
        return self

    def checkout(self, job_id: int):
        data = self._read()
        if job_id in data['workers']:
            data['workers'].remove(job_id)
            self._write(data)
        log.info("Pool checked-out job_id=%i" % job_id)
        return self

    def __enter__(self):
        # log.debug("Pool entering context")
        while self.concurrent >= self.max_concurrent:
            # print("Pool is full")
            time.sleep(1)
        else:
            # print("Pool is not longer full")
            self.checkin(self.job_id)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.checkout(self.job_id)

    def __repr__(self):
        summary = ["<Pool>"]
        summary.append("Lock file: %s" % self.lockfile)
        summary.append("Max concurrent workers: %i" % self.max_concurrent)
        summary.append("Currently registered workers: %i" % self.concurrent)
        return "\n".join(summary)


def logfile():
    LOGFILE = os.path.sep.join([BASEDIR, "logs", "worker.log"])
    return LOGFILE


def read_status_for_pid(pid):
    pattern = ("INFO / worker / %i / status: " % pid)
    # print(pattern)
    lines = []
    with open(logfile(), 'r') as log:
        for line in log:
            # print(line.strip())
            if pattern in line.strip():
                lines.append(line.strip())
    if len(lines) == 0:
        raise ValueError("Cannot find this PID status in log file")
    else:
        status = lines[-1].split("/")[-1].replace("status:","").strip()
        return status


def read_progress_for_pid(pid):
    pattern = ("INFO / worker / %i / progress: " % pid)
    lines = []
    with open(logfile(), 'r') as log:
        for line in log:
            if pattern in line.strip():
                lines.append(line.strip())
    if len(lines) == 0:
        raise ValueError("Cannot find this PID progress in log file")
    else:
        progress = float(lines[-1].split("/")[-1].replace("progress:","").strip())
        return progress


# Mandatory function !
def read_data_for_pid(pid):
    pattern1 = ("INFO / worker / %i / status: " % pid)
    pattern2 = ("INFO / worker / %i / progress: " % pid)
    pattern3 = ("INFO / worker / %i / result: " % pid)
    lines1, lines2, lines3 = [], [], []
    with open(logfile(), 'r') as log:
        for line in log:
            if pattern1 in line.strip():
                lines1.append(line.strip())
            if pattern2 in line.strip():
                lines2.append(line.strip())
            if pattern3 in line.strip():
                lines3.append(line.strip())
    if len(lines1) == 0:
        raise ValueError("Cannot find status for this PID in log file")
    else:
        status = lines1[-1].split("/")[-1].replace("status:", "").strip()
        if len(lines2) == 0:
            progress = None
        else:
            progress = float(lines2[-1].split("/")[-1].replace("progress:", "").strip())
        if len(lines3) == 0:
            result = '?'
        else:
            result = lines3[-1].split("/")[-1].replace("result:", "").strip()
        return {'status': status, 'progress': progress, 'result': result}


def load_params(data):
    data = json.loads(data)
    log.debug(data)
    return data


def dummy_task(data):
    """Execute tasks using data dict parameters

    data was sent by :meth:`TasksManager.create`
    data is of the :meth:`Tasks.to_dict` output
    data eg:
        {"id": 3,
        "user_id": 2,
        "label": "",
        "nfloats": 12000,
        "status": "queue",
        "created": "2024-01-11T09:19:23.322712",
        "updated": "2024-01-11T09:19:23.322723",
        "pid": null,
        "final_state": "?",
        "progress": 0.0,
        "storage_path": "/Users/gmaze/git/github/gmaze/flask-template-tasks-manager/apps/static/results/pro/3"}
    """
    def make_dummy_file(fname, bsize=1024):
        f = open(fname, "wb")
        f.seek(bsize - 1)
        f.write(b"\0")
        f.close()

    # Save data parameters to file:
    if 'storage_path' in data:
        fout = os.path.join(data['storage_path'], "data.json")
    else:
        fout = logfile().replace("worker.log", "worker_%i.json" % data['id'])
    with open(fout, 'w') as fp:
        json.dump(data, fp)

    # Dummy task
    TimeLapse = int(int(data['nfloats']) / 10 / 10)
    for i in range(TimeLapse):
        time.sleep(1)
        log.info("progress: %0.1f" % (i*100/TimeLapse))

    # Dummy output:
    if 'storage_path' in data:
        fout = os.path.join(data['storage_path'], "dummy_result_file")
        make_dummy_file(fout, 1024*TimeLapse*2)

    # Return boolean output to indicate success or failure
    return int(time.time()) & 0x1


if __name__ == '__main__':
    DEBUGFORMATTER = '%(asctime)s / %(levelname)s / %(name)s / %(process)d / %(message)s'
    logging.basicConfig(
        level=logging.DEBUG,
        format=DEBUGFORMATTER,
        # datefmt='%I:%M:%S %p',
        datefmt='%d/%m %H:%M:%S',
        handlers=[logging.FileHandler(logfile(), mode='a')]
    )

    # sys.argv[0]  # this script name
    if len(sys.argv) == 2:
        data = load_params(sys.argv[1])  # Read arguments from a json string
        log.info("status: queue")

        with PoolHelper(job_id=data['id']):
            log.info("status: running")
            try:
                outcome = dummy_task(data)
                if outcome:
                    log.info("result: success")
                else:
                    log.info("result: failed")
                log.info("status: done")
            except:
                log.info("status: error")
                log.info("result: error")
                pass
    # elif len(sys.argv) == 3:
    #     pid = sys.argv[2]
        # print(read_status_for_pid(LOGFILE, int(pid)))
    else:
        log.debug("No json data")

