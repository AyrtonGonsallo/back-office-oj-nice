import platform

from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os
from datetime import datetime
import locale
bp = Blueprint('presences', __name__, )

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



@bp.route('/presences_par_semaines', methods=['GET', 'POST'])
def presences_par_semaines():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    response = requests.get(f'{API_BASE_URL}/api/statistiques/group_semaine_travail')
    response.raise_for_status()
    group_semaine_travail_appels = response.json()
    return render_template('presences_par_semaines.html', user=user,group_semaine_travail_appels=group_semaine_travail_appels)

@bp.app_template_filter('datetimeformat')
def datetimeformat(value, format='%d %B %Y'):
    date_obj = datetime.fromisoformat(value)
    return date_obj.strftime(format)