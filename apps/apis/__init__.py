# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 25/11/2023

from flask import Blueprint
from flask_restx import Api
from .namespace_tasks import api as ns_tasks
from .namespace_users import api as ns_users
from .namespace_plans import api as ns_plans
from .namespace_monitors import api as ns_monitors
import logging


# configure root logger
logging.basicConfig(level=logging.INFO)


blueprint = Blueprint(
    'api_blueprint',
    __name__,
    url_prefix='/api/1'
)

api = Api(blueprint,
            title='VirtualFleet-Recovery',
            version='1.0',
            description='An API to make VirtualFleet-Recovery tasks')

api.add_namespace(ns_tasks)
api.add_namespace(ns_users)
api.add_namespace(ns_plans)
api.add_namespace(ns_monitors)
