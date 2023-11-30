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


def load_params(data):
    data = json.loads(data)
    log.debug(data)
    return data


def dummy_task(data):
    time.sleep(int(data['nfloats']) / 10 / 10)  # Dummy stuff
    return True



if __name__ == '__main__':
    DEBUGFORMATTER = '%(asctime)s / %(levelname)s / %(name)s / %(process)d / %(message)s'
    logging.basicConfig(
        level=logging.DEBUG,
        format=DEBUGFORMATTER,
        datefmt='%I:%M:%S %p',
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
