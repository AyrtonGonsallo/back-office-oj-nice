from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,SelectField,EmailField
from wtforms.validators import DataRequired, Length


class FormAddDojo(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    submit = SubmitField('Ajouter')
