from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,SelectField,EmailField
from wtforms.validators import DataRequired

class FormAddUser(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    prenom = StringField('prenom', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired()])
    role = SelectField('Role',choices=[ ] ,validators=[DataRequired()])
    submit = SubmitField('Ajouter')
