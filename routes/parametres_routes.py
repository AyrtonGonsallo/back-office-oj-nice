from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os

from forms.form_add_parametre import FormAddParametre
from forms.form_edit_parametre import FormEditParametre

bp = Blueprint('parametres', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')


@bp.route('/parametres', methods=['GET', 'POST'])
def parametres():
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
        response = requests.get(f'{API_BASE_URL}/api/parametres/get_parametres')
        response.raise_for_status()
        parametres = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search:
            parametres = [u for u in parametres if
                            search.lower() in u['nom'].lower()]

        # Tri
        parametres = sorted(
            parametres,
            key=lambda x: x.get(sort, ''),
            reverse=(direction == 'desc')
        )

        # Pagination manuelle
        total = len(parametres)
        start = (page - 1) * per_page
        end = start + per_page
        parametres_page = parametres[start:end]

        # Pour le template
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
        }

        return render_template(
            'parametres.html',
            parametres=parametres_page,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
            user=user
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"


@bp.route('/ajouter_parametre', methods=['GET', 'POST'])
def ajouter_parametre():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    form = FormAddParametre()


    if form.validate_on_submit():
        # Traiter les données du formulaire ici
        nom = form.nom.data
        valeur = form.valeur.data

        # envoyer post a http://localhost:3000/api/auth/add_user
        payload = {
            'nom': nom,
            'valeur': valeur,
        }
        data=None

        try:
            response = requests.post(
                f'{API_BASE_URL}/api/parametres/add_parametre',
                json=payload,
                timeout=5  # optionnel, éviter attente infinie
            )
            data = response.json()
            response.raise_for_status()  # Lève une erreur si code >=400
            flash(f'Le parametre {nom} a été bien été créé .', 'success')
            return redirect(url_for('parametres.parametres'))
        except requests.RequestException as e:
            print(data)
            flash(f'Erreur lors de la création de du parametre : {data["message"]}', 'danger')
    return render_template('ajouter_parametre.html',user=user,form=form)


@bp.route('/modifier_parametre/<int:parametre_id>', methods=['GET', 'POST'])
def modifier_parametre(parametre_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    form2 = FormEditParametre()

    # Récupération de l'utilisateur à modifier
    try:
        response = requests.get(f'{API_BASE_URL}/api/parametres/get_parametre/{parametre_id}')
        response.raise_for_status()
        parametre = response.json()
        print(parametre)
    except requests.RequestException as e:
        print("Erreur requête API:", e)
        parametre = None
        flash("Impossible de charger le parametre.", "danger")
        return redirect(url_for('parametres.parametres'))  # ou autre page d'erreur

    # Remplir le formulaire avec les données existantes uniquement en GET
    if request.method == 'GET':
        form_data = {
            'nom': parametre.get('nom', ''),
            'valeur': parametre.get('valeur', '')
        }
        form2.process(data=form_data)

    # Soumission du formulaire
    if form2.validate_on_submit():
        payload = {
            'nom': form2.nom.data,
            'valeur': form2.valeur.data
        }

        try:
            response = requests.put(
                f'{API_BASE_URL}/api/parametres/update_parametre/{parametre_id}',
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            flash('parametre modifié avec succès !', 'success')
            return redirect(url_for('parametres.parametres'))  # ou autre page
        except requests.RequestException as e:
            flash(f'Erreur lors de la modification du parametre : {e}', 'danger')
    else:
        if request.method == 'POST':
            print(form2.errors)
            flash("Le formulaire contient des erreurs.", "warning")

    return render_template('modifier_parametre.html', user=user, form2=form2)


@bp.route('/supprimer_parametre/<int:parametre_id>', methods=['GET'])
def supprimer_parametre(parametre_id):
    try:
        response = requests.delete(
            f'{API_BASE_URL}/api/parametres/delete_parametre/{parametre_id}',
            timeout=5
        )
        response.raise_for_status()
        flash('parametre supprimé avec succès !', 'success')
    except requests.RequestException as e:
        flash(f'Erreur lors de la suppression du parametre : {e}', 'danger')

    return redirect(url_for('parametres.parametres'))  # Redirection vers la liste des utilisateurs