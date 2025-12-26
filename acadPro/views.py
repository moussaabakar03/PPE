
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required


from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from django.contrib import messages

from acadPro.forms import ConnexionForm
from secretaire.models import AnneeScolaire, Classe, Cout, Enseignant, Etudiant, Parent, depotDossierEtudiant
from acadPro.utils.decorators import parent_required, enseignant_required



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
            messages.info(request,"Veuillez télécharger votre CV.")
            return render(request, "depotDossier.html")

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
        messages.success(request,"Nous avons bien reçu votre demande. Vous recevrez un email de confirmation dans les prochaines heures avec les instructions pour la suite du processus.")
        return redirect('depotDossier')
    
    return render(request, "depotDossier.html")

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
        form = ConnexionForm(request.POST, request=request)  # ✅ on passe request ici

        if form.is_valid():
            utilisateur = form.get_user()
            login(request, utilisateur)

            if utilisateur.is_superuser:
                messages.success(request, f"Bienvenue {utilisateur}")
                return redirect(reverse('secretaire:index'))
            elif utilisateur.is_staff:
                messages.success(request, f"Bienvenue {utilisateur}")
                return redirect(reverse('comptable:indexComptable'))
            elif utilisateur.role == "parent":
                parent = get_object_or_404(Parent, utilisateur=utilisateur)
                messages.success(request, f"Bienvenue {parent.nom} {parent.prenom}")
                return redirect("parent")
            elif utilisateur.role == "enseignant":
                enseignant = Enseignant.objects.get(utilisateur=utilisateur)
                messages.success(request, f"Bienvenue {enseignant.nom} {enseignant.prenom}")
                return redirect("enseignant")
            elif utilisateur.role == "eleve":
                eleve = Etudiant.objects.get(utilisateur=utilisateur)
                messages.success(request, f"Bienvenue {eleve.nom} {eleve.prenom}")
                return redirect('eleve:notes')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect")

    else:
        form = ConnexionForm()
    
    return render(request, 'connexion.html', {"form": form})



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


@login_required
@parent_required 
def parent(request):
    
    # parent = get_object_or_404(Parent, utilisateur = request.user)
    # enfants = parent.etudiant.all()
    
    parent = Parent.objects.get(utilisateur=request.user)
    enfants = parent.etudiant.all()
    
    return render(request, "parent.html", {"parent": parent, "enfants": enfants})



@login_required
@enseignant_required 
def enseignant(request):
    return render(request, "enseignant.html")

