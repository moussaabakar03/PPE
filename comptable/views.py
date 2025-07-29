from django.shortcuts import render

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
# from .models import Enseignant
# from .form import PaiementPersonnelForm

from secretaire.models import Cout, Inscription, Etudiant, AnneeScolaire, SalleDeClasse
# from . form import PaiementForm, timezone
# Create your views here.



def selectionSalle(request):
    annees = AnneeScolaire.objects.all().order_by('-id')
    SalleDeClasses = SalleDeClasse.objects.all()
    context = {
        'SalleClasses': SalleDeClasses,
        "annees": annees
    }
    # Inclure le chemin relatif vers le template
    return render(request, 'selectionSalle.html', context)


def ajouter_paiement(request, id):
    salleClasse = SalleDeClasse.objects.get(id=id)
    inscrits = Inscription.objects.filter(
        salleClasse = salleClasse
    ).select_related('etudiant', 'salleClasse')
   
    context = {
        'paiement': paiements,
        'inscrits': inscrits,
    }
    return render(request, 'ajouter_paiement.html', context)




def liste_eleve(request, id_salle, id_annee):
 
    # Initialisation du contexte
    context = {}
    
    try:
        # Récupération de la salle de classe
        salleClasse = get_object_or_404(SalleDeClasse, id=id_salle)
        anneesScolaire = get_object_or_404(AnneeScolaire, id= id_annee)
        
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
        }

    except Exception as e:
        messages.error(request, f"Erreur de chargement: {str(e)}")
        context['error'] = str(e)
    
    return render(request,  'liste_eleve.html', context)


def ajouter_paiement(request, id_inscription):
    inscriptionEleve = get_object_or_404(Inscription, id=id_inscription)
    
    classe = inscriptionEleve.salleClasse.niveau
    annee = inscriptionEleve.anneeAcademique
    
    cout = get_object_or_404(Cout, classe=classe, anneeScolaire=annee)
    
    
    if request.method == 'POST':
        # form = PaiementForm(request.POST)
        # if form.is_valid():
        #     paiement = form.save(commit=False)
        #     paiement.etudiant = eleve
        #     paiement.save()
        #     messages.success(request, f"Paiement enregistré pour {eleve.nom_complet()}")
        #     return redirect('liste_eleve', id_salle=eleve.classe.salle.id, id_classe=eleve.classe.id)
        pass
    else:
        # form = PaiementForm(initial={
        #     'date_paiement': timezone.now().date(),
        #     'mois_couvert': timezone.now().strftime("%B %Y")
        # })
        pass
    
    return render(request,  'ajouter_paiement.html', {
        'eleve': inscriptionEleve,
        'cout': cout,
        'salle': inscriptionEleve.classe.salle if hasattr(inscriptionEleve, 'classe') else None
    })

def liste_personnel(request):
    enseignants = Enseignant.objects.all()
    return render(request,  'liste_personnel.html', {
        'enseignants': enseignants
    })

def detail_enseignant(request, enseignant_id):
    enseignant = get_object_or_404(Enseignant, id=enseignant_id)
    return render(request,  'detail_enseignant.html', {
        'enseignant': enseignant
    })


def ajouter_paiement_personnel(request, enseignant_id):
    enseignant = get_object_or_404(Enseignant, id=enseignant_id)

    if request.method == 'POST':
        form = PaiementPersonnelForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.enseignant = enseignant
            paiement.save()
            return redirect('liste_personnel')
    else:
        form = PaiementPersonnelForm()

    return render(request,  'ajouter_paiement_personnel.html', {
        'form': form,
        'enseignant': enseignant
    })