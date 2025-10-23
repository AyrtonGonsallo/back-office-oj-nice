from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TimeField, SelectMultipleField, EmailField, DateField
from wtforms.validators import DataRequired, Regexp, Optional


class FormAddAdherent(FlaskForm):
    nom = StringField('nom', validators=[DataRequired()])
    prenom = StringField('prenom', validators=[DataRequired()])
    email = EmailField('email')
    telephone = StringField('telephone', validators=[Optional(),Regexp(
            r'^(0|\+33)*[1-9](\d{2}){4}$',
            message="Numéro de téléphone invalide. Format attendu : 0601020304 ou +33601020304"
        )])
    date_inscription = DateField('date d\'inscription',validators=[Optional()] )
    dojoId = SelectField('dojo', choices=[],coerce=int, validators=[DataRequired()])
    coursId = SelectMultipleField(
        'cours',
        choices=[],  # rempli dynamiquement dans ta vue
        coerce=int,  # important pour recevoir des entiers
        validators=[Optional()]
    )
    categorie_age = SelectField(
        "catégorie d'âge",
        choices=[("éveil", "éveil"),("mini poussins", "mini poussins"),("poussin", "poussin"),("minimes", "minimes"),("benjamin", "benjamin"),
                 ("juniors", "juniors"),("cadets", "cadets"),],
        validators=[DataRequired()]
    )
    submit = SubmitField('Ajouter')
