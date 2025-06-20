from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class FormRecuperation(FlaskForm):
    form_name = HiddenField(default='recuperation')
    identifiant2 = StringField('Identifiant', validators=[DataRequired()])
    submit2 = SubmitField('Envoyer')

