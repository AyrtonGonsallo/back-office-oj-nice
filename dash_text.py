import os

import requests
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, url_for, redirect, session


from routes import auth_routes, gestion_des_comptes_routes, dojos_routes, cours_routes, professeurs_routes, \
    adherents_routes, appel_routes, qrcode_routes

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
    response = requests.get(f'{API_BASE_URL}/api/statistiques/presence_semaine_travail')
    response.raise_for_status()
    presence_semaine_travail = response.json()
    response = requests.get(f'{API_BASE_URL}/api/statistiques/presence_par_dojo')
    response.raise_for_status()
    presence_par_dojo = response.json()

    return render_template('tableau_de_bord.html', user=user,appels_consecutifs=appels,presence_par_dojo=presence_par_dojo,presence_semaine_travail=presence_semaine_travail)


@app.route('/adherents', methods=['GET', 'POST'])
def adherents():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('adherents.html', user=user)



@app.route('/parametres', methods=['GET', 'POST'])
def parametres():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('parametres.html', user=user)


@app.errorhandler(500)
def internal_error(error):
    import traceback
    print("ERREUR 500 :", traceback.format_exc())
    return render_template("500.html", error=error), 500


if __name__ == '__main__':
    app.run(debug=True, port=5500)
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True