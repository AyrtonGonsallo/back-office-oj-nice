import os
import sys
import requests
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, flash, url_for, redirect, session, request
from forms.form import MyForm
from forms.form_add_user import FormAddUser
from forms.form_edit_user import FormEditUser
from forms.form_recuperation import FormRecuperation
from dotenv import load_dotenv
from routes import auth_routes, gestion_des_comptes_routes, dojos_routes, cours_routes, professeurs_routes, \
    adherents_routes, appel_routes, qrcode_routes, presences_routes, historique_emails_routes, parametres_routes


sys.path.insert(0, os.path.dirname(__file__))
load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')

app = Flask(__name__, )

app.secret_key = 'fdsfref'
bootstrap = Bootstrap5(app)






app.register_blueprint(auth_routes.bp)
app.register_blueprint(gestion_des_comptes_routes.bp)
app.register_blueprint(appel_routes.bp)
app.register_blueprint(qrcode_routes.bp)
app.register_blueprint(dojos_routes.bp)
app.register_blueprint(cours_routes.bp)
app.register_blueprint(parametres_routes.bp)
app.register_blueprint(presences_routes.bp)
app.register_blueprint(historique_emails_routes.bp)
app.register_blueprint(professeurs_routes.bp)
app.register_blueprint(adherents_routes.bp)





@app.route('/tableau_de_bord', methods=['GET', 'POST'])
def tableau_de_bord():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    response = requests.get(f'{API_BASE_URL}/api/statistiques/get_absences_consecutives')
    response.raise_for_status()
    appels = response.json()
    appels_consecutifs_sorted = sorted(
        appels,
        key=lambda x: x['adherent']['nom'].lower() if x.get('adherent') else ""
    )
    response = requests.get(f'{API_BASE_URL}/api/statistiques/presence_semaine_travail')
    response.raise_for_status()
    presence_semaine_travail = response.json() or {}

    # Valeurs par défaut si null ou absentes
    presences_total = presence_semaine_travail.get("presencesTotal") or 0
    judokas_total = presence_semaine_travail.get("judokasDistinctsTotal") or 0

    if judokas_total > 0:
        presence_semaine_travail["presences_par_judokas"] = round(
            presences_total / judokas_total, 1
        )
    else:
        presence_semaine_travail["presences_par_judokas"] = 0

    # Deuxième appel API
    response = requests.get(f"{API_BASE_URL}/api/statistiques/presence_par_dojo")
    response.raise_for_status()
    presence_par_dojo = response.json() or []

    # Trier en gérant les valeurs nulles
    presence_par_dojo_sorted = sorted(
        presence_par_dojo,
        key=lambda x: (x.get("dojoName") or "").lower()
    )

    return render_template('tableau_de_bord.html', user=user, appels_consecutifs=appels_consecutifs_sorted,
                           presence_par_dojo=presence_par_dojo_sorted,
                           presence_semaine_travail=presence_semaine_travail)


@app.route('/adherents', methods=['GET', 'POST'])
def adherents():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('adherents.html', user=user)




application = app





"""
sys.path.insert(0, os.path.dirname(__file__))


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    message = 'It works!\n'
    version = 'Python %s\n' % sys.version.split()[0]
    response = '\n'.join([message, version])
    return [response.encode()]


if __name__ == '__main__':
    app.run(debug=True)

"""