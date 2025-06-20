import os

from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, url_for, redirect, session
from routes import auth_routes, gestion_des_comptes_routes, dojos_routes, cours_routes

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Requis pour les formulaires CSRF
bootstrap = Bootstrap5(app)
API_BASE_URL = os.getenv('API_BASE_URL')

app.register_blueprint(auth_routes.bp)
app.register_blueprint(gestion_des_comptes_routes.bp)
app.register_blueprint(dojos_routes.bp)
app.register_blueprint(cours_routes.bp)


@app.route('/tableau_de_bord', methods=['GET', 'POST'])
def tableau_de_bord():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('tableau_de_bord.html', user=user)


@app.route('/adherents', methods=['GET', 'POST'])
def adherents():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('adherents.html', user=user)



@app.route('/parametres', methods=['GET', 'POST'])
def parametres():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('parametres.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)