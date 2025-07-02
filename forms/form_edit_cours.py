from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TimeField, SelectMultipleField
from wtforms.validators import DataRequired


class FormEditCours(FlaskForm):
    heure = TimeField('heure', validators=[DataRequired()])
    jour = SelectField('jour',choices=[("Lundi", "Lundi"), ("Mardi", "Mardi"), ("Mercredi", "Mercredi"),
                 ("Jeudi", "Jeudi"), ("Vendredi", "Vendredi"), ("Samedi", "Samedi"),
                 ("Dimanche", "Dimanche")],validators=[DataRequired()])
    dojoId = SelectField('dojo', choices=[],coerce=int, validators=[DataRequired()])
    profsId = SelectMultipleField(
        'professeurs',
        choices=[],  # rempli dynamiquement dans ta vue
        coerce=int,  # important pour recevoir des entiers
        validators=[DataRequired()]
    )
    categorie_age = SelectMultipleField(
        "catégorie d'âge",
        choices=[("éveil", "éveil"),("mini poussins", "mini poussins"),("poussin", "poussin"),("minimes", "minimes"),("benjamin", "benjamin"),
                 ("juniors", "juniors"),("cadets", "cadets"),],
        validators=[DataRequired()]
    )
    submit = SubmitField('Modifier')
