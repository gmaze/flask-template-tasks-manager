from flask import (
    render_template,
    request,
    abort,
    redirect,
    url_for
)
from flask_login import (
    current_user,
    login_required,
)

from apps import db
from apps.monitors import blueprint


@blueprint.route('/', methods=['GET'])
def default_route():
    # return redirect(url_for('home_blueprint.index'))
    return render_template('home/monitors.html')
