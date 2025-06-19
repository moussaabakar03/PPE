
from django.shortcuts import redirect, render

from secretaire.models import AnneeScolaire, Enseignant, Etudiant, depotDossierEtudiant

def pageAccueil(request):
    return render(request, 'accueil/accueil.html')

def depotDossier(request):
    if request.method == "POST":
        cv = request.FILES["cv"]
        cv = request.FILES.get("cv")
        if not cv:
            return render(request, "accueil/depotDossier.html", {"erreur": "Veuillez télécharger votre CV."})

        niveau = request.POST["niveau"]
        numero_telephone = request.POST["numero_telephone"]
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        email = request.POST['email']
        # message = request.POST['message']
        
        depotDossierEtudiant.objects.create(
            dossier=cv,
            nom=nom,
            prenom=prenom,
            mail=email,
            niveau=niveau,
            numero_telephone=numero_telephone
        )
        return redirect('pageAccueil')
    return render(request, "accueil/depotDossier.html")

def receptionDossierStudent(request):
    receptions = depotDossierEtudiant.objects.all()
    annees = AnneeScolaire.objects.all()
    return render(request, 'accueil/receptionDossierStudent.html', {"receptions": receptions, "annees": annees})

def traiterConnexion(request):
    if request.method == "POST":
        matricule = request.POST['matricule']
        nom = request.POST['nom']
        try:
            eleve = Etudiant.objects.get(matricule=matricule, nom=nom)
            request.session['matricule'] = eleve.matricule  
            return redirect('notes', matricule=eleve.matricule)
        except Etudiant.DoesNotExist:
            # Gérer l'erreur si l'étudiant n'existe pas
            return render(request, 'accueil/connexion.html', {'erreur': "Identifiants incorrects"})
    return render(request, 'accueil/connexion.html')

def formateur(request):
    enseignants = Enseignant.objects.all()
    contains = {'enseignants': enseignants}
    return render(request, 'accueil/formateur.html', contains)