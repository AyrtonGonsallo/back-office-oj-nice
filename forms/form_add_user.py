from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,SelectField,EmailField
from wtforms.validators import DataRequired, Length


class FormAddUser(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    prenom = StringField('prenom', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    dojoId = SelectField('dojo', choices=[], coerce=int, validators=[])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired(message="Le mot de passe est requis."),
        Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères.")])
    role = SelectField('Role',choices=[ ] ,validators=[DataRequired()])
    submit = SubmitField('Ajouter')
