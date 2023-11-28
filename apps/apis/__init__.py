# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 25/11/2023

from flask import Blueprint
from flask_restx import Api
from .namespace1 import api as ns1
from .namespace2 import api as ns2
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
            description='An API to make VirtualFleet-Recovery simulations')
api.add_namespace(ns1)
api.add_namespace(ns2)
