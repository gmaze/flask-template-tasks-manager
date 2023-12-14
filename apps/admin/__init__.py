# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 14/12/2023
from flask import Blueprint

blueprint = Blueprint(
    'admin_blueprint',
    __name__,
    url_prefix='/admin'
)


