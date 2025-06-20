from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,SelectField,EmailField
from wtforms.validators import DataRequired, Length


class FormEditDojo(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    submit = SubmitField('Modifier')
