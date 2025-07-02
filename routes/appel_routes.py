from datetime import datetime
from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os

from forms.form_add_adherent import FormAddAdherent
from forms.form_add_appel import FormAddAppel
from forms.form_edit_adherent import FormEditAdherent

bp = Blueprint('appels', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')





@bp.route('/ajouter_appel', methods=['GET', 'POST'])
def ajouter_appel():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))
    form = FormAddAppel()
    try:
        response  = requests.get(f'{API_BASE_URL}/api/dojo_cours/get_all_cours')
        response.raise_for_status()
        cours = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        cours = []

        # Remplir les choices dynamiquement
    form.coursId.choices = [(str(c['id']), c['jour']+' '+c['heure']) for c in cours]


    try:
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_adherents')
        response.raise_for_status()
        adherents = response.json()  # liste d'objets {id:..., nom:...}
    except requests.RequestException:
        adherents = []

    form.adherentId.choices = [(str(ad['id']), ad['nom']+' '+ad['prenom']) for ad in adherents]

    if form.validate_on_submit():
        # Traiter les données du formulaire ici

        coursId = form.coursId.data
        date = form.date.data.strftime('%Y-%m-%d')  # ✅ Date complète (YYYY-MM-DD)
        adherentId = form.adherentId.data  # ✅ Liste d'IDs (SelectMultipleField)
        status = form.status.data  # ✅ Peut être une liste ou une chaîne selon ton form

        # Construction du payload pour l'API backend Node.js
        payload = {
            'date': date,
            'coursId': coursId,
            'adherentId': adherentId,
            'status': status,
            # 'dojoId': ...  # à inclure si présent dans le formulaire
        }
        data=None

        try:
            response = requests.post(
                f'{API_BASE_URL}/api/adherents/add_appel',
                json=payload,
                timeout=5  # optionnel, éviter attente infinie
            )
            data = response.json()
            response.raise_for_status()  # Lève une erreur si code >=400
            flash(f'appel ajouté', 'success')
            return redirect(url_for('adherents.liste_des_appels_par_cours', cours_id=coursId))

        except requests.RequestException as e:
            print(data)
            flash(f'Erreur lors de l\'ajout de l\'appel : {data["message"]}', 'danger')
    else:
        if request.method == 'POST':
            print(form.errors)
            flash("Certains champs n'ont pas été remplis ou sont invalides.", "warning")

    return render_template('ajouter_appel.html',user=user,form=form)



@bp.route('/modifier_status_appel/<int:appel_id>/<int:cours_id>/<int:adherent_id>/<liste_des_appels_par_cours>/<date>', methods=['GET',])
def modifier_status_appel(appel_id,cours_id,adherent_id,liste_des_appels_par_cours,date):
    liste_des_appels_par_cours = True if liste_des_appels_par_cours.lower() == 'true' else False
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    try:
        # Appel PUT vers le backend pour mettre à jour l'appel
        response = requests.put(
            f'{API_BASE_URL}/api/adherents/switch_status_appel/{appel_id}',
            timeout=5
        )
        response.raise_for_status()
        flash(f'Statut de présence de l\'appel {appel_id} mis à jour avec succès.', "success")
    except requests.RequestException as e:
        print("Erreur API:", e)
        flash("Erreur lors de la mise à jour de la présence.", "danger")

    if liste_des_appels_par_cours:
        return redirect(url_for('adherents.liste_des_appels_par_cours_et_date', cours_id=cours_id,date=date))
    else:
        return redirect(url_for('adherents.fiche_adherent', adherent_id=adherent_id))


@bp.route('/supprimer_appel/<int:appel_id>/<int:cours_id>/<int:adherent_id>/<liste_des_appels_par_cours>', methods=['GET'])
def supprimer_appel(appel_id,cours_id,adherent_id,liste_des_appels_par_cours):
    liste_des_appels_par_cours = True if liste_des_appels_par_cours.lower() == 'true' else False
    try:
        response = requests.delete(
            f'{API_BASE_URL}/api/adherents/delete_appel/{appel_id}',
            timeout=5
        )
        response.raise_for_status()
        flash('appel supprimé avec succès !', 'success')
    except requests.RequestException as e:
        flash(f'Erreur lors de la suppression de l\'appel : {e}', 'danger')

    if liste_des_appels_par_cours:
        return redirect(url_for('adherents.liste_des_appels_par_cours', cours_id=cours_id))  # Redirection vers la liste des cours
    else:
        return redirect(url_for('adherents.fiche_adherent', adherent_id=adherent_id))  # Redirection vers la liste des cours

