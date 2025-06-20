from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField,EmailField
from wtforms.validators import DataRequired

class FormEditUser(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    prenom = StringField('prenom', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    role = SelectField('Role',choices=[ ] ,validators=[DataRequired()])
    submit = SubmitField('Modifier')
