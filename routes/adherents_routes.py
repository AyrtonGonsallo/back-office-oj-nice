from datetime import datetime
from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os

from forms.form_add_adherent import FormAddAdherent
from forms.form_edit_adherent import FormEditAdherent

bp = Blueprint('adherents', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')



@bp.route('/adherents', methods=['GET', 'POST'])
def adherents():
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
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_adherents')
        response.raise_for_status()
        adherents = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search:
            adherents = [c for c in adherents if
                            search.lower() in c['nom'].lower() or search.lower() in c['prenom'].lower() ]

        # Tri
        adherents = sorted(
            adherents,
            key=lambda x: x['Dojo']['nom'] if sort == 'Dojo' else x.get(sort, ''),
            reverse=(direction == 'desc')
        )

        # Pagination manuelle
        total = len(adherents)
        start = (page - 1) * per_page
        end = start + per_page
        adherents_page = adherents[start:end]

        # Pour le template
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
        }

        return render_template(
            'adherents.html',
            adherents=adherents_page,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
            user=user
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"




@bp.route('/liste_des_appels_par_cours/<int:cours_id>', methods=['GET', 'POST'])
def liste_des_appels_par_cours(cours_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    # Paramètres de recherche et tri
    search_adherents = request.args.get('search_adherents', '')
    sort_adherents = request.args.get('sort_adherents', 'id')
    direction_adherents = request.args.get('direction_adherents', 'desc')
    page_adherents = int(request.args.get('page_adherents', 1))
    per_page_adherents = 10

    # Paramètres de recherche et tri
    search_appels = request.args.get('search_appels', '')
    sort_appels = request.args.get('sort_appels', 'date')
    direction_appels = request.args.get('direction_appels', 'desc')
    page_appels = int(request.args.get('page_appels', 1))
    per_page_appels = 10

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



    try:
        response = requests.get(f'{API_BASE_URL}/api/adherents/adherents_by_cours/{cours_id}')
        response.raise_for_status()
        adherents = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search_adherents:
            adherents = [c for c in adherents if
                            search_adherents.lower() in c['nom'].lower() or search_adherents.lower() in c['prenom'].lower() ]

        # Tri
        adherents = sorted(
            adherents,
            key=lambda x:  x.get(sort_adherents, ''),
            reverse=(direction_adherents == 'desc')
        )

        # Pagination manuelle
        total_adherents = len(adherents)
        start_adherents = (page_adherents - 1) * per_page_adherents
        end_adherents = start_adherents + per_page_adherents
        adherents_page = adherents[start_adherents:end_adherents]

        # Pour le template
        pagination_adherents = {
            'page': page_adherents,
            'per_page': per_page_adherents,
            'total_adherents': total_adherents,
            'pages_adherents': (total_adherents + per_page_adherents - 1) // per_page_adherents,
        }

        response = requests.get(f'{API_BASE_URL}/api/adherents/get_distincts_appel_dates_by_cours/{cours_id}')
        response.raise_for_status()
        distincts_appel_dates_by_cours = response.json()
        selected_appel_date = request.args.get('date')
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_appels_by_cours/{cours_id}')
        response.raise_for_status()
        appels = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search_appels or selected_appel_date:
            appels = [
                c for c in appels
                if (not search_appels or search_appels.lower() in c['nom'].lower() or search_appels.lower() in c[
                    'prenom'].lower())
                   and (not selected_appel_date or c['date'] == selected_appel_date)
            ]

        # Tri
        appels = sorted(
            appels,
            key=lambda x: (
                x['Adherent']['nom'].lower() if sort_appels == 'Adherent' and 'Adherent' in x else
                x['Cour']['jour'] if sort_appels == 'Cour' and 'Cour' in x else
                x.get(sort_appels, '')
            ),
            reverse=(direction_appels == 'desc')
        )

        # Pagination manuelle
        total_appels = len(appels)
        start_appels = (page_appels - 1) * per_page_appels
        end_appels = start_appels + per_page_appels
        appels_page = appels[start_appels:end_appels]

        # Pour le template
        pagination_appels = {
            'page': page_appels,
            'per_page': per_page_appels,
            'total_appels': total_appels,
            'pages_appels': (total_appels + per_page_appels - 1) // per_page_appels,
        }




        return render_template(
            'liste_des_appels.html',
            adherents=adherents_page,
            pagination_adherents=pagination_adherents,
            search_adherents=search_adherents,
            sort_adherents=sort_adherents,
            direction_adherents=direction_adherents,
            appels=appels_page,
            pagination_appels=pagination_appels,
            search_appels=search_appels,
            sort_appels=sort_appels,
            direction_appels=direction_appels,
            user=user,
            cours=cours,
            selected_appel_date=selected_appel_date,
            distincts_appel_dates_by_cours=distincts_appel_dates_by_cours
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"




@bp.route('/liste_des_appels_par_cours_et_date/<int:cours_id>/<date>', methods=['GET', 'POST'])
def liste_des_appels_par_cours_et_date(cours_id,date):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))



    # Paramètres de recherche et tri
    search_appels = request.args.get('search_appels', '')
    sort_appels = request.args.get('sort_appels', 'date')
    direction_appels = request.args.get('direction_appels', 'desc')
    page_appels = int(request.args.get('page_appels', 1))
    per_page_appels = 10

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



    try:
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_appels_by_cours_and_date/{cours_id}/{date}')
        response.raise_for_status()
        appels = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search_appels :
            appels = [
                c for c in appels
                if (not search_appels or search_appels.lower() in c['nom'].lower() or search_appels.lower() in c[
                    'prenom'].lower())
            ]

        # Tri
        appels = sorted(
            appels,
            key=lambda x: (
                x['Adherent']['nom'].lower() if sort_appels == 'Adherent' and 'Adherent' in x else
                x['Cour']['jour'] if sort_appels == 'Cour' and 'Cour' in x else
                x.get(sort_appels, '')
            ),
            reverse=(direction_appels == 'desc')
        )

        # Pagination manuelle
        total_appels = len(appels)
        start_appels = (page_appels - 1) * per_page_appels
        end_appels = start_appels + per_page_appels
        appels_page = appels[start_appels:end_appels]

        # Pour le template
        pagination_appels = {
            'page': page_appels,
            'per_page': per_page_appels,
            'total_appels': total_appels,
            'pages_appels': (total_appels + per_page_appels - 1) // per_page_appels,
        }




        return render_template(
            'liste_des_appels_detaillee.html',

            appels=appels_page,
            pagination_appels=pagination_appels,
            search_appels=search_appels,
            sort_appels=sort_appels,
            direction_appels=direction_appels,
            user=user,
            cours=cours,
            date=date

        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"



@bp.route('/ajouter_adherent', methods=['GET', 'POST'])
def ajouter_adherent():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    form = FormAddAdherent()
    try:
        response  = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_all_cours')
        response.raise_for_status()
        cours = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        cours = []

        # Remplir les choices dynamiquement
    form.coursId.choices = [(str(c['id']), c['jour']+' '+c['heure'][0:5]) for c in cours]


    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_dojos')
        response.raise_for_status()
        dojos = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        dojos = []

    form.dojoId.choices = [(str(c['id']), c['nom']) for c in dojos]

    if form.validate_on_submit():
        # Traiter les données du formulaire ici
        nom = form.nom.data
        prenom = form.prenom.data
        email = form.email.data
        telephone = form.telephone.data
        dojoId = form.dojoId.data
        date_inscription = form.date_inscription.data.strftime('%Y-%m-%d')  # ✅ Date complète (YYYY-MM-DD)
        cours_ids = form.coursId.data  # ✅ Liste d'IDs (SelectMultipleField)
        categorie_age = form.categorie_age.data  # ✅ Peut être une liste ou une chaîne selon ton form

        # Construction du payload pour l'API backend Node.js
        payload = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'date_inscription': date_inscription,
            'dojoId': dojoId,
            'coursIds': cours_ids,
            'categorie_age': categorie_age,
            # 'dojoId': ...  # à inclure si présent dans le formulaire
        }
        data=None

        try:
            response = requests.post(
                f'{API_BASE_URL}/api/adherents/add_adherent',
                json=payload,
                timeout=5  # optionnel, éviter attente infinie
            )
            data = response.json()
            response.raise_for_status()  # Lève une erreur si code >=400
            flash(f'L\'adhérent {prenom} {nom} a été bien été créé.', 'success')
            return redirect(url_for('adherents.adherents'))
        except requests.RequestException as e:
            print(data)
            flash(f'Erreur lors de la création de l’adherent : {data["message"]}', 'danger')
    else:
        if request.method == 'POST':
            print(form.errors)
            flash("Certains champs n'ont pas été remplis ou sont invalides.", "warning")

    return render_template('ajouter_adherent.html',user=user,form=form)





@bp.route('/modifier_adherent/<int:adherent_id>', methods=['GET', 'POST'])
def modifier_adherent(adherent_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    form = FormEditAdherent()
    try:
        response  = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_all_cours')
        response.raise_for_status()
        cours = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        cours = []

        # Remplir les choices dynamiquement
    form.coursId.choices = [(str(c['id']), c['jour']+' '+c['heure'][0:5]) for c in cours]


    try:
        response = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_dojos')
        response.raise_for_status()
        dojos = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        dojos = []

    form.dojoId.choices = [(str(c['id']), c['nom']) for c in dojos]

    # Récupération de l' adherent à modifier
    try:
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_adherent/{adherent_id}')
        response.raise_for_status()
        adherent = response.json()
        print(adherent)
    except requests.RequestException as e:
        print("Erreur requête API:", e)
        adherent = None
        flash("Impossible de charger l'adherent.", "danger")
        return redirect(url_for('adherents.adherents'))  # ou autre page d'erreur


    # Remplir le formulaire avec les données existantes (GET)
    if request.method == 'GET' and adherent:
        date_str = adherent.get('date_inscription')
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date_obj = None
        form_data = {
            'nom': adherent.get('nom', ''),
            'prenom': adherent.get('prenom', ''),
            'email': adherent.get('email', ''),
            'telephone': adherent.get('telephone', ''),
            'dojoId': adherent.get('dojoId'),
            'date_inscription': date_obj,  # format YYYY-MM-DD accepté
            'coursId': [cours['id'] for cours in adherent.get('Cours', [])],
            'categorie_age': adherent.get('categorie_age')
        }
        form.process(data=form_data)




    if form.validate_on_submit():
        # Traiter les données du formulaire ici
        nom = form.nom.data
        prenom = form.prenom.data
        email = form.email.data
        telephone = form.telephone.data
        dojoId = form.dojoId.data
        date_inscription = form.date_inscription.data.strftime('%Y-%m-%d')  # ✅ Date complète (YYYY-MM-DD)
        cours_ids = form.coursId.data  # ✅ Liste d'IDs (SelectMultipleField)
        categorie_age = form.categorie_age.data  # ✅ Peut être une liste ou une chaîne selon ton form

        # Construction du payload pour l'API backend Node.js
        payload = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'date_inscription': date_inscription,
            'dojoId': dojoId,
            'coursIds': cours_ids,
            'categorie_age': categorie_age,
        }
        data=None

        try:
            response = requests.put(
                f'{API_BASE_URL}/api/adherents/edit_adherent/{adherent_id}',
                json=payload,
                timeout=5  # optionnel, éviter attente infinie
            )
            data = response.json()
            response.raise_for_status()  # Lève une erreur si code >=400
            flash(f'L\'adhérent {prenom} {nom} a été bien été modifié.', 'success')
            return redirect(url_for('adherents.adherents'))
        except requests.RequestException as e:
            print(data)
            flash(f'Erreur lors de la modification de l’adherent : {data["message"]}', 'danger')
    else:
        if request.method == 'POST':
            print(form.errors)
            flash("Certains champs n'ont pas été remplis ou sont invalides.", "warning")

    return render_template('modifier_adherent.html',user=user,form=form)




@bp.route('/supprimer_adherent/<int:adherent_id>', methods=['GET'])
def supprimer_adherent(adherent_id):
    try:
        response = requests.delete(
            f'{API_BASE_URL}/api/adherents/delete_adherent/{adherent_id}',
            timeout=5
        )
        response.raise_for_status()
        flash('adherent supprimé avec succès !', 'success')
    except requests.RequestException as e:
        flash(f'Erreur lors de la suppression de l\'adherent : {e}', 'danger')

    return redirect(url_for('adherents.adherents'))  # Redirection vers la liste des cours




@bp.route('/fiche_adherent/<int:adherent_id>', methods=['GET', 'POST'])
def fiche_adherent(adherent_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    # Paramètres de recherche et tri
    search_appels = request.args.get('search_appels', '')
    sort_appels = request.args.get('sort_appels', 'date')
    direction_appels = request.args.get('direction_appels', 'desc')
    page_appels = int(request.args.get('page_appels', 1))
    per_page_appels = 10

    # Récupération de l' adherent à modifier
    try:
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_adherent/{adherent_id}')
        response.raise_for_status()
        adherent = response.json()
        print(adherent)
    except requests.RequestException as e:
        print("Erreur requête API:", e)
        adherent = None
        flash("Impossible de charger l'adherent.", "danger")
        return redirect(url_for('adherents.adherents'))  # ou autre page d'erreur

    response = requests.get(f'{API_BASE_URL}/api/adherents/get_appels_by_adherent/{adherent_id}')
    response.raise_for_status()
    appels = response.json()

    # Filtrage (recherche sur nom ou prénom)
    if search_appels:
        appels = [c for c in appels if
                  search_appels.lower() in c['nom'].lower() or search_appels.lower() in c[
                      'prenom'].lower()]

    # Tri
    appels = sorted(
        appels,
        key=lambda x: (
            x['Adherent']['nom'].lower() if sort_appels == 'Adherent' and 'Adherent' in x else
            x['Cour']['jour'] if sort_appels == 'Cour' and 'Cour' in x else
            x.get(sort_appels, '')
        ),
        reverse=(direction_appels == 'desc')
    )

    # Pagination manuelle
    total_appels = len(appels)
    start_appels = (page_appels - 1) * per_page_appels
    end_appels = start_appels + per_page_appels
    appels_page = appels[start_appels:end_appels]

    # Pour le template
    pagination_appels = {
        'page': page_appels,
        'per_page': per_page_appels,
        'total_appels': total_appels,
        'pages_appels': (total_appels + per_page_appels - 1) // per_page_appels,
    }




    return render_template('fiche_adherent.html',user=user,adherent=adherent,appels=appels_page,
        pagination_appels=pagination_appels,
        search_appels=search_appels,
        sort_appels=sort_appels,
        direction_appels=direction_appels,)