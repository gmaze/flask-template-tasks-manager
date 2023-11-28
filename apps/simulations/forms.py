#!/bin/env python
# -*coding: UTF-8 -*-
#
# HELP
#
# Created by gmaze on 27/11/2023
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, IntegerRangeField
from wtforms.validators import Email, DataRequired

class SimulationForm(FlaskForm):
    label = StringField('Label (simulation nickname)',
                             id='sim_label')
    nb_floats = IntegerRangeField('Number of floats',
                             id='sim_nbfloats',
                             validators=[DataRequired()])
