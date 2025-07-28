
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.contrib import messages

from acadPro.forms import ConnexionForm
from secretaire.models import AnneeScolaire, Classe, Cout, Enseignant, Etudiant, depotDossierEtudiant



from django.core.mail import send_mail
from django.conf import settings




def pageAccueil(request):
    return render(request, 'accueil.html')

def aPropos(request):
    return render(request, 'aPropos.html')

def cours(request):
    return render(request, 'cours.html')

def contact(request):
    return render(request, 'contact.html')

def depotDossier(request):
    if request.method == "POST":
        # cv = request.FILES["cv"]
        cv = request.FILES.get("cv")
        if not cv:
            return render(request, "depotDossier.html", {"erreur": "Veuillez télécharger votre CV."})

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
        
        return redirect('depotDossier')
    message = "Nous avons bien reçu votre demande. Vous recevrez un email de confirmation dans les prochaines heures avec les instructions pour la suite du processus."
    
    return render(request, "depotDossier.html", {"message": message})

def receptionDossierStudent(request):
    form = ContactForm()
    message_envoye = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            sujet = form.cleaned_data['sujet']
            message = form.cleaned_data['message']

            contenu_message = f"De: <{email}>\n\n{message}"

            send_mail(
                sujet,
                contenu_message,
                settings.EMAIL_HOST_USER,
                [email],# Mets ici ton adresse de réception
                fail_silently=False,
            )
            message_envoye = True
            
            
    receptions = depotDossierEtudiant.objects.all()
    annees = AnneeScolaire.objects.all()
    
    return render(request, 'receptionDossierStudent.html', {"receptions": receptions, "annees": annees, 'form': form, 'message_envoye': message_envoye})


def admission_Inscription(request):
    return render(request, 'admission_Inscription.html')


from .forms import ContactForm

def contact_view(request):
    form = ContactForm()
    message_envoye = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            sujet = form.cleaned_data['sujet']
            message = form.cleaned_data['message']

            contenu_message = f"De: {nom} <{email}>\n\n{message}"

            send_mail(
                sujet,
                contenu_message,
                settings.EMAIL_HOST_USER,
                ['alimoussaabakar03@gmail.com'],  # Mets ici ton adresse de réception
                fail_silently=False,
            )
            message_envoye = True

    return render(request, 'accueil/sendMail.html', {'form': form, 'message_envoye': message_envoye})

def connexion(request):
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        # matricule = request.POST['matricule']
        # nom = request.POST['password']
        
        if form.is_valid():
            utilisateur = form.get_user()
            login(request, utilisateur)
            if utilisateur.is_superuser:
                return redirect(reverse('secretaire:index'))
            return redirect('eleve:notes')
        else:
            messages.error(request, "identifiant ou mot de passe incorrect")
            
            
    else:
        form = ConnexionForm()
    return render(request, 'connexion.html', {"form": form})
        
    #     try:
    #         eleve = Etudiant.objects.get(matricule=matricule, nom=nom)
    #         # request.session['matricule'] = eleve.matricule  
    #         return redirect('eleve:notes', matricule=eleve.matricule)
    #     except Etudiant.DoesNotExist:
    #         # Gérer l'erreur si l'étudiant n'existe pas
    #         return render(request, 'accueil/connexion.html', {'erreur': "Identifiants incorrects"})
    # return render(request, 'accueil/connexion.html')

def deconnexion(request):
    logout(request)
    return redirect("pageAccueil")

# def traitement_login(request):
#     if request.method == "POST":
#         username = request.POST.get("matricule")
#         password = request.POST.get("nom")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request,user)
#             if user.is_superuser:
#                 return redirect(reverse('secretaire:index'))
#             elif user.groups.filter(name="Eleve").exists():
#                 return redirect('inscriptionPayement')
#         else:
#             return redirect('eleve:notes', matricule = username)
#             # return HttpResponse('Page non trouvée')

#     return render(request, 'connexion.html')

def formateur(request):
    enseignants = Enseignant.objects.all()
    contains = {'enseignants': enseignants}
    return render(request, 'accueil/formateur.html', contains)


# def contact(request):
#     return render(request, 'accueil/contact.html')

def prixDeClasse(request):
    classes = Classe.objects.all()
    couts = Cout.objects.filter(classe__in = classes)
    for cout in couts:
        coutAnnuel = cout.coutInscription + cout.coutScolarite + cout.fraisAssocie
        cout.coutScolarite = coutAnnuel
    contains = {'couts': couts}
    return render(request, 'accueil/prixDeClasse.html', contains)







