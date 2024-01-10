from flask_wtf import FlaskForm
from wtforms import StringField, IntegerRangeField
from wtforms.validators import DataRequired


class SimulationForm(FlaskForm):
    label = StringField('Label (simulation nickname)',
                             id='sim_label')
    nb_floats = IntegerRangeField('Number of floats',
                             id='sim_nbfloats',
                             validators=[DataRequired()])
