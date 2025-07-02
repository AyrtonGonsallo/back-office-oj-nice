from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os
from forms.form import MyForm
from forms.form_recuperation import FormRecuperation

bp = Blueprint('auth', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')


@bp.route('/', methods=['GET', 'POST'])
def first_contact():
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form_type = request.form.get('form_name')
    form = MyForm()
    formRecuperation = FormRecuperation()

    if form_type == 'connexion' and form.validate_on_submit():
        # traitement ici
        identifiant = form.identifiant.data
        mot_de_passe = form.mot_de_passe.data
        print(mot_de_passe)
        try:
            response = requests.post(
                f'{API_BASE_URL}/api/auth/login',
                headers={'Content-Type': 'application/json'},
                json={
                    'email': identifiant,
                    'password': mot_de_passe
                }
            )
            print(mot_de_passe)
            if response.status_code == 200:
                data = response.json()
                print(data)
                nom = data.get('nom')
                prenom = data.get('prenom')
                role = data.get('role')
                session['user'] = data
                print(f"Bienvenue {prenom} {nom} ({role})")
                return redirect(url_for('tableau_de_bord'))
            else:
                flash('Connexion échouée : identifiants invalides ou serveur indisponible', 'danger')

        except requests.exceptions.RequestException as e:
            flash(f"Erreur de connexion : {str(e)}", 'danger')
            print("123")
    if form_type == 'recuperation' and formRecuperation.validate_on_submit():
        # traitement ici
        identifiant2 = formRecuperation.identifiant2.data
        try:
            response = requests.post(
                f'{API_BASE_URL}/api/auth/recuperer_utilisateur',
                headers={'Content-Type': 'application/json'},
                json={
                    'email': identifiant2
                }
            )
            if response.status_code == 200:
                flash(f"Récupération réussie. Consultez votre adresse {identifiant2}","success")
                return redirect(url_for('auth.login'))
            else:
                flash('Connexion échouée : identifiants invalides ou serveur indisponible', 'danger')

        except requests.exceptions.RequestException as e:
            flash(f"Erreur de connexion : {str(e)}", 'danger')
    return render_template('index.html', form=form,formRecuperation=formRecuperation)


@bp.route('/logout')
def logout():
    session.clear()  # ou session.pop('user', None)
    return redirect(url_for('auth.login'))  # ou vers la page d'accueil