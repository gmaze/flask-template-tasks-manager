#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 27/11/2023

from flask import (
    render_template,
    redirect,
    request,
    url_for,
)
from flask import current_app as app
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)

from flask_sqlalchemy.session import Session

from apps import db
from apps.simulations import blueprint
from apps.simulations.forms import SimulationForm
from apps.apis.models import Tasks
from apps.authentication.models import Users
from apps.apis.util import TasksManager


# print("simulations.routes")
# print(db.session)
# print(type(db.session))
T = TasksManager(db.session)


@blueprint.route('/simulations/launch', methods=['GET', 'POST'])
@login_required
def simulations():
    simulation_form = SimulationForm(request.form)

    if 'launch' in request.form:

        # Locate user
        # user = Users.query.filter_by(username=str(current_user)).first()

        # Read form data
        label = request.form['label']
        nfloats = request.form['nb_floats']

        # Submit new simulation:
        payload = {'user_id': current_user.get_id(),
                  'label': label,
                  'nfloats': nfloats}
        # print("Submitted new task from webapp with", payload)
        TasksManager(db.session).create(payload)

        return render_template('simulations/launcher.html',
                               form=SimulationForm(request.form),
                               launched=True,
                               )


    return render_template('simulations/launcher.html',
                           form=simulation_form)
