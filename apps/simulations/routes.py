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
from apps.simulations import blueprint
from apps.simulations.forms import SimulationForm
from apps.authentication.models import Users, role_required
from apps.apis.util import TasksManager


T = TasksManager(db.session)


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def default_route():
    simulation_form = SimulationForm(request.form)

    if 'launch' in request.form:

        # Read form data
        label = request.form['label']
        nfloats = request.form['nb_floats']

        # Submit new simulation:
        payload = {'user_id': current_user.get_id(),
                  'label': label,
                  'nfloats': nfloats}

        # Check if user quota allows for new tasks to be created:
        this_user = Users.find_by_id(payload['user_id'])
        if this_user.tasks_desc_to_dict['quota_left'] > 0:
            TasksManager(db.session).create(payload)
        else:
            return render_template('simulations/launcher.html',
                                   form=SimulationForm(request.form),
                                   launched=False,
                                   error="You reached your subscription plan tasks limit ! Please upgrade or wait for %i seconds to submit a new task" % this_user.tasks_desc_to_dict['retry-after']
                                   )

        return render_template('simulations/launcher.html',
                               form=SimulationForm(request.form),
                               launched=True,
                               )

    return render_template('simulations/launcher.html',
                           form=simulation_form)

@blueprint.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.is_authenticated:
        if current_user.role_level < 100:
            return render_template('home/page-401.html'), 401
        else:
            return render_template('simulations/dashboard.html')
    else:
        return render_template('home/page-403.html'), 403