from django.shortcuts import render

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
# from .models import Enseignant
# from .form import PaiementPersonnelForm

import json
from collections import defaultdict
from decimal import Decimal

from comptable.models import PaiementEleve
from secretaire.models import Classe, Cout, Inscription, Etudiant, AnneeScolaire, SalleDeClasse
from django.contrib.auth.decorators import login_required

from acadPro.utils.decorators import staff_required

# from . form import PaiementForm, timezone
# Create your views here.
@login_required
@staff_required
def selectionSalle(request):
    annees = AnneeScolaire.objects.all().order_by('-id')
    SalleDeClasses = SalleDeClasse.objects.all()
    context = {
        'SalleClasses': SalleDeClasses,
        "annees": annees
    }
    # Inclure le chemin relatif vers le template
    return render(request, 'selectionSalle.html', context)

@login_required
@staff_required
def liste_eleve(request, id_salle, id_annee):
    # Initialisation du contexte
    context = {}
    
    try:
        # Récupération de la salle de classe
        salleClasse = get_object_or_404(SalleDeClasse, id=id_salle)
        anneesScolaire = get_object_or_404(AnneeScolaire, id= id_annee)
        couts = Cout.objects.filter(classe=salleClasse.niveau, anneeScolaire=anneesScolaire)
        messagesCoutNonEnregistrer = ""
        if not couts.exists():
            # messages.error(request, "Aucun cout n'est enregistré pour cette salle de classe ")
            messagesCoutNonEnregistrer= "Aucun cout n'est enregistré cette année pour cette salle de classe. Pour effectuer cette opératrion, le secretaire doit ajouter les frais de cette classe"

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
            "messagesCoutNonEnregistrer": messagesCoutNonEnregistrer
        }

    except Exception as e:
        messages.error(request, f"Erreur de chargement: {str(e)}")
        context['error'] = str(e)
    
    return render(request,  'liste_eleve.html', context)

@login_required
@staff_required
def ajouter_paiement(request, id_inscription, id_annee):
    anneeScol = get_object_or_404(AnneeScolaire, id=id_annee)
    inscriptionEleve = get_object_or_404(Inscription, id=id_inscription, anneeAcademique = anneeScol)
    classe = inscriptionEleve.salleClasse.niveau
    
    eleve = inscriptionEleve.etudiant

    cout = get_object_or_404(Cout, anneeScolaire=anneeScol, classe=classe)
    totalCout = cout.coutInscription + cout.coutScolarite + cout.fraisEtudeDossier + cout.fraisAssocie

    paiements = PaiementEleve.objects.filter(inscription_Etudiant=inscriptionEleve)

    totalPaye = sum(p.montantVerse for p in paiements)
    resteTotalPaye = totalCout - totalPaye

    # Paiement par type
    dejaPayeParType = defaultdict(Decimal)
    
    for p in paiements:
        dejaPayeParType[p.typePaiement] += p.montantVerse
        
    if request.method == 'POST':
        type_paiement = request.POST.get('type_paiement')
        montantVerse = Decimal(request.POST.get('montantVerse') or "0")
        mode_paiement = request.POST.get('mode_paiement')
        periodeConcerne = request.POST.get('periodeConcerne')

        montantMaximum = {
            'Frais de scolarité': cout.coutScolarite,
            "Frais d'inscription": cout.coutInscription,
            "Frais d'étude du dossier": cout.fraisEtudeDossier,
            "Frais Associés": cout.fraisAssocie,
            "Autre": 0
        }.get(type_paiement, 0)

        dejaPaye = dejaPayeParType[type_paiement]

        if dejaPaye + montantVerse > montantMaximum:
            error = "Montant versé dépasse le montant requis pour ce type de frais."
            messages.error(request, f"Montant versé dépasse le montant requis pour {type_paiement}.")
        else:
            PaiementEleve.objects.create(
                inscription_Etudiant=inscriptionEleve,
                montantVerse=montantVerse,
                typePaiement=type_paiement,
                modePaiment=mode_paiement,
                periodeConcerne=periodeConcerne
            )
            messages.success(request, f"Paiement de {montantVerse} FCFA pour {eleve.nom} {eleve.prenom} enregistré avec succès.")
            return redirect(request.path)  # Rafraîchir la page

    return render(request, 'ajouter_paiement.html', {
        'inscriptionEleve': inscriptionEleve,
        'cout': cout,
        'anneeScol': anneeScol,
        'salleClasse': inscriptionEleve.salleClasse,
        'paiements': paiements,
        'totalCout': totalCout,
        'totalPaye': totalPaye,
        'resteTotalPaye': resteTotalPaye,
        'dejaPayeParType_json': json.dumps({k: float(v) for k, v in dejaPayeParType.items()}),

    })

@login_required
@staff_required
def indexComptable(request):
    paiements = PaiementEleve.objects.all()
    totalMontantPaye = sum(paiement.montantVerse for paiement in paiements)
    
    paiementsRecentes= PaiementEleve.objects.all()[:5]
    return render(request, 'dashbordComptable.html', {
        'paiements': paiements,
        'totalPaye': totalMontantPaye,
        'paiementsRecentes': paiementsRecentes
    })

@login_required
@staff_required
def listePaiments(request):
    paiements = PaiementEleve.objects.all()
    return render(request, 'listePaiments.html', {'paiements': paiements})

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
        anneeScolaire = request.POST.get("anneeScolaire", "").strip()
        niveau = request.POST.get("niveau", "").strip()

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

        if anneeScolaire:
            try:
                anneeAcademique = AnneeScolaire.objects.get(pk=int(anneeScolaire))
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
    
    
    