#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 27/11/2023
from flask import Blueprint

blueprint = Blueprint(
    'tasks_blueprint',
    __name__,
    url_prefix='/tasks'
)
