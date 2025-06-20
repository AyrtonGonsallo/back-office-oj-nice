from datetime import datetime
import json
from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os

from forms.form_add_cours import FormAddCours
from forms.form_edit_cours import FormEditCours

bp = Blueprint('cours', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')





@bp.route('/cours', methods=['GET', 'POST'])
def cours():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    # Paramètres de recherche et tri
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'asc')
    page = int(request.args.get('page', 1))
    per_page = 10

    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_all_cours')
        response.raise_for_status()
        cours = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search:
            cours = [c for c in cours if
                            search.lower() in c['Dojo']['nom'].lower() or search.lower() in c['categorie_age'].lower() or search.lower() in c['jour'].lower() or search.lower() in json.dumps(c['Utilisateurs']).lower()]

        # Tri
        cours = sorted(
            cours,
            key=lambda x: x['Role']['titre'] if sort == 'role' else x.get(sort, ''),
            reverse=(direction == 'desc')
        )

        # Pagination manuelle
        total = len(cours)
        start = (page - 1) * per_page
        end = start + per_page
        cours_page = cours[start:end]

        # Pour le template
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
        }

        return render_template(
            'cours.html',
            cours=cours_page,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
            user=user
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"


@bp.route('/ajouter_cours', methods=['GET', 'POST'])
def ajouter_cours():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    form = FormAddCours()
    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_dojos')
        response.raise_for_status()
        dojos = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        dojos = []

        # Remplir les choices dynamiquement
    form.dojoId.choices = [(int(dojo['id']), dojo['nom']) for dojo in dojos]

    # Récupération des rôles pour le champ select
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/get_professeurs')
        response.raise_for_status()
        professeurs = response.json()
    except requests.RequestException:
        professeurs = []

    form.profsId.choices = [(str(professeur['id']), professeur['nom'] + ' ' + professeur['prenom']) for professeur in
                             professeurs]

    if form.validate_on_submit():
        # Récupération des données du formulaire
        heure = form.heure.data.strftime('%H:%M')  # conversion objet `time` -> chaîne
        jour = form.jour.data
        dojoId = form.dojoId.data
        profsIds = form.profsId.data  # liste d'IDs
        categories = form.categorie_age.data  # liste aussi (car SelectMultipleField)

        # Construction du payload à envoyer
        payload = {
            'heure': heure,
            'jour': jour,
            'dojoId': dojoId,
            'profsIds': profsIds,  # tableau
            'categorie_age': categories  # tableau
        }

        try:
            response = requests.post(
                f'{API_BASE_URL}/api/dojo_cours/add_cours',
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            flash(f"Le cours a été créé avec succès.", 'success')
            return redirect(url_for('cours.cours'))

        except requests.RequestException as e:
            print(e)
            try:
                data = response.json()
                message = data.get("message", "Erreur inconnue")
            except:
                message = "Erreur réseau ou serveur."
            flash(f"Erreur lors de la création du cours : {message}", 'danger')

    return render_template("ajouter_cours.html", user=user, form=form)


@bp.route('/modifier_cours/<int:cours_id>', methods=['GET', 'POST'])
def modifier_cours(cours_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    form2 = FormEditCours()

    # Récupération des rôles pour le champ select
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/get_professeurs')
        response.raise_for_status()
        professeurs = response.json()
    except requests.RequestException:
        professeurs = []

    form2.profsId.choices = [(str(professeur['id']), professeur['nom']+' '+professeur['prenom']) for professeur in professeurs]

    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_dojos')
        response.raise_for_status()
        dojos = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        dojos = []

        # Remplir les choices dynamiquement
    form2.dojoId.choices = [(int(dojo['id']), dojo['nom']) for dojo in dojos]

    # Récupération du cours à modifier
    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_cours/{cours_id}')
        response.raise_for_status()
        cours = response.json()
        print(cours)
    except requests.RequestException as e:
        print("Erreur requête API:", e)
        cours = None
        flash("Impossible de charger l'utilisateur.", "danger")
        return redirect(url_for('cours.cours'))  # ou autre page d'erreur

    # Remplir le formulaire avec les données existantes uniquement en GET
    # Remplir le formulaire avec les données existantes (GET)
    if request.method == 'GET':
        form_data = {
            'heure': datetime.strptime(cours.get('heure', ''), '%H:%M:%S').time() if cours.get('heure') else None,
            'jour': cours.get('jour', ''),
            'dojoId': str(cours.get('dojoId', '')),
            'profsId': [u['id'] for u in cours.get('Utilisateurs', [])],  # liste d'IDs
            'categorie_age': cours.get('categorie_age', '').split(', ')  # liste
        }
        form2.process(data=form_data)
    print(form2.profsId.data)
    # Soumission du formulaire (POST)
    if form2.validate_on_submit():
        payload = {
            'heure': form2.heure.data.strftime('%H:%M'),
            'jour': form2.jour.data,
            'dojoId': form2.dojoId.data,
            'profsIds': form2.profsId.data,
            'categorie_age': form2.categorie_age.data  # liste
        }

        try:
            response = requests.put(
                f'{API_BASE_URL}/api/dojo_cours/update_cours/{cours_id}',
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            flash('Cours modifié avec succès !', 'success')
            return redirect(url_for('cours.cours'))

        except requests.RequestException as e:
            flash(f'Erreur lors de la modification du cours : {e}', 'danger')

    else:
        if request.method == 'POST':
            print(form2.errors)
            flash("Le formulaire contient des erreurs.", "warning")

    return render_template('modifier_cours.html', user=user, form=form2)


@bp.route('/supprimer_cours/<int:cours_id>', methods=['GET'])
def supprimer_cours(cours_id):
    try:
        response = requests.delete(
            f'{API_BASE_URL}/api/dojo_cours/delete_cours/{cours_id}',
            timeout=5
        )
        response.raise_for_status()
        flash('Cours supprimé avec succès !', 'success')
    except requests.RequestException as e:
        flash(f'Erreur lors de la suppression du cours : {e}', 'danger')

    return redirect(url_for('cours.cours'))  # Redirection vers la liste des cours