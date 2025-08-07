from datetime import datetime
from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os
import base64
from io import BytesIO
import qrcode

from forms.form_add_adherent import FormAddAdherent
from forms.form_edit_adherent import FormEditAdherent

bp = Blueprint('qrcode', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')



@bp.route('/generation_qrcode', methods=['GET', 'POST'])
def generation_qrcode():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    # Paramètres de recherche et tri
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'id')
    direction = request.args.get('direction', 'asc')
    page = int(request.args.get('page', 1))
    per_page = 50

    try:
        # Récupération des adhérents
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_adherents')
        response.raise_for_status()
        adherents = response.json()

        # Filtrage
        if search:
            adherents = [c for c in adherents if
                         search.lower() in c['nom'].lower() or search.lower() in c['prenom'].lower()]

        # Tri
        adherents = sorted(
            adherents,
            key=lambda x: x['Dojo']['nom'] if sort == 'Dojo' else x.get(sort, ''),
            reverse=(direction == 'desc')
        )

        # Pagination
        total = len(adherents)
        start = (page - 1) * per_page
        end = start + per_page
        adherents_page = adherents[start:end]

        # Traitement du formulaire (POST uniquement)
        if request.method == 'POST':
            ids_str = request.form.get('ids')  # ex: "5,7,12"
            if not ids_str:
                flash("Aucun ID reçu", 'danger')
                return redirect(url_for('generation_qrcode'))

            ids = [int(i) for i in ids_str.split(',')]
            adherents_choisis = [a for a in adherents if a['id'] in ids]
            for adherent in adherents_choisis:
                qr_code = generer_qrcode_base64(adherent)

                requests.put(
                    f'{API_BASE_URL}/api/qrcode/{adherent["id"]}/update_qrcode',
                    json={'qrcode': qr_code}
                )
            print(f"adherents_choisis: {len(adherents_choisis)}")
            flash("QR codes générés pour : " + ", ".join((a['nom'] + ' ' + a['prenom']) for a in adherents_choisis),
                  'success')

            # ⚠️ Tu peux ici rediriger ou afficher les QR codes

        # Affichage
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
        }

        return render_template(
            'qrcode_adherents.html',
            adherents=adherents_page,
            pagination=pagination,
            search=search,
            sort=sort,
            direction=direction,
            user=user
        )

    except requests.RequestException as e:
        return f"Erreur de requête : {e}"


def generer_qrcode_base64(adherent):
    data = f"ID:{adherent['id']};Nom:{adherent['nom']};Prenom:{adherent['prenom']};Dojo:{adherent['Dojo']['nom']}"

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qrcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return qrcode_base64