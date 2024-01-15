import os
import json
import time
from datetime import timezone
from datetime import date, datetime
import warnings
import logging
import fcntl


# log = logging.getLogger("application.util")
BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class PoolHelper_old:
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
        print("Pool instantiated:\n", self, "\n")

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
            print("Pool initiated:\n", self, "\n")
        else:
            print("Pool already initiated:\n", self, "\n")

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
        print("Checking-in job_id=%i" % job_id)
        data = self._read()
        if self.concurrent < self.max_concurrent:
            data['workers'].append(job_id)
            self._write(data)
        else:
            warnings.warn("This Pool has reached its maximum number of concurrent worker, try again later")
        print("Pool check-in:\n", self, "\n")
        return self

    def checkout(self, job_id: int):
        data = self._read()
        if job_id in data['workers']:
            data['workers'].remove(job_id)
            self._write(data)
        print("Pool check-out:\n", self, "\n")
        return self

    def __enter__(self):
        print("Pool entering context:\n", self, "\n")
        while self.concurrent >= self.max_concurrent:
            print("Pool is full")
            time.sleep(1)
        else:
            print("Pool is not longer full")
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
