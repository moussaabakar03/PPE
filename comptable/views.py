from django.shortcuts import render

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
# from .models import Enseignant
# from .form import PaiementPersonnelForm

import json
from collections import defaultdict
from decimal import Decimal

from comptable.models import PaiementEleve
from secretaire.models import Classe, Cout, Inscription, Etudiant, AnneeScolaire, SalleDeClasse, TrancheCout
from django.contrib.auth.decorators import login_required

from acadPro.utils.decorators import staff_required



from django.core.mail import send_mail
from django.conf import settings


def annee_active():
    try:
        return AnneeScolaire.objects.get(est_active=True)
    except AnneeScolaire.DoesNotExist:
        return None
    

def changer_annee_active(request, annee_id):
    annee = AnneeScolaire.objects.get(id=annee_id)
    annee.est_active = True
    annee.save()
    messages.success(request, f"L'année {annee} est maintenant active.")
    return redirect("comptable:indexComptable")



@login_required
@staff_required
def indexComptable(request):
    paiements = PaiementEleve.objects.filter(inscription_Etudiant__anneeAcademique=annee_active())
    totalMontantPaye = sum(paiement.montantVerse for paiement in paiements)
    
    paiementsRecentes= PaiementEleve.objects.filter(inscription_Etudiant__anneeAcademique=annee_active())[:5]

    nbre_transactions = PaiementEleve.objects.filter(inscription_Etudiant__anneeAcademique=annee_active()).count()

    return render(request, 'dashbordComptable.html', {
        'paiements': paiements,
        'totalPaye': totalMontantPaye,
        'paiementsRecentes': paiementsRecentes,
        'nbre_transactions': nbre_transactions
    })



# from . form import PaiementForm, timezone
# Create your views here.
@login_required
@staff_required
def selectionSalle(request, id_salle):
    # annees = AnneeScolaire.objects.all().order_by('-id')
    annee = annee_active()
    classe = get_object_or_404(Classe, id=id_salle)
    salleClasses = SalleDeClasse.objects.filter(niveau=classe)
    
    tranches = TrancheCout.objects.filter(cout__classe=classe, cout__anneeScolaire=annee)

    context = {
        'salleClasses': salleClasses,
        "annee": annee,
        "classe": classe,
        "tranches": tranches
    }
    # Inclure le chemin relatif vers le template
    return render(request, 'selectionSalle.html', context)


@login_required
@staff_required
def selectionClasse(request):
    annee = annee_active()
    classes = Classe.objects.all()
    context = {
        'classes': classes,
        "annee": annee  
    }
    # Inclure le chemin relatif vers le template
    return render(request, 'selection_classe.html', context)


@login_required
@staff_required
def liste_eleve(request, id_salle):
    # Initialisation du contexte
    context = {}
    
    try:
        # Récupération de la salle de classe
        salleClasse = get_object_or_404(SalleDeClasse, id=id_salle)
        # anneesScolaire = get_object_or_404(AnneeScolaire, id= id_annee)
        anneesScolaire = annee_active()
        couts = Cout.objects.filter(classe=salleClasse.niveau, anneeScolaire=anneesScolaire)
        messagesCoutNonEnregistrer = ""
        if not couts.exists():
            # messages.error(request, "Aucun cout n'est enregistré pour cette salle de classe ")
            messagesCoutNonEnregistrer= "Aucun cout n'est enregistré cette année pour cette classe. Pour effectuer cette opératrion, le secretaire doit ajouter les frais de cette classe"

        # Récupération des élèves inscrits avec optimisation des requêtes
        inscrits = Inscription.objects.filter(
            salleClasse=salleClasse,
            anneeAcademique=anneesScolaire
        ).select_related('etudiant').order_by('etudiant__nom', 'etudiant__prenom')
       
        # Préparation du contexte pour le template
        context = {
            "salleClasse": salleClasse,
            "anneesScolaire": anneesScolaire,
            "inscrits": inscrits,
            "messagesCoutNonEnregistrer": messagesCoutNonEnregistrer,
        }

    except Exception as e:
        messages.error(request, f"Erreur de chargement: {str(e)}")
        context['error'] = str(e)
    
    return render(request,  'liste_eleve.html', context)

@login_required
@staff_required
def ajouter_paiement(request, id_inscription):
    # anneeScol = get_object_or_404(AnneeScolaire, id=id_annee)
    anneeScol = annee_active()
    inscriptionEleve = get_object_or_404(Inscription, id=id_inscription, anneeAcademique = anneeScol)
    classe = inscriptionEleve.salleClasse.niveau
    
    eleve = inscriptionEleve.etudiant

    cout = get_object_or_404(Cout, anneeScolaire=anneeScol, classe=classe)
    totalCout = cout.coutInscription + cout.coutScolarite + cout.fraisEtudeDossier + cout.fraisAssocie

    paiements = PaiementEleve.objects.filter(inscription_Etudiant=inscriptionEleve)

    totalPaye = sum(p.montantVerse for p in paiements)
    resteTotalPaye = totalCout - totalPaye
    
    # Frais de scolarité
    # Frais d'inscription
    # Frais d'étude du dossier
    # Frais Associés
    
    paiementsScolarite = PaiementEleve.objects.filter(inscription_Etudiant=inscriptionEleve, typePaiement="Scolarite")
    totalScolarite = sum(p.montantVerse for p in paiementsScolarite)
    total_reste_scolarite = cout.coutScolarite - totalScolarite
    paiementsInscription = PaiementEleve.objects.filter(inscription_Etudiant=inscriptionEleve, typePaiement="Inscription")
    totalInscription = sum(p.montantVerse for p in paiementsInscription)
    total_reste_inscription = cout.coutInscription - totalInscription
    paiementsEtudeDossier = PaiementEleve.objects.filter(inscription_Etudiant=inscriptionEleve, typePaiement="Etude du dossier")
    totalEtudeDossier = sum(p.montantVerse for p in paiementsEtudeDossier)
    total_reste_etude_dossier = cout.fraisEtudeDossier - totalEtudeDossier
    paiementsFraisAssocie = PaiementEleve.objects.filter(inscription_Etudiant=inscriptionEleve, typePaiement="Associés")
    totalFraisAssocie = sum(p.montantVerse for p in paiementsFraisAssocie)
    total_reste_frais_associe = cout.fraisAssocie - totalFraisAssocie
    
    

    # Paiement par type
    dejaPayeParType = defaultdict(Decimal)
    
    for p in paiements:
        dejaPayeParType[p.typePaiement] += p.montantVerse
        
    if request.method == 'POST':
        type_paiement = request.POST.get('type_paiement')
        montantVerse = Decimal(request.POST.get('montantVerse') or "0")
        mode_paiement = request.POST.get('mode_paiement')
        # periodeConcerne = request.POST.get('periodeConcerne')

        montantMaximum = {
            'Scolarite': cout.coutScolarite,
            "Inscription": cout.coutInscription,
            "Etude du dossier": cout.fraisEtudeDossier,
            "Associés": cout.fraisAssocie,
            "Autre": 0
        }.get(type_paiement, 0)

        
        dejaPaye = dejaPayeParType[type_paiement]
        
        if montantVerse >= 1:
            if dejaPaye + montantVerse > montantMaximum:
                # error = "Montant versé dépasse le montant requis pour ce type de frais."
                messages.error(request, f"Montant versé dépasse le montant requis pour {type_paiement}.")
            else:
                PaiementEleve.objects.create(
                    inscription_Etudiant=inscriptionEleve,
                    montantVerse=montantVerse,
                    typePaiement=type_paiement,
                    modePaiment=mode_paiement,
                )
                messages.success(request, f"Paiement de {montantVerse} FCFA pour {eleve.nom} {eleve.prenom} enregistré avec succès.")
                return redirect(request.path) 
        else:
            messages.error(request, "Le montant doit être superieur égale '1'")
            return redirect("comptable:ajouter_paiement", id_inscription=id_inscription)

    tranches = TrancheCout.objects.filter(cout__classe=classe, cout__anneeScolaire=anneeScol)
    paiements_effectues = dejaPayeParType["Scolarite"]
    
    mes_traches = []
    cumul = 0
    for tranche in tranches:
        cumul += tranche.montant
        mes_traches.append({
            "id": tranche.id,
            "montant": tranche.montant,
            "libelle": tranche.libelle,
            "cumul": cumul,
            "reste_a_payer": max(0, cumul - paiements_effectues)
        })
    tranches = mes_traches
    first_mois_non_paye = None
    for tranche in tranches:
        if paiements_effectues < tranche['cumul']:
            first_mois_non_paye = tranche
            break
    
    
    return render(request, 'ajouter_paiement.html', {
        'inscriptionEleve': inscriptionEleve,
        'cout': cout,
        'anneeScol': anneeScol,
        'salleClasse': inscriptionEleve.salleClasse,
        'paiements': paiements,
        'totalCout': totalCout,
        'totalPaye': totalPaye,
        "totalInscription": totalInscription,
        "totalEtudeDossier": totalEtudeDossier,
        "totalFraisAssocie": totalFraisAssocie,
        'totalScolarite': totalScolarite,
        'total_reste_scolarite': total_reste_scolarite,
        'total_reste_inscription': total_reste_inscription,
        'total_reste_etude_dossier': total_reste_etude_dossier,
        'total_reste_frais_associe': total_reste_frais_associe,
        'resteTotalPaye': resteTotalPaye,
        'dejaPayeParType_json': json.dumps({k: float(v) for k, v in dejaPayeParType.items()}),
        'tranches':  tranches,
        'paiements_effectues': paiements_effectues,
        'first_mois_non_paye': first_mois_non_paye
    })


@login_required
@staff_required
def modifierPaiement(request, id_paiement):
    paiement = get_object_or_404(PaiementEleve, id=id_paiement)
    inscription_id = paiement.inscription_Etudiant.id

    if request.method == 'POST':
        # Vous pouvez restreindre les champs modifiables ici
        paiement.montantVerse = Decimal(request.POST.get('montantVerse'))
        paiement.modePaiment = request.POST.get('mode_paiement')
        # paiement.typePaiement = request.POST.get('type_paiement')
        paiement.save()
        messages.success(request, "Paiement modifié avec succès.")
        return redirect('comptable:ajouter_paiement', id_inscription=inscription_id)

    return render(request, 'modifierPaiement.html', {'paiement': paiement})

@login_required
@staff_required
def modifier_paiement(request, id_paiement):
    paiement = get_object_or_404(PaiementEleve, id=id_paiement)

    if request.method == 'POST':
        # Vous pouvez restreindre les champs modifiables ici
        paiement.montantVerse = Decimal(request.POST.get('montantVerse'))
        paiement.modePaiment = request.POST.get('mode_paiement')
        paiement.description = request.POST.get('description')
        paiement.save()
        messages.success(request, "Paiement modifié avec succès.")
        return redirect('comptable:listePaiements')

    return render(request, 'modifier_paiement.html', {'paiement': paiement})

@login_required
@staff_required
def supprimer_paiement(request, id_paiement):
    paiement = get_object_or_404(PaiementEleve, id=id_paiement)
    if paiement:
        paiement.delete()
        messages.success(request, "Paiement supprimé avec succès.")
        return redirect('comptable:listePaiements')
    
@login_required
@staff_required
def supprimerPaiement(request, id_paiement):
    paiement = get_object_or_404(PaiementEleve, id=id_paiement)
    inscription_id = paiement.inscription_Etudiant.id

    if paiement:
        paiement.delete()
        messages.success(request, "Paiement supprimé avec succès.")
        return redirect('comptable:ajouter_paiement', id_inscription=inscription_id)
    

@login_required
@staff_required
def alerte_retard_paiement(request, id_classe):
    inscris = Inscription.objects.filter(
        salleClasse__niveau__id=id_classe,
        anneeAcademique=annee_active()
    )

    tranches = TrancheCout.objects.filter(
        cout__classe__id=id_classe,
        cout__anneeScolaire=annee_active()
    )
    
    if request.method == "GET":
        tranche_filtre = request.GET.get("tranche_filter")
        if not tranche_filtre:
            return redirect("comptable:selectionSalle", id_salle=id_classe)
        tranche = get_object_or_404(TrancheCout, id=tranche_filtre)
    else:
        return redirect("comptable:selectionSalle", id_salle=id_classe)
    
    # Calcul du cumul jusqu'à la tranche sélectionnée
    cumul = 0
    for t in tranches:
        cumul += t.montant
        if t == tranche:
            break
    
    # Vérification des paiements
    for i in inscris:
        paiements = PaiementEleve.objects.filter(
            inscription_Etudiant=i,
            typePaiement="Scolarite"
        )
        total_paye = sum(p.montantVerse for p in paiements)
        
        if total_paye < cumul:
            montant_restant = cumul - total_paye
            # print(f"Élève: {i.etudiant.nom} {i.etudiant.prenom} - Retard de {montant_restant} FCFA")
            
            parent = i.etudiant.parent
            if parent and parent.email:
                # Envoi d'un mail au parent
                sujet = f"Alerte retard de paiement - {i.etudiant.nom} {i.etudiant.prenom}"
                message = (
                    f"Bonjour {parent.nom} {parent.prenom},\n\n"
                    f"Votre enfant {i.etudiant.nom} {i.etudiant.prenom} "
                    f"n'a pas encore payé la tranche '{tranche.libelle}'.\n"
                    f"Montant restant dû : {montant_restant} FCFA.\n\n"
                    f"Merci de régulariser la situation avant la date d'échéance : {tranche.date_echeance}.\n\n"
                    f"Cordialement,\nAdministration scolaire"
                )
                
                send_mail(
                    sujet,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [parent.email],
                    fail_silently=False,
                )
                # print(f"Mail envoyé à {parent.email}")
                messages.success(request, f"Alerte envoyée à {parent.email}")
        # else:
        #     # print(f"Élève: {i.etudiant.nom} {i.etudiant.prenom} - Paiement à jour")
        #     messages.info(request, f"Paiement à jour pour {i.etudiant.nom} {i.etudiant.prenom}")
        #     pass
    return redirect("comptable:selectionSalle", id_salle=id_classe)


@login_required
@staff_required
def export_paiement_pdf(request, id_inscription):

    annee = annee_active()
    inscriptionEleve = get_object_or_404(Inscription, id=id_inscription, anneeAcademique=annee)
    eleve = inscriptionEleve.etudiant

    paiements = PaiementEleve.objects.filter(inscription_Etudiant=inscriptionEleve)

    cout = get_object_or_404(Cout, anneeScolaire=annee, classe=inscriptionEleve.salleClasse.niveau)
    totalCout = cout.coutInscription + cout.coutScolarite + cout.fraisEtudeDossier + cout.fraisAssocie
    totalPaye = sum(p.montantVerse for p in paiements)
    resteTotal = totalCout - totalPaye

    # Totaux par type
    totalInscription = sum(p.montantVerse for p in paiements if p.typePaiement == "Frais d'inscription")
    totalEtudeDossier = sum(p.montantVerse for p in paiements if p.typePaiement == "Frais d'étude du dossier")
    totalScolarite = sum(p.montantVerse for p in paiements if p.typePaiement == "Frais de scolarité")
    totalFraisAssocie = sum(p.montantVerse for p in paiements if p.typePaiement == "Frais Associés")

    context = {
        'eleve': eleve,
        'paiements': paiements,
        'totalCout': totalCout,
        'totalPaye': totalPaye,
        'resteTotal': resteTotal,
        'totalInscription': totalInscription,
        'totalEtudeDossier': totalEtudeDossier,
        'totalScolarite': totalScolarite,
        'totalFraisAssocie': totalFraisAssocie,
        'inscription': inscriptionEleve,
        'annee': annee,
    }

    html = render_to_string('paiement_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="paiement_{eleve.nom}_{eleve.prenom}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF")
    return response


@login_required
@staff_required
def listePaiements(request):
    paiements = PaiementEleve.objects.filter(inscription_Etudiant__anneeAcademique = annee_active())
    return render(request, 'listePaiements.html', {'paiements': paiements})

# def liste_personnel(request):
#     enseignants = Enseignant.objects.all()
#     return render(request,  'liste_personnel.html', {
#         'enseignants': enseignants
#     })

# def detail_enseignant(request, enseignant_id):
#     enseignant = get_object_or_404(Enseignant, id=enseignant_id)
#     return render(request,  'detail_enseignant.html', {
#         'enseignant': enseignant
#     })


# def ajouter_paiement_personnel(request, enseignant_id):
    # enseignant = get_object_or_404(Enseignant, id=enseignant_id)

    # if request.method == 'POST':
    #     form = PaiementPersonnelForm(request.POST)
    #     if form.is_valid():
    #         paiement = form.save(commit=False)
    #         paiement.enseignant = enseignant
    #         paiement.save()
    #         return redirect('liste_personnel')
    # else:
    #     form = PaiementPersonnelForm()

    # return render(request,  'ajouter_paiement_personnel.html', {
    #     'form': form,
    #     'enseignant': enseignant
    # })
    
    
@login_required
@staff_required    
def enretardSurPaiement(request):
    if request.method == "POST":
        matricule = request.POST.get("matricule", "").strip()
        niveau = request.POST.get("niveau", "").strip()

        anneeAcademique = annee_active()

        inscriptions = Inscription.objects.all()
        filtres_appliques = []

        if matricule:
            inscriptions = inscriptions.filter(etudiant__matricule__icontains=matricule)
            filtres_appliques.append(f"matricule: {matricule}")

        if niveau:
            try:
                classe = Classe.objects.get(pk=int(niveau))
                inscriptions = inscriptions.filter(salleClasse__niveau=classe)
                filtres_appliques.append(f"niveau: {classe}")
            except (ValueError, Classe.DoesNotExist):
                pass

        if anneeAcademique:
            try:
                inscriptions = inscriptions.filter(anneeAcademique=anneeAcademique)
                filtres_appliques.append(f"année: {anneeAcademique}")
            except (ValueError, AnneeScolaire.DoesNotExist):
                pass

        if filtres_appliques:
            messages.info(request, f"Filtres appliqués: {', '.join(filtres_appliques)}.")

        return render(request, 'enretardSurPaiement.html', {
            "inscriptions": inscriptions,
            "anneeScolaires": AnneeScolaire.objects.all(),
            "niveaux": Classe.objects.all()
        })
    
    else:
        inscriptions = Inscription.objects.select_related('etudiant', 'salleClasse__niveau').all()
        contains = {
            "inscriptions": inscriptions,
            "anneeScolaires": AnneeScolaire.objects.all(),
            "niveaux": Classe.objects.all()
        }
        return render(request, 'enretardSurPaiement.html', contains)
    
    
