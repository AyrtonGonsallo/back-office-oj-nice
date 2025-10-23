import os

import requests
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, url_for, redirect, session


from routes import auth_routes, gestion_des_comptes_routes, dojos_routes, cours_routes, professeurs_routes, \
    adherents_routes, appel_routes, qrcode_routes, presences_routes, historique_emails_routes, parametres_routes

app = Flask(__name__)
app.secret_key = 'super-seecret-key'  # Requis pour les formulaires CSRF
bootstrap = Bootstrap5(app)
API_BASE_URL = os.getenv('API_BASE_URL')

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
        return redirect(url_for('auth.login'))
    return render_template('adherents.html', user=user)





@app.errorhandler(500)
def internal_error(error):
    import traceback
    print("ERREUR 500 :", traceback.format_exc())
    return render_template("500.html", error=error), 500


if __name__ == '__main__':
    app.run(debug=True, port=5500)
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True