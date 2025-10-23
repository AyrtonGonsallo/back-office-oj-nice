import platform

from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os
from datetime import datetime
import locale
from math import ceil
bp = Blueprint('historique', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')


try:
    if platform.system() == 'Windows':
        # Locale Windows
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
    else:
        # Locale Linux / serveur
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    print("Impossible de définir la locale, on reste sur la locale par défaut")



@bp.route('/historique_des_emails', methods=['GET', 'POST'])
def historique_des_emails():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    # Récupérer les paramètres GET
    search = request.args.get('search_emails', '').lower()
    sort = request.args.get('sort_emails', 'dateEnvoi')  # tri par défaut
    direction = request.args.get('direction_emails', 'desc')
    page = int(request.args.get('page', 1))
    per_page = 10  # nombre d'emails par page

    # Récupérer les données depuis l'API
    response = requests.get(f'{API_BASE_URL}/api/historique/historique_des_emails')
    response.raise_for_status()
    historique_des_emails = response.json().get("data", [])

    # 1. Filtrer par recherche (objet ou destinataire)
    if search:
        historique_des_emails = [
            e for e in historique_des_emails
            if search in e['objet'].lower() or search in e['adherentNom'].lower() or search in e['adherentEmail'].lower()
        ]

    # 2. Trier
    reverse = direction == 'desc'
    try:
        historique_des_emails.sort(key=lambda x: x.get(sort, ''), reverse=reverse)
    except KeyError:
        pass  # si la clé n'existe pas, on ignore

    # 3. Pagination
    total_items = len(historique_des_emails)
    total_pages = ceil(total_items / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    historique_page = historique_des_emails[start:end]

    # Pagination info à passer au template
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_items,
        'pages': total_pages
    }

    return render_template(
        'historique_emails.html',
        user=user,
        historique_des_emails=historique_page,
        search_emails=search,
        sort_emails=sort,
        direction_emails=direction,
        pagination=pagination
    )

@bp.app_template_filter('datetimeformat')
def datetimeformat(value, format='%d %B %Y'):
    date_obj = datetime.fromisoformat(value)
    return date_obj.strftime(format)