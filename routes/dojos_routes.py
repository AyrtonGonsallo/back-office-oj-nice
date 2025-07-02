from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os

from forms.form_add_dojo import FormAddDojo
from forms.form_edit_dojo import FormEditDojo

bp = Blueprint('dojos', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')


@bp.route('/dojos', methods=['GET', 'POST'])
def dojos():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    # Paramètres de recherche et tri
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'asc')
    page = int(request.args.get('page', 1))
    per_page = 10

    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_dojos')
        response.raise_for_status()
        dojos = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search:
            dojos = [u for u in dojos if
                            search.lower() in u['nom'].lower()]

        # Tri
        dojos = sorted(
            dojos,
            key=lambda x: x.get(sort, ''),
            reverse=(direction == 'desc')
        )

        # Pagination manuelle
        total = len(dojos)
        start = (page - 1) * per_page
        end = start + per_page
        dojos_page = dojos[start:end]

        # Pour le template
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
        }

        return render_template(
            'dojos.html',
            dojos=dojos_page,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
            user=user
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"


@bp.route('/ajouter_dojo', methods=['GET', 'POST'])
def ajouter_dojo():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    form = FormAddDojo()


    if form.validate_on_submit():
        # Traiter les données du formulaire ici
        nom = form.nom.data

        # envoyer post a http://localhost:3000/api/auth/add_user
        payload = {
            'nom': nom,
        }
        data=None

        try:
            response = requests.post(
                f'{API_BASE_URL}/api/dojo_cours/add_dojo',
                json=payload,
                timeout=5  # optionnel, éviter attente infinie
            )
            data = response.json()
            response.raise_for_status()  # Lève une erreur si code >=400
            flash(f'Le dojo {nom} a été bien été créé .', 'success')
            return redirect(url_for('dojos.dojos'))
        except requests.RequestException as e:
            print(data)
            flash(f'Erreur lors de la création de du dojo : {data["message"]}', 'danger')
    return render_template('ajouter_dojo.html',user=user,form=form)


@bp.route('/modifier_dojo/<int:dojo_id>', methods=['GET', 'POST'])
def modifier_dojo(dojo_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    form2 = FormEditDojo()

    # Récupération de l'utilisateur à modifier
    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_dojo/{dojo_id}')
        response.raise_for_status()
        dojo = response.json()
        print(dojo)
    except requests.RequestException as e:
        print("Erreur requête API:", e)
        dojo = None
        flash("Impossible de charger le dojo.", "danger")
        return redirect(url_for('gestion_des_comptes.gestion_des_comptes'))  # ou autre page d'erreur

    # Remplir le formulaire avec les données existantes uniquement en GET
    if request.method == 'GET':
        form_data = {
            'nom': dojo.get('nom', '')
        }
        form2.process(data=form_data)

    # Soumission du formulaire
    if form2.validate_on_submit():
        payload = {
            'nom': form2.nom.data
        }

        try:
            response = requests.put(
                f'{API_BASE_URL}/api/dojo_cours/update_dojo/{dojo_id}',
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            flash('dojo modifié avec succès !', 'success')
            return redirect(url_for('dojos.dojos'))  # ou autre page
        except requests.RequestException as e:
            flash(f'Erreur lors de la modification du dojo : {e}', 'danger')
    else:
        if request.method == 'POST':
            print(form2.errors)
            flash("Le formulaire contient des erreurs.", "warning")

    return render_template('modifier_dojo.html', user=user, form2=form2)


@bp.route('/supprimer_dojo/<int:dojo_id>', methods=['GET'])
def supprimer_dojo(dojo_id):
    try:
        response = requests.delete(
            f'{API_BASE_URL}/api/dojo_cours/delete_dojo/{dojo_id}',
            timeout=5
        )
        response.raise_for_status()
        flash('dojo supprimé avec succès !', 'success')
    except requests.RequestException as e:
        flash(f'Erreur lors de la suppression du dojo : {e}', 'danger')

    return redirect(url_for('dojos.dojos'))  # Redirection vers la liste des utilisateurs