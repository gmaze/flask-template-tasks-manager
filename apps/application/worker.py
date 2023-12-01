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

log = logging.getLogger("worker")


def logfile():
    BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
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
        status = lines1[-1].split("/")[-1].replace("status:","").strip()
        if len(lines2) == 0:
            progress = None
        else:
            progress = float(lines2[-1].split("/")[-1].replace("progress:","").strip())
        if len(lines3) == 0:
            result = '?'
        else:
            result = lines3[-1].split("/")[-1].replace("result:","").strip()
        return {'status': status, 'progress': progress, 'result': result}



def load_params(data):
    data = json.loads(data)
    log.debug(data)
    return data


def dummy_task(data):
    TimeLapse = int(int(data['nfloats']) / 10 / 10)
    for i in range(TimeLapse):
        time.sleep(1)
        log.info("progress: %0.1f" % (i*100/TimeLapse))
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

    # Read arguments as a json string
    # sys.argv[0]  # this script name
    if len(sys.argv) == 2:
        data = load_params(sys.argv[1])
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
