#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 27/11/2023

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass
