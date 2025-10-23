from datetime import datetime
from flask import Blueprint, render_template, flash, url_for, redirect, session, request
import requests
import os
import base64
from io import BytesIO
import qrcode
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A6, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from flask import send_file

from forms.form_add_adherent import FormAddAdherent
from forms.form_edit_adherent import FormEditAdherent

bp = Blueprint('qrcode', __name__, )

API_BASE_URL = os.getenv('API_BASE_URL')

# Configuration statique (modifiable une fois)
DOSSIER_CARTES = "static/cartes/"
LOGO_PATH = "static/images/logo_white.png"
SAISON = "2025-2026"


def generer_carte_adherent(adherent_id):
    """
    Récupère les infos d'un adhérent via l'API et génère sa carte PDF.
    Le champ 'qrcode' doit être une image encodée en base64.
    """
    # --- 1️⃣ Récupérer les infos de l'adhérent depuis l'API
    try:
        response = requests.get(f'{API_BASE_URL}/api/adherents/get_adherent/{adherent_id}')
        response.raise_for_status()
        adherent = response.json()
    except Exception as e:
        print(f"❌ Erreur récupération API pour l'adhérent {adherent_id} : {e}")
        return None

    qrcode_base64 = adherent.get("qrcode")
    if not qrcode_base64:
        print(f"⚠️ Aucun QR code trouvé pour {adherent['nom']} {adherent['prenom']}")
        return None

    # --- 3️⃣ Décodage QR code
    try:
        qrcode_bytes = base64.b64decode(qrcode_base64)
        qrcode_image = ImageReader(io.BytesIO(qrcode_bytes))
    except Exception as e:
        print(f"❌ Erreur décodage QR code base64 : {e}")
        return None

    # --- 4️⃣ Dossier sortie
    os.makedirs(DOSSIER_CARTES, exist_ok=True)

    # --- 5️⃣ Création PDF
    nom_pdf = f"carte_{adherent['id']}.pdf"
    output_path = os.path.join(DOSSIER_CARTES, nom_pdf)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A6))
    width, height = landscape(A6)

    # --- Bande bleue (fine)
    pdf.setFillColor(colors.HexColor("#007BFF"))
    pdf.rect(0, 25, width, 6, fill=1, stroke=0)

    # --- Bande noire (footer)
    pdf.setFillColor(colors.black)
    pdf.rect(0, 0, width, 25, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawCentredString(width / 2, 8, "Cette carte est strictement personelle. En cas de perte, merci de nous le signaler dans les meilleurs délais.")

    # --- En-tête (gauche)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(colors.black)
    pdf.drawString(20, height - 45, f"SAISON {SAISON}")

    pdf.setFont("Helvetica", 16)
    pdf.drawString(20, height - 65, adherent['Dojo']['nom'])

    # --- Logo (droite)
    try:
        logo = ImageReader(LOGO_PATH)
        # Ajustement position pour être bien visible
        pdf.drawImage(logo, width - 130, height - 85, width=120, height=70,
                      preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"⚠️ Erreur chargement logo : {e}")

    # --- QR code centré
    qr_size = 130  # un peu plus grand
    pdf.drawImage(qrcode_image,
                  (width - qr_size) / 2,
                  (height - qr_size) / 2 - 10,  # recentré légèrement
                  width=qr_size, height=qr_size,
                  preserveAspectRatio=True, mask='auto')

    # --- Nom / Prénom centré (en dessous du QR)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(width / 2, (height / 2) - qr_size / 2 - 25, f"{adherent['prenom']} {adherent['nom']}")

    # --- Finalisation
    pdf.save()
    buffer.seek(0)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())

    print(f"✅ Carte générée : {output_path}")
    try:
        fichier_data = {
            "nom": os.path.basename(output_path),
            "type": "carte_membre",
            "adherent_id": adherent["id"]
        }
        response = requests.post(f"{API_BASE_URL}/api/fichiers/add_file", json=fichier_data)
        if response.status_code == 201:
            print("📁 Fichier enregistré avec succès dans la base.")
        else:
            print(f"⚠️ Échec de l'enregistrement du fichier : {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur d'enregistrement fichier : {e}")

    return output_path

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
            goal = request.form.get('goal')
            if goal == 'generation_qrcode':
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


            elif goal == 'generation_carte':
                ids_str = request.form.get('ids')  # ex: "5,7,12"
                if not ids_str:
                    flash("Aucun ID reçu", 'danger')
                    return redirect(url_for('generation_qrcode'))

                ids = [int(i) for i in ids_str.split(',')]
                adherents_choisis = [a for a in adherents if a['id'] in ids]
                cartes_generees = 0
                for adherent_id in ids:
                    if generer_carte_adherent(adherent_id):
                        cartes_generees += 1

                flash(f"{cartes_generees} carte(s) générée(s) dans {DOSSIER_CARTES}", 'success')

                print(f"adherents_choisis: {len(adherents_choisis)}")
                flash("Cartes générées pour : " + ", ".join((a['nom'] + ' ' + a['prenom']) for a in adherents_choisis),
                      'success')



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