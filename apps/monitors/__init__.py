from flask import Blueprint

blueprint = Blueprint(
    'monitors_blueprint',
    __name__,
    url_prefix='/monitors'
)

