from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os
from forms.form_add_user import FormAddUser
from forms.form_edit_user import FormEditUser

bp = Blueprint('professeurs', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')



@bp.route('/professeurs', methods=['GET', 'POST'])
def professeurs():
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
        response = requests.get(f'{API_BASE_URL}/api/professeurs/get_professeurs')
        response.raise_for_status()
        professeurs = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search:
            professeurs = [u for u in professeurs if
                            search.lower() in u['nom'].lower() or search.lower() in u['prenom'].lower() or search.lower() in u['email'].lower() or search.lower() in u['Role']['titre'].lower()]

        # Tri
        professeurs = sorted(
            professeurs,
            key=lambda x: x['Role']['titre'] if sort == 'role' else x.get(sort, ''),
            reverse=(direction == 'desc')
        )

        # Pagination manuelle
        total = len(professeurs)
        start = (page - 1) * per_page
        end = start + per_page
        professeurs_page = professeurs[start:end]

        # Pour le template
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
        }

        return render_template(
            'professeurs.html',
            professeurs=professeurs_page,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
            user=user
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"

