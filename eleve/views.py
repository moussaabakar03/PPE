from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from datetime import datetime

from comptable.models import PaiementEleve
from secretaire.models import AlertCompteEleve, AnneeScolaire, Cout, Emargement, EmploiDuTemps, Etudiant, Evaluation, Inscription, Messages, PlageHoraire, SalleDeClasse, depotDossierEtudiant

from acadPro.utils.decorators import eleve_required




from types import SimpleNamespace

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO


import qrcode
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from django.http import HttpResponse
from django.conf import settings
from io import BytesIO
import os




# def navBarEleve(request):
#     matricule = request.session.get('matricule')  ============================
#     id = 1
#     etudiant 
#     if not matricule:
#         return redirect('connexion') 
#     return render(request, 'eleve/partial/navBar.html', {'matricule': matricule, 'id': id})



def navBarEleve(request):
    matricule = request.user
    # id = 1
    etudiant = Etudiant.objects.get(username= request.user)
    # inscrits = etudiant.inscriptions.all()
    # for inscription in inscrits:
    #     print(f" =======================================  inscription: {inscription.anneeAcademique}")
    if not matricule:
        return redirect('connexion') 
    return render(request, 'eleve/partial/navBar.html', {'etudiant': etudiant})


def header(request):
    matricule = request.session.get('matricule')
    eleveConnecter = Etudiant.objects.get(username= request.user)
    return render(request, 'eleve/partial/header.html', {'etudiant': eleveConnecter})


def compteEtudiant(request):
    etudiant = Etudiant.objects.get(username=request.user)
    inscriptions = etudiant.inscriptions.all()

    somme_notes_ponderees = 0.0
    somme_coefficients = 0
    
    if request.method == "POST":
        # moyenne = 0.0
        
        matiere = request.POST['matiere']
        trimestre = request.POST['trimestre']
        typeEvaluation = request.POST['typeEvaluation']
        
        evaluations = etudiant.evaluations.all()
        
        if matiere:
            evaluations = etudiant.evaluations.filter(cours__matiere__nom__contains = matiere.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        elif trimestre:
            evaluations = etudiant.evaluations.filter(trimestre__contains = trimestre.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        elif typeEvaluation:
            evaluations = etudiant.evaluations.filter(typeEvaluation__contains = typeEvaluation.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        elif matiere and trimestre and typeEvaluation:
            evaluations = etudiant.evaluations.filter(typeEvaluation__contains = typeEvaluation, trimestre__contains = trimestre, cours__matiere__nom__contains = matiere.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        
        moyenne = round(somme_notes_ponderees / somme_coefficients, 2) if somme_coefficients != 0 else 0.0
        
        context = {
            "etudiant": etudiant,
            "evaluations": evaluations,
            "moyenne": moyenne
            }
        return render(request, 'eleve/compteEtudiant.html', context)
        
        
    else:    
        evaluations = etudiant.evaluations.all()
        for evaluation in evaluations:
            coefficient = evaluation.cours.coefficient
            somme_notes_ponderees += float(evaluation.note) * coefficient
            somme_coefficients += coefficient

        moyenne = round(somme_notes_ponderees / somme_coefficients, 2) if somme_coefficients != 0 else 0.0

        context = {
            "etudiant": etudiant,
            "evaluations": evaluations,
            "moyenne": moyenne
        }
        return render(request, 'eleve/compteEtudiant.html', context)

def accueilEtudiant(request):
    etudiant = Etudiant.objects.get(user=request.user)
    return render(request, 'eleve/accueilEtudiant.html', {'etudiant': etudiant})

@login_required
@eleve_required
def presence(request):
    try:
        etudiant = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')
    inscrits = Inscription.objects.filter(etudiant =etudiant)
    # parent = Etudiant.objects.get(parent = etudiant.parent)
    emargements = Emargement.objects.filter(inscrits__in=inscrits).order_by('-id')
    return render(request, 'eleve/presence.html', {"etudiant": etudiant, "emargements": emargements})
    

@login_required
@eleve_required
def notes(request):
    try:
        etudiant = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')

    evaluations = None

    if request.method == "POST":
        annee = request.POST.get('annee')
        if annee:
            anneeScolaire = AnneeScolaire.objects.get(pk=int(annee))
            evaluations = Evaluation.objects.filter(
                cours__anneeScolaire=anneeScolaire,
                etudiant=etudiant
            )

    return render(
        request,
        'eleve/notes.html',
        {
            'evaluations': evaluations,
            'etudiant': etudiant,
            'annees': AnneeScolaire.objects.all().order_by('-id')
        }
    )


@login_required
@eleve_required
def inscriptionPayement(request):
    return render(request, 'eleve/inscriptionPayement.html')

@login_required
@eleve_required
def messagesEleves(request):
    try:
        etudiants = Etudiant.objects.exclude(utilisateur__username=request.user.username)
        
        etudiant = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')
    # dictionnaire {id_etudiant: dernier_message}
    derniers_messages = {}

    for etudt in etudiants:
        dernier = Messages.objects.filter(
            Q(expediteur=etudiant, destinataire=etudt) |
            Q(expediteur=etudt, destinataire=etudiant)
        ).order_by("-date_envoi").first()

        derniers_messages[etudt.id] = dernier

    context = {
        "etudiants": etudiants, 
        "etudiant": etudiant,
        "derniers_messages": derniers_messages
    }
    return render(request, 'eleve/messages.html', context)





@login_required
@eleve_required
def alert_eleve(request, id):
    eleve_exp  = get_object_or_404(Etudiant, utilisateur__username=request.user.username)
    eleve_dest = get_object_or_404(Etudiant, id=id)

    if eleve_exp == eleve_dest:
        messages.error(request, "Vous ne pouvez pas vous signaler vous-même.")
        return redirect("eleve:messagesEleves")

    if request.method == "POST":
        contenu = request.POST.get("contenu", "").strip()[:500]
        type_signalement = request.POST.get("type_signalement", "autre")
        gravite= request.POST.get("gravite", "moderee")
        # message_ref_id   = request.POST.get("message_ref_id", "")

        if type_signalement not in ["harcelement", "insulte", "menace", "contenu_inapproprie", "spam", "autre"]:
            type_signalement = "autre"
        if gravite not in ["faible", "moderee", "grave"]:
            gravite = "moderee"

        from django.utils import timezone
        from datetime import timedelta

        deja_signale = AlertCompteEleve.objects.filter(
            eleve_expedi=eleve_exp, 
            eleve_signale=eleve_dest,
            date_signalement__gte=timezone.now() - timedelta(minutes=10)
        ).exists()

        if deja_signale:
            messages.warning(request, "Vous avez déjà soumis un signalement récemment. L'administration s'en charge.")
            return redirect("eleve:echangeEleveEleve", id=eleve_dest.id)

        # Récupérer le message référencé si fourni
        # message_reference = None
        # if message_ref_id:
        #     try:
        #         message_reference = Message.objects.get(id=int(message_ref_id))
        #     except (Message.DoesNotExist, ValueError):
        #         pass

        AlertCompteEleve.objects.create(
            eleve_expedi=eleve_exp,
            eleve_signale=eleve_dest,
            contenu=contenu or "Aucune précision fournie.",
            type_signalement=type_signalement,
            gravite=gravite,
            # message_reference = message_reference,
        )

        messages.success(request, "Votre signalement a bien été transmis à l'administration. Merci de rester calme.")
        return redirect("eleve:echangeEleveEleve", id=eleve_dest.id)

    return redirect("eleve:messagesEleves")


@login_required
@eleve_required
def emploiDuTempsEtudiant(request):
    try:
        eleve = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')
    
    inscrits = eleve.inscriptions.all()
    containts = {"inscrits": inscrits, "etudiant": eleve}
    return render(request, "eleve/emploi_temps_etudiant.html", containts)

    

@login_required
@eleve_required
def affichageEmploiTemps(request, id1, id2):
    try:
        eleve = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')
    
    salle = SalleDeClasse.objects.get(id=id1)
    annee = AnneeScolaire.objects.get(id=id2)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    
      
    horaires = PlageHoraire.objects.filter(salle=salle, annee=annee).first()
        
    heures = []
    if horaires:
        for h in range(horaires.debut, horaires.fin):
            heures.append(f"{h}h- {h+1}h")
    # else:
    #     return render(request, 'emploiTemps.html', {'salle': salle, 'annee': annee, 'jours': jours, 'heures': heures})
    
    emploi_dict = {}  

    for heure in heures:
        emploi_dict[heure] = {}
        for jour in jours:
            emploi = EmploiDuTemps.objects.filter(
                salle=salle, annee=annee, heure=heure, jour=jour
            ).first()
            emploi_dict[heure][jour] = emploi

    contains = {
        'salle': salle,
        'annee': annee,
        'jours': jours,
        'heures': heures,
        # 'emploi': emploi,
        'emploi_dict': emploi_dict,
        'etudiant': eleve,
    }

    return render(request, "eleve/affichageEmploiTemps.html", contains)



from django.http import JsonResponse

@login_required
@eleve_required
def echangeEleveEleve(request, id):
    try:
        eleve = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')
    
    etudiant = get_object_or_404(Etudiant, pk=id)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        contenu_message = request.POST.get('messageEleve', '').strip()
        if contenu_message:
            message = Messages.objects.create(
                contenu=contenu_message,
                expediteur=eleve,
                destinataire=etudiant,
                est_lu=False
            )
            return JsonResponse({
                'status': 'success',
                'contenu': message.contenu,
                'heure': message.date_envoi.strftime('%H:%M:%S'),
                'id': message.id
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Message vide'}, status=400)

    # Si GET ou non AJAX
    tous_messages = Messages.objects.filter(
        Q(expediteur=eleve, destinataire=etudiant) |
        Q(expediteur=etudiant, destinataire=eleve)
    ).order_by('date_envoi')

    etudiants = Etudiant.objects.exclude(utilisateur__username=request.user.username)

    return render(request, 'eleve/echangeEleveEleve.html', {
        'etudiant': etudiant,
        'eleve': eleve,
        'tous_messages': tous_messages,
        'etudiants': etudiants,
    })




# @login_required
# def mesPaiement(request):
#     eleve = get_object_or_404(Etudiant, username = request.user)
#     inscriptions = eleve.inscriptions.all()
    
#     mesPaiements = PaiementEleve.objects.filter(
#         inscription_Etudiant__in = inscriptions, inscription_salleClasse__in = inscriptions.salleClasse
#     )
    
#     return render(request, 'eleve/mesPaiement.html', {'mesPaiements': mesPaiements , 'etudiant': eleve, 'inscriptions': inscriptions})
from collections import defaultdict


from collections import defaultdict

@login_required
@eleve_required
def mesPaiement(request):

    # Récupération de l'élève connecté
    try:
        eleve = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')

    inscriptions = eleve.inscriptions.all()
    paiements = PaiementEleve.objects.filter(inscription_Etudiant__in=inscriptions)

    # Récupération de l'année scolaire
    annee = inscriptions.first().anneeAcademique if inscriptions else None

    # Paiements regroupés par salle
    paiements_temp = defaultdict(list)
    for paiement in paiements:
        salle = paiement.inscription_Etudiant.salleClasse
        paiements_temp[salle.id].append(paiement)

    paiements_par_salle = []
    total_paye_global = 0
    restePayer_global = 0

    for salle_id, paiements in paiements_temp.items():

        salle = paiements[0].inscription_Etudiant.salleClasse

        # FILTRAGE PAR TYPE DE PAIEMENT
        totalInscription = sum(p.montantVerse for p in paiements if p.typePaiement == "Inscription")
        totalEtudeDossier = sum(p.montantVerse for p in paiements if p.typePaiement == "Etude du dossier")
        totalScolarite = sum(p.montantVerse for p in paiements if p.typePaiement == "Scolarite")
        totalFraisAssocie = sum(p.montantVerse for p in paiements if p.typePaiement == "Associés")

        total_salle = totalInscription + totalEtudeDossier + totalScolarite + totalFraisAssocie
        total_paye_global += total_salle

        # Récupération du coût total de la classe
        try:
            cout_obj = Cout.objects.get(anneeScolaire=annee, classe=salle.niveau)
        except Cout.DoesNotExist:
            cout_obj = SimpleNamespace(coutInscription=0, coutScolarite=0, fraisEtudeDossier=0, fraisAssocie=0)

        cout_total = (
            cout_obj.coutInscription +
            cout_obj.coutScolarite +
            cout_obj.fraisEtudeDossier +
            cout_obj.fraisAssocie
        )

        reste_salle = max(cout_total - total_salle, 0)
        restePayer_global += reste_salle

        paiements_par_salle.append({
            'salle': salle,
            'paiements': sorted(paiements, key=lambda p: p.datePaiement, reverse=True),
            'totalInscription': totalInscription,
            'totalEtudeDossier': totalEtudeDossier,
            'totalScolarite': totalScolarite,
            'totalFraisAssocie': totalFraisAssocie,

            # Coûts attendus individuellement
            'coutInscription': cout_obj.coutInscription,
            'coutEtudeDossier': cout_obj.fraisEtudeDossier,
            'coutScolarite': cout_obj.coutScolarite,
            'coutFraisAssocie': cout_obj.fraisAssocie,

            # Restes individuels par type
            'resteInscription': max(cout_obj.coutInscription - totalInscription, 0),
            'resteEtudeDossier': max(cout_obj.fraisEtudeDossier - totalEtudeDossier, 0),
            'resteScolarite': max(cout_obj.coutScolarite - totalScolarite, 0),
            'resteFraisAssocie': max(cout_obj.fraisAssocie - totalFraisAssocie, 0),

            'cout_attendu': cout_total,
            'total_paye': total_salle,
            'reste_a_payer': reste_salle,
        })


    return render(request, 'eleve/mesPaiement.html', {
        'paiements_par_salle': paiements_par_salle,
        'etudiant': eleve,
        'total_paye': total_paye_global,
        'restePayer': restePayer_global,
    })



def export_paiement_pdf(request, salle_id):

    eleve = get_object_or_404(Etudiant, utilisateur=request.user)
    inscription = eleve.inscriptions.filter(salleClasse_id=salle_id).first()
    salle = inscription.salleClasse
    annee = inscription.anneeAcademique

    paiements = PaiementEleve.objects.filter(inscription_Etudiant=inscription)

    # Totaux par type
    totalInscription = sum(p.montantVerse for p in paiements if p.typePaiement == "Inscription")
    totalEtudeDossier = sum(p.montantVerse for p in paiements if p.typePaiement == "Etude du dossier")
    totalScolarite = sum(p.montantVerse for p in paiements if p.typePaiement == "Scolarite")
    totalFraisAssocie = sum(p.montantVerse for p in paiements if p.typePaiement == "Associés")

    total_paye = totalInscription + totalEtudeDossier + totalScolarite + totalFraisAssocie

    try:
        cout = Cout.objects.get(anneeScolaire=annee, classe=salle.niveau)
    except Cout.DoesNotExist:
        cout = SimpleNamespace(coutInscription=0, coutScolarite=0, fraisEtudeDossier=0, fraisAssocie=0)

    cout_total = cout.coutInscription + cout.coutScolarite + cout.fraisEtudeDossier + cout.fraisAssocie

    reste_a_payer = max(cout_total - total_paye, 0)

    # PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # LOGO
    logo_path = os.path.join(settings.STATIC_ROOT, "image/Logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=4*cm, height=4*cm)
        logo.hAlign = "CENTER"
        elements.append(logo)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b><font size=20>RELEVÉ DE PAIEMENT</font></b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    # INFO ÉLÈVE
    elements.append(Paragraph(f"<b>Élève :</b> {eleve.nom} {eleve.prenom}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Classe :</b> {salle.niveau} - {salle.nom}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Année scolaire :</b> {annee}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Matricule :</b> {eleve.matricule}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # HISTORIQUE DES PAIEMENTS
    elements.append(Paragraph("<b>Historique des paiements</b>", styles["Heading3"]))
    historique_data = [["Date", "Type", "Montant (FCFA)", "Mode"]]
    for p in paiements.order_by('-datePaiement'):
        historique_data.append([
            p.datePaiement.strftime("%d/%m/%Y"),
            p.typePaiement,
            p.montantVerse,
            p.modePaiment,
        ])
    if len(historique_data) == 1:
        historique_data.append(["-", "Aucun paiement enregistré", "-", "-"])

    historique_table = Table(historique_data, colWidths=[3*cm, 5*cm, 4*cm, 4*cm])
    historique_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    elements.append(historique_table)
    elements.append(Spacer(1, 20))

    # RÉCAPITULATIF
    elements.append(Paragraph("<b>Récapitulatif</b>", styles["Heading3"]))
    data = [
        ["Type", "Payé (FCFA)", "Attendu", "Reste"],
        ["Frais d'inscription", totalInscription, cout.coutInscription, max(cout.coutInscription - totalInscription, 0)],
        ["Frais étude dossier", totalEtudeDossier, cout.fraisEtudeDossier, max(cout.fraisEtudeDossier - totalEtudeDossier, 0)],
        ["Frais scolarité", totalScolarite, cout.coutScolarite, max(cout.coutScolarite - totalScolarite, 0)],
        ["Frais associés", totalFraisAssocie, cout.fraisAssocie, max(cout.fraisAssocie - totalFraisAssocie, 0)],
        ["", "", "", ""],
        ["TOTAL", total_paye, cout_total, reste_a_payer],
    ]

    table = Table(data, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # QR CODE
    qr_data = (
        f"Eleve: {eleve.nom} {eleve.prenom}\n"
        f"Classe: {salle.niveau}-{salle.nom}\n"
        f"Année: {annee}\n"
        f"Total payé: {total_paye} FCFA\n"
        f"Reste: {reste_a_payer} FCFA"
    )

    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer)
    qr_buffer.seek(0)
    qr = Image(qr_buffer, width=3*cm, height=3*cm)
    qr.hAlign = "LEFT"

    elements.append(Paragraph("<b>Vérification QR Code :</b>", styles["Normal"]))
    elements.append(qr)
    elements.append(Spacer(1, 20))

    # # SIGNATURE
    # elements.append(Paragraph("<b>Directeur des Études</b>", styles["Normal"]))
    # elements.append(Spacer(1, 40))
    # elements.append(Paragraph("______________________________", styles["Normal"]))

    # Build
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Paiements_{eleve.nom}_{salle.nom}.pdf"'

    return response


@login_required
@eleve_required
def profil(request):
    try:
        etudiant = Etudiant.objects.get(utilisateur__username=request.user.username)
    except Etudiant.DoesNotExist:
        messages.error(request, "Les identifiants sont incorrects !")
        return redirect('connexion')
    context = {'etudiant': etudiant}
    
    return render(request, 'eleve/profil.html', context)




from django.utils import timezone

@login_required
@eleve_required
def messages_api(request, id, matricule):
    last_id = int(request.GET.get("since", 0))
    destinataire = Etudiant.objects.get(username=request.user)
    expediteur = get_object_or_404(Etudiant, pk=id)
    
    # Récupérer les messages non lus
    messages_nouveaux = Messages.objects.filter(
        Q(expediteur=expediteur, destinataire=destinataire, id__gt=last_id) |
        Q(expediteur=destinataire, destinataire=expediteur, id__gt=last_id)
    ).order_by('date_envoi')
    
    data = [{
        "id": m.id,
        "contenu": m.contenu,
        "heure": m.date_envoi.strftime("%H:%M:%S")
    } for m in messages_nouveaux]
    
    return JsonResponse({"messages": data})

@login_required
@eleve_required
def marquer_message_lu(request, message_id):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        message = get_object_or_404(Messages, pk=message_id, destinataire__username=request.user)
        message.est_lu = True
        message.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)



