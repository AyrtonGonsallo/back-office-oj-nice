import os

import requests
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, flash, url_for, redirect, session, request
from form import MyForm
from form_add_user import FormAddUser
from form_edit_user import FormEditUser
from form_recuperation import FormRecuperation

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Requis pour les formulaires CSRF
bootstrap = Bootstrap5(app)
API_BASE_URL = os.getenv('API_BASE_URL')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_type = request.form.get('form_name')
    form = MyForm()
    formRecuperation = FormRecuperation()

    if form_type == 'connexion' and form.validate_on_submit():
        # traitement ici
        identifiant = form.identifiant.data
        mot_de_passe = form.mot_de_passe.data
        try:
            response = requests.post(
                f'{API_BASE_URL}/api/auth/login',
                headers={'Content-Type': 'application/json'},
                json={
                    'email': identifiant,
                    'password': mot_de_passe
                }
            )
            if response.status_code == 200:
                data = response.json()
                nom = data.get('nom')
                prenom = data.get('prenom')
                role = data.get('role')
                session['user'] = data
                print(f"Bienvenue {prenom} {nom} ({role})")
                return redirect(url_for('home'))
            else:
                flash('Connexion échouée : identifiants invalides ou serveur indisponible', 'danger')

        except requests.exceptions.RequestException as e:
            flash(f"Erreur de connexion : {str(e)}", 'danger')
    if form_type == 'recuperation' and formRecuperation.validate_on_submit():
        # traitement ici
        identifiant2 = formRecuperation.identifiant2.data
        try:
            response = requests.post(
                f'{API_BASE_URL}/api/auth/recuperer_utilisateur',
                headers={'Content-Type': 'application/json'},
                json={
                    'email': identifiant2
                }
            )
            if response.status_code == 200:
                flash(f"Récupération réussie. Consultez votre adresse {identifiant2}","success")
                return redirect(url_for('login'))
            else:
                flash('Connexion échouée : identifiants invalides ou serveur indisponible', 'danger')

        except requests.exceptions.RequestException as e:
            flash(f"Erreur de connexion : {str(e)}", 'danger')
    return render_template('index.html', form=form,formRecuperation=formRecuperation)


@app.route('/logout')
def logout():
    session.clear()  # ou session.pop('user', None)
    return redirect(url_for('login'))  # ou vers la page d'accueil

@app.route('/', methods=['GET', 'POST'])
def first_contact():
    return redirect(url_for('login'))
@app.route('/home', methods=['GET', 'POST'])
def home():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('home.html', user=user)

@app.route('/liste_des_comptes', methods=['GET', 'POST'])
def liste_des_comptes():
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
        response = requests.get(f'{API_BASE_URL}/api/auth/utilisateurs')
        response.raise_for_status()
        utilisateurs = response.json()

        # Filtrage (recherche sur nom ou prénom)
        if search:
            utilisateurs = [u for u in utilisateurs if
                            search.lower() in u['nom'].lower() or search.lower() in u['prenom'].lower() or search.lower() in u['email'].lower() or search.lower() in u['Role']['titre'].lower()]

        # Tri
        utilisateurs = sorted(
            utilisateurs,
            key=lambda x: x['Role']['titre'] if sort == 'role' else x.get(sort, ''),
            reverse=(direction == 'desc')
        )

        # Pagination manuelle
        total = len(utilisateurs)
        start = (page - 1) * per_page
        end = start + per_page
        utilisateurs_page = utilisateurs[start:end]

        # Pour le template
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
        }

        return render_template(
            'liste_des_comptes.html',
            utilisateurs=utilisateurs_page,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
            user=user
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"


@app.route('/ajouter_utilisateur', methods=['GET', 'POST'])
def ajouter_utilisateur():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    form = FormAddUser()
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/roles')
        response.raise_for_status()
        roles = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        roles = []

        # Remplir les choices dynamiquement
    form.role.choices = [(str(role['id']), role['titre']) for role in roles]

    if form.validate_on_submit():
        # Traiter les données du formulaire ici
        nom = form.nom.data
        prenom = form.prenom.data
        email = form.email.data
        mot_de_passe = form.mot_de_passe.data
        role_id = form.role.data
        # envoyer post a http://localhost:3000/api/auth/add_user
        payload = {
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'password': mot_de_passe,
            'roleId': role_id
        }
        data=None

        try:
            response = requests.post(
                f'{API_BASE_URL}/api/auth/add_user',
                json=payload,
                timeout=5  # optionnel, éviter attente infinie
            )
            data = response.json()
            response.raise_for_status()  # Lève une erreur si code >=400
            flash(f'Le compte de {prenom} {nom} a été bien été créé et un message avec les identifiants et le lien de téléchargement de l\'application a été envoyé à l\'adresse {email}.', 'success')
            return redirect(url_for('liste_des_comptes'))
        except requests.RequestException as e:
            print(data)
            flash(f'Erreur lors de la création de l’utilisateur : {data["message"]}', 'danger')
    return render_template('ajouter_utilisateur.html',user=user,form=form)

@app.route('/modifier_utilisateur/<int:user_id>', methods=['GET', 'POST'])
def modifier_utilisateur(user_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    form2 = FormEditUser()

    # Récupération des rôles pour le champ select
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/roles')
        response.raise_for_status()
        roles = response.json()
    except requests.RequestException:
        roles = []

    form2.role.choices = [(str(role['id']), role['titre']) for role in roles]

    # Récupération de l'utilisateur à modifier
    try:
        response = requests.get(f'{API_BASE_URL}/api/auth/get_user/{user_id}')
        response.raise_for_status()
        utilisateur = response.json()
        print(utilisateur)
    except requests.RequestException as e:
        print("Erreur requête API:", e)
        utilisateur = None
        flash("Impossible de charger l'utilisateur.", "danger")
        return redirect(url_for('dashboard'))  # ou autre page d'erreur

    # Remplir le formulaire avec les données existantes uniquement en GET
    if request.method == 'GET':
        form_data = {
            'nom': utilisateur.get('nom', ''),
            'prenom': utilisateur.get('prenom', ''),
            'email': utilisateur.get('email', ''),
            'role': utilisateur.get('Role', {}).get('id', None)
        }
        form2.process(data=form_data)

    # Soumission du formulaire
    if form2.validate_on_submit():
        payload = {
            'nom': form2.nom.data,
            'prenom': form2.prenom.data,
            'email': form2.email.data,
            'roleId': form2.role.data
        }

        try:
            response = requests.put(
                f'{API_BASE_URL}/api/auth/edit_user/{user_id}',
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            flash('Utilisateur modifié avec succès !', 'success')
            return redirect(url_for('liste_des_comptes'))  # ou autre page
        except requests.RequestException as e:
            flash(f'Erreur lors de la modification de l’utilisateur : {e}', 'danger')
    else:
        if request.method == 'POST':
            print(form2.errors)
            flash("Le formulaire contient des erreurs.", "warning")

    return render_template('modifier_utilisateur.html', user=user, form2=form2)


@app.route('/supprimer_utilisateur/<int:user_id>', methods=['GET'])
def supprimer_utilisateur(user_id):
    try:
        response = requests.delete(
            f'{API_BASE_URL}/api/auth/delete_user/{user_id}',
            timeout=5
        )
        response.raise_for_status()
        flash('Utilisateur supprimé avec succès !', 'success')
    except requests.RequestException as e:
        flash(f'Erreur lors de la suppression de l’utilisateur : {e}', 'danger')

    return redirect(url_for('liste_des_comptes'))  # Redirection vers la liste des utilisateurs


if __name__ == '__main__':
    app.run(debug=True)