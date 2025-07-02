from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TimeField, SelectMultipleField, EmailField, DateField, \
    BooleanField
from wtforms.validators import DataRequired, Regexp


class FormAddAppel(FlaskForm):

    date = DateField('date du jour', validators=[DataRequired()])
    adherentId = SelectField('adhérent', choices=[],coerce=int, validators=[DataRequired()])
    coursId = SelectField(
        'cours',
        choices=[],  # rempli dynamiquement dans ta vue
        coerce=int,  # important pour recevoir des entiers
        validators=[DataRequired()]
    )
    status = BooleanField("Présent")
    submit = SubmitField('Ajouter')
