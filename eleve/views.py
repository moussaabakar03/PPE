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
from secretaire.models import AnneeScolaire, Emargement, EmploiDuTemps, Etudiant, Evaluation, Inscription, Messages, PlageHoraire, SalleDeClasse, depotDossierEtudiant
# Create your views here.


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
def presence(request):
    if Etudiant.objects.filter(username = request.user).exists():
        etudiant = Etudiant.objects.get(username = request.user)
    else:
        messages.error(request, "Veillez vous authentifier")
        return redirect('connexion')
    inscrits = Inscription.objects.filter(etudiant =etudiant)
    # parent = Etudiant.objects.get(parent = etudiant.parent)
    emargements = Emargement.objects.filter(inscrits__in=inscrits).order_by('-id')
    return render(request, 'eleve/presence.html', {"etudiant": etudiant, "emargements": emargements})
    
@login_required
def notes(request):
    if Etudiant.objects.filter(username = request.user).exists():
        etudiant = Etudiant.objects.get(username = request.user)
    else:
        messages.error(request, "Les identifiants sont incorrect!")
        return redirect('connexion')

    # inscriptions = etudiant.inscriptions.all()
    if request.method == "POST":
        annee = request.POST['annee']
        if annee:
            anneeScolaire = AnneeScolaire.objects.get(pk=int(annee))
            if etudiant:
                evaluations = Evaluation.objects.filter(cours__anneeScolaire = anneeScolaire, etudiant = etudiant)
                return render(request, 'eleve/notes.html', {'evaluations': evaluations, 'etudiant': etudiant, 'annees': AnneeScolaire.objects.all().order_by('-id')})
            else:
                return HttpResponse("Aucun étudiant trouvé")
        else:
            evaluations = None
    else:
        evaluations = None
    
    return render(request, 'eleve/notes.html', {'evaluations': evaluations, 'etudiant': etudiant, 'annees': AnneeScolaire.objects.all().order_by('-id')})

@login_required
def inscriptionPayement(request):
    return render(request, 'eleve/inscriptionPayement.html')

@login_required
def messagesEleves(request):
    etudiants = Etudiant.objects.exclude(username = request.user)
    etudiant = get_object_or_404(Etudiant, username = request.user)
    contains = {"etudiants": etudiants, "etudiant": etudiant}
    return render(request, 'eleve/messages.html', contains)

@login_required
def emploiDuTempsEtudiant(request):
    eleve = Etudiant.objects.get(username = request.user)
    inscrits = eleve.inscriptions.all()
    containts = {"inscrits": inscrits, "etudiant": eleve}
    return render(request, "eleve/emploi_temps_etudiant.html", containts)

    



#s'intégrer avec AJAX
@login_required
def echangeMessageEleves(request, id):
    eleve = Etudiant.objects.get(username = request.user)
    etudiant = Etudiant.objects.get(id=id)
    
    etudiants = Etudiant.objects.exclude(username = request.user)
    
    if request.method == "POST" and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print(request.POST)  # Pour debug
        contenu_message = request.POST['message']
        if contenu_message != '':
            message = Messages.objects.create(contenu=contenu_message, expediteur=eleve, destinataire=etudiant, est_lu=False)
            message.save()
        else:
            messages = Messages.objects.filter(expediteur=eleve, destinataire=etudiant)
            for message in messages:
                message.est_lu = True
                message.save()
                return redirect('echangeMessageEleves', id=id)
            return redirect('echangeMessageEleves', id=id)
        
        return redirect('echangeMessageEleves', id=id)
    
    #   if request.method == "POST":
    #     contenu_message = request.POST.get('message') or json.loads(request.body).get('message')
    #     if contenu_message:
    #         message = Messages.objects.create(contenu=contenu_message, expediteur=eleve, destinataire=etudiant, est_lu=False)
    #         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #             return JsonResponse({
    #                 'success': True,
    #                 'message_id': message.id,
    #                 'date_envoi': message.date_envoi.strftime('%H:%M:%S'),
    #             })
    #         else:
    #             return redirect('echangeMessageEleves', id=id)
    # # Récupérer tous les messages entre ces deux utilisateurs
    tous_messages = Messages.objects.filter(
        (Q(expediteur=eleve) & Q(destinataire=etudiant)) | 
        (Q(expediteur=etudiant) & Q(destinataire=eleve))
    ).order_by('date_envoi')
    
    # Marquer les messages comme lus quand la page est chargée
    Messages.objects.filter(expediteur=etudiant, destinataire=eleve, est_lu=False).update(est_lu=True)
    
    contains = {
        'etudiant': etudiant, 
        'eleve': eleve, 
        'tous_messages': tous_messages,
        "etudiants": etudiants,
    }
    return render(request, 'eleve/echangeMessageEleves.html', contains)


@login_required
def affichageEmploiTemps(request, id1, id2):
    eleve = Etudiant.objects.get(username = request.user)
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
def echangeEleveEleve(request, id):
    eleve = Etudiant.objects.get(username=request.user)
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

    etudiants = Etudiant.objects.exclude(username=request.user)

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

def mesPaiement(request):
    eleve = get_object_or_404(Etudiant, username=request.user)
    inscriptions = eleve.inscriptions.all()
    paiements_groupes = defaultdict(list)

    # Récupérer tous les paiements liés aux inscriptions de l'élève
    paiements = PaiementEleve.objects.filter(inscription_Etudiant__in=inscriptions)

    # Grouper les paiements par salleClasse
    for paiement in paiements:
        salle = paiement.inscription_Etudiant.salleClasse
        paiements_groupes[salle].append(paiement)

    return render(request, 'eleve/mesPaiement.html', {
        'paiements_groupes': dict(paiements_groupes),
        'etudiant': eleve
    })
  



from django.utils import timezone

@login_required
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
def marquer_message_lu(request, message_id):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        message = get_object_or_404(Messages, pk=message_id, destinataire__username=request.user)
        message.est_lu = True
        message.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)