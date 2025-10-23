from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,SelectField,EmailField
from wtforms.validators import DataRequired, Length


class FormEditParametre(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    valeur = StringField('valeur', validators=[DataRequired()])
    submit = SubmitField('Modifier')
