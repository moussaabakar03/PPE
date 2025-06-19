from collections import defaultdict
from django.contrib import messages
from datetime import timedelta, datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from . models import AnneeScolaire, Classe, Cours, Cout, Emargement, Etudiant, Enseignant, Evaluation, Inscription, Matiere, Messages, Parent, SalleDeClasse, cvEnseignant, depotDossierEtudiant
from django.utils.timezone import localtime
from django.db.models import Q



import random
import string
from django.utils.text import slugify


from django.contrib.auth.forms import UserCreationForm 
# from .form import CustomUserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

# @login_required
def index(request):
    inscriptions = Inscription.objects.all().count()
    enseignants = Enseignant.objects.count()
    contains = {'inscriptions': inscriptions, 'enseignants': enseignants}
    return render(request, 'index.html', contains)

def index3(request):
    return render(request, 'index3.html')

def index4(request):
    return render(request, 'index4.html')

def index5(request):
    return render(request, 'index5.html')

def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'login.html')


def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) # type: ignore
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm() # type: ignore
    return render(request, 'inscription.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('login')



#Année scolaire.

def ajoutAnneeScolaire(request):
    if request.method == 'POST':
        debut_str = request.POST.get('debutAnnee')
        fin_str = request.POST.get('finAnnee')

        try:
            debutAnnee = datetime.strptime(debut_str, '%Y-%m-%d').date()
            finAnnee = datetime.strptime(fin_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Format de date invalide.")
            return redirect('ajoutAnneeScolaire')

        # Vérifie que l'année de début est inférieure à celle de fin
        if debutAnnee >= finAnnee:
            messages.error(request, "L'année de début doit être inférieure à l'année de fin.")
            return redirect('ajoutAnneeScolaire')

        # Vérification : est-ce qu'une année scolaire avec ces années existe déjà ?
        if AnneeScolaire.objects.filter(
            debutAnnee__year=debutAnnee.year,
            fintAnnee__year=finAnnee.year
        ).exists():
            messages.error(request, f"L'année scolaire {debutAnnee.year}-{finAnnee.year} existe déjà.")
            return redirect('ajoutAnneeScolaire')

        # Création si OK
        annee = AnneeScolaire(debutAnnee=debutAnnee, fintAnnee=finAnnee)
        annee.save()
        messages.success(request, f"Année scolaire {debutAnnee.year}-{finAnnee.year} ajoutée avec succès.")
        return redirect('affichageAnneeScolaire')

    return render(request, 'ajoutAnneeScolaire.html')

def affichageAnneeScolaire(request):
    anneesScolaires = AnneeScolaire.objects.all()
    return render(request, 'affichageAnneeScolaire.html', {'anneesScolaires': anneesScolaires})

def modifierAnneeScolaire(request, id):
    anneeScolaire = AnneeScolaire.objects.get(id=id)
    
    if request.method == 'POST':
        debut_str = request.POST.get('debutAnnee')
        fin_str = request.POST.get('finAnnee')

        try:
            debutAnnee = datetime.strptime(debut_str, '%Y-%m-%d').date()
            finAnnee = datetime.strptime(fin_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Format de date invalide.")
            return redirect('affichageAnneeScolaire')

        # Vérifie que l'année de début est inférieure à celle de fin
        if debutAnnee >= finAnnee:
            messages.error(request, "L'année de début doit être inférieure à l'année de fin.")
            return redirect('affichageAnneeScolaire')

        # Vérification : est-ce qu'une année scolaire avec ces années existe déjà ?
        if AnneeScolaire.objects.filter(
            debutAnnee__year=debutAnnee.year,
            fintAnnee__year=finAnnee.year
        ).exists():
            messages.error(request, f"L'année scolaire {debutAnnee.year}-{finAnnee.year} existe déjà.")
            return redirect('affichageAnneeScolaire')


        anneeScolaire.debutAnnee = debutAnnee
        anneeScolaire.fintAnnee = finAnnee

        anneeScolaire.save()
        messages.success(request, f"Année scolaire {debutAnnee.year}-{finAnnee.year} modifiée avec succès.")
        return redirect('affichageAnneeScolaire')
    
    return render(request, 'modifierAnneeScolaire.html', {'anneeScolaire': anneeScolaire})

def supprimerAnneeScolaire(request, id):
    anneeScolaire = AnneeScolaire.objects.get(id=id)
    anneeScolaire.delete()
    return redirect('affichageAnneeScolaire')


#Etudiant
def all_student(request):
    inscription = Inscription.objects.all()
    if request.method == 'POST':
        matricule = request.POST['matricule']
        nom = request.POST.get('nom')        
        
        etudiant = Etudiant.objects.filter(matricule__icontains=matricule, nom__icontains=nom)
        
        context = {'etudiants': etudiant, 'inscription': inscription}
        return render(request, 'all-student.html', context)
    else:
        etudiant = Etudiant.objects.all()
        context = {'etudiants': etudiant, 'inscription': inscription}
        return render(request, 'all-student.html', context)

def generate_matricule(nom):
    prefix = slugify(nom)[:4].upper()  # Les 4 premières lettres du nom, en majuscules
    suffix = ''.join(random.choices(string.digits, k=4))  # 4 chiffres aléatoires
    return f"{prefix}{suffix}"

def admit_form(request):
    salles = SalleDeClasse.objects.all()
    parentss = Parent.objects.all()

    if request.method == "POST":
        nom = request.POST["nom"]
        prenom = request.POST["prenom"]
        genre = request.POST["genre"]
        date_naissance = request.POST["date_naissance"]
        groupe_sanguin = request.POST["groupe_sanguin"]
        mail = request.POST["mail"]
        telephone = request.POST["telephone"]
        nationnalite = request.POST["nationnalite"]
        photo = request.FILES.get("photo")
        parent = request.POST.get("parent")

        # Génération du matricule
        matricule = generate_matricule(nom)

        # Assurer unicité du matricule
        while Etudiant.objects.filter(matricule=matricule).exists():
            matricule = generate_matricule(nom)

        parent_id = Parent.objects.get(pk=int(parent))

        Etudiant.objects.create(
            nom=nom,
            prenom=prenom,
            parent=parent_id,
            matricule=matricule,
            genre=genre,
            date_naissance=date_naissance,
            groupe_sanguin=groupe_sanguin,
            mail=mail,
            telephone=telephone,
            nationnalite=nationnalite,
            photo=photo
        )

        return redirect("all-student")

    return render(request, "admit-form.html", {"salles": salles, "parentss": parentss})

def modifier_student(request, matricule):
    
    mtrcle = mtrcle = get_object_or_404(Etudiant, matricule=matricule)
    
    groupes_sanguins = ["A+", "A-", "B+", "B-", "O+", "O-"]
    sections = SalleDeClasse.objects.all()

    if request.method == "POST":
        mtrcle.nom = request.POST["nom"]
        mtrcle.prenom = request.POST["prenom"]
        parent_id = request.POST["parent"]
        mtrcle.matricule = request.POST["matricule"]
        mtrcle.genre = request.POST["genre"]
        mtrcle.date_naissance = request.POST["date_naissance"]
        mtrcle.groupe_sanguin = request.POST["groupe_sanguin"]
        mtrcle.mail = request.POST["mail"]
        # mtrcle.niveau = request.POST["niveau"]
        mtrcle.telephone = request.POST["telephone"]
        mtrcle.nationnalite = request.POST["nationnalite"]
        mtrcle.photo = request.FILES.get("photo")
        # mtrcle.salleDeClasse = SalleDeClasse.objects.get(pk=int(request.POST["salleDeClasse"]))

        mtrcle.parent = Parent.objects.get(pk=int(parent_id))
        
        mtrcle.save()
        return redirect("all-student")
    

    return render(request, "modifier-student.html", {
        "student": mtrcle,
        "groupes_sanguins": groupes_sanguins,
        "sections": sections,
        "parents": Parent.objects.all(),
    })

def supprimer_student(request, matricule):
    mtrcle = Etudiant.objects.get(matricule = matricule)
    if request.method == "GET":
        mtrcle.delete()
        return redirect("all-student")
    
def student_promotion(request):
    return render(request, 'student-promotion.html')

def student_detail(request, matricule):
    etudiant = Etudiant.objects.get(matricule = matricule)
    inscrits = etudiant.inscriptions.all()
    # parent = Etudiant.objects.get(parent = etudiant.parent)
    annees = AnneeScolaire.objects.all().order_by("-id")
    context = {"etudiant": etudiant, "inscrits": inscrits, "annees": annees}
    return render(request, 'student-details.html', context)

def detailEtudiant(request, matricule, id):
    etudiant = Etudiant.objects.get(matricule=matricule)
    parent = Parent.objects.get(id=id)
    inscriptions = etudiant.inscriptions.all()
    

    somme_notes_ponderees = 0.0
    somme_coefficients = 0
    
    if request.method == "POST":
                
        matiere = request.POST['matiere']
        trimestre = request.POST['trimestre']
        typeEvaluation = request.POST['typeEvaluation']
        
        evaluations = etudiant.evaluations.all()
        
        if matiere:
            evaluations = etudiant.evaluations.filter(cours__matiere__nom__contains = matiere.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.matiere.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        elif trimestre:
            evaluations = etudiant.evaluations.filter(trimestre__contains = trimestre.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.matiere.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        elif typeEvaluation:
            evaluations = etudiant.evaluations.filter(typeEvaluation__contains = typeEvaluation.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.matiere.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        elif matiere and trimestre and typeEvaluation:
            evaluations = etudiant.evaluations.filter(typeEvaluation__contains = typeEvaluation, trimestre__contains = trimestre, cours__matiere__nom__contains = matiere.strip())
            for evaluation in evaluations:
                coefficient = evaluation.cours.matiere.coefficient
                somme_notes_ponderees += float(evaluation.note) * coefficient
                somme_coefficients += coefficient
        else:
            messages.error(request, "Aucune donnée trouvées!!!")
        moyenne = round(somme_notes_ponderees / somme_coefficients, 2) if somme_coefficients != 0 else 0.0
        
        context = {
            "etudiant": etudiant,
            "parent": parent,
            "inscriptions": inscriptions,
            "evaluations": evaluations,
            "moyenne": moyenne,
            }
        return render(request, 'detailEtudiant.html', context)
        
        
    else:    
        evaluations = etudiant.evaluations.all()
        for evaluation in evaluations:
            coefficient = evaluation.cours.matiere.coefficient
            somme_notes_ponderees += float(evaluation.note) * coefficient
            somme_coefficients += coefficient

        moyenne = round(somme_notes_ponderees / somme_coefficients, 2) if somme_coefficients != 0 else 0.0

        context = {
            "etudiant": etudiant,
            "parent": parent,
            "inscriptions": inscriptions,
            "evaluations": evaluations,
            "moyenne": moyenne
        }
        return render(request, 'detailEtudiant.html', context)



#teacher
def all_teacher(request):
    enseignants = Enseignant.objects.all()
    content = {"enseignants": enseignants }
    return render(request, 'all-teacher.html', content)

def add_teacher(request):
    if request.method == "POST":
        nom = request.POST["nom"]
        prenom = request.POST["prenom"]
        sexe = request.POST["sexe"]
        date_naissance = request.POST["date_naissance"]
        diplome = request.POST["diplome"]
        profession = request.POST["profession"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        photo = request.FILES.get("photo")  
        
        lieuDeNaissance = request.POST["lieuDeNaissance"]
        salaire = request.POST["salaire"]
        typeDeContrat = request.POST["typeDeContrat"]
        date_debut_contrat = request.POST["date_debut_contrat"]
        date_fin_contrat = request.POST["date_fin_contrat"]
        matricule = generate_matricule(nom)
        while (Enseignant.objects.filter( matricule = matricule).exists()):
            matricule = generate_matricule(nom)

    
        Enseignant.objects.create( matricule = matricule, nom = nom, prenom = prenom, profession = profession, tel = phone, 
                                diplome = diplome,  photo = photo , date_naissance = date_naissance, sexe = sexe, mail = email,
                                lieuDeNaissance= lieuDeNaissance, salaire = salaire, typeDeContrat = typeDeContrat, 
                                date_debut_contrat = date_debut_contrat, date_fin_contrat = date_fin_contrat)
        return redirect("all-teacher")
    return render(request, 'add-teacher.html')

def teacher_detail(request):
    return render(request, 'teacher-details.html')

def modifier_teacher(request, matricule):
    enseignant = Enseignant.objects.get(matricule = matricule)
    groupes_sanguins = ["A+", "A-", "B+", "B-", " AB+", "AB-", "O+", "O-"]
    if request.method == "POST":
        enseignant.matricule = request.POST["matricule"]
        enseignant.nom = request.POST["nom"]
        enseignant.prenom = request.POST["prenom"]
        enseignant.profession = request.POST["profession"]
        enseignant.tel = request.POST["phone"]
        enseignant.diplome = request.POST["diplome"]
        enseignant.photo = request.FILES.get("photo")
        enseignant.date_naissance = request.POST["date_naissance"]
        enseignant.sexe = request.POST["sexe"]
        enseignant.typeDeContrat = request.POST["typeContrat"]
        enseignant.mail = request.POST["email"]
        enseignant.save()
        return redirect("all-teacher")
    return render(request, 'modifier-teacher.html', {"enseignant": enseignant, "groupes_sanguins": groupes_sanguins})

def supprimer_teacher(request, matricule):
    enseignant = Enseignant.objects.get(matricule = matricule)
    enseignant.delete()
    return redirect("all-teacher")

def detailEnseignant(request, matricule):
    enseignant = Enseignant.objects.get(matricule = matricule)
    context = {"enseignant": enseignant}
    return render(request, 'detaitEnseignant.html', context)

def cvEnseignants(request, id):
    if request.method == "POST":
        cv = request.FILES.get("cv")
        enseignant = Enseignant.objects.get(id = id)

        cvEnseignant.objects.create(
            cv = cv,
            enseignant = enseignant
        )
        return redirect('detailEnseignant', matricule = enseignant.matricule)
    return render(request, 'cvEnseignant.html')

def listeCvEnseignant(request, id):
    enseignant = Enseignant.objects.get(id = id)
    cvEnseignants = cvEnseignant.objects.filter(enseignant = enseignant)
    return render(request, 'listeCvEnseignant.html', {"cvEnseignants" : cvEnseignants, "enseignant" : enseignant})

def suppCvEnseignant(request, id):
    cvAsupp = cvEnseignant.objects.get(id = id)
    enseignant = cvAsupp.enseignant
    cvAsupp.delete()
    messages.success (request, "cv supprimé avec succès")
    return redirect('listeCvEnseignant', id = enseignant.id)


#parent
def all_parents(request):
    parents = Parent.objects.all()
    return render(request, 'all-parents.html', {"parents": parents})

def ajout_parents(request):
    if request.method == "POST":
        nom = request.POST["nom"]
        prenom = request.POST["prenom"]
        genre = request.POST["genre"]
        telephone = request.POST["telephone"]
        email = request.POST["email"]
        profession = request.POST.get("profession", "")
        lien_de_parente = request.POST["lien_de_parente"]
        photo = request.FILES.get("photo")
        
        # Création de l'objet Parent
        Parent.objects.create(
            nom=nom,
            prenom=prenom,
            genre=genre,
            telephone=telephone,
            email=email,
            profession=profession,
            lien_de_parente=lien_de_parente,
            photo=photo
        )

        return redirect("all-parents")  # Redirige vers la liste des parents (à adapter selon ton URLconf)
    return render(request, 'add-parents.html')

def modifier_parent(request, id):
    parent = Parent.objects.get(id = id)
    if request.method == "POST":
        parent.nom = request.POST["nom"]
        parent.prenom = request.POST["prenom"]
        parent.genre = request.POST["genre"]
        parent.telephone = request.POST["telephone"]
        parent.email = request.POST["email"]
        parent.profession = request.POST.get("profession", "")
        parent.lien_de_parente = request.POST["lien_de_parente"]

        if "photo" in request.FILES:
            parent.photo = request.FILES["photo"]
        
        parent.save()
    
        return redirect("all-parents")
    
    return render(request, 'modifierParent.html', {"parent": parent})

def supprimer_parent(request, id):
    Parent.objects.get(id =id).delete()
    return redirect("all-parents")  # Redirige vers la liste des parents


#Matiere
def all_class(request):
    if request.method == "POST":
        nom = request.POST["nom"]
        # niveau = request.POST["niveau"]
        # classe = Classe.objects.get(classe = niveau)
        
        matiere = Matiere.objects.filter(
                nom__icontains=nom
            )

        return render(request, 'all-class.html', {"matieres": matiere})
    else:
        matiere = Matiere.objects.all()
        return render(request, 'all-class.html', {"matieres": matiere})

def add_class(request):
    # enseignants = Enseignant.objects.all()
    # niveaux = Classe.objects.all()
    # content = {"enseignants": enseignants, "niveaux": niveaux}
    if request.method == "POST":
        nom = request.POST["nom"]
        # niveau = request.POST["niveau"]
        coefficient = request.POST["coefficient"]
        description = request.POST.get("description", "")  # facultatif
        # enseignant_id = request.POST["enseignant"]
        # enseignant = Enseignant.objects.get(pk=int(enseignant_id))
        # classe = Classe.objects.get(pk=int(niveau))
        
        if Matiere.objects.filter(nom=nom).exists():
            messages.error(request, "Cette matière existe déjà")
        else:
            Matiere.objects.create(
                nom=nom,
                coefficient=coefficient,
                description=description,
            )
            # messages.success(request, "Matière ajoutée avec succès")
            return redirect("all-class")

    return render(request, 'add-class.html')

def supprimer_matiere(request, id):
    Matiere.objects.get(id=id).delete()
    return redirect("all-class")

def modifier_matiere(request, id):
    matiere = Matiere.objects.get(id=id)

    if request.method == "POST":
        matiere.nom = request.POST["nom"]
        # matiere.niveau = request.POST["niveau"]
        matiere.code = request.POST["code"]
        matiere.coefficient = request.POST["coefficient"]
        matiere.description = request.POST.get("description", "") 

        # enseignant_id = request.POST["enseignant"]
        # matiere.enseignant = Enseignant.objects.get(pk=int(enseignant_id))

        # niveau_id = request.POST["niveau"]
        # matiere.niveau = Classe.objects.get(pk=int(niveau_id))

        matiere.save()
        return redirect("all-class")
    return render(request, "modifierMatiere.html", {
        "matiere": matiere,
    })



#salle de classe
def all_salle(request):
    salles = SalleDeClasse.objects.all()
    etudiant = Etudiant.objects.all()
    annees = AnneeScolaire.objects.all().order_by('-id')
    return render(request, 'all-salle.html', {"salles": salles, "etudiants": etudiant, "annees": annees})

def add_salle(request):
    niveau = Classe.objects.all()
    if request.method == "POST":
        nom = request.POST["nom"]
        capacite = int(request.POST["capacite"])
        niveau = request.POST["niveau"]
        emplacement = request.POST.get("emplacement", "")  

        classe = Classe.objects.get(pk=int(niveau))
        
        if SalleDeClasse.objects.filter(nom = nom, niveau=classe).exists():
            messages.error(request, f"La salle '{nom}' dont la capacité est '{capacite}' existe deja! Veillez modifier la salle existante ou changer le nom de la salle.")
            return redirect("add-salle")
        
        
        SalleDeClasse.objects.create(
            nom=nom,
            capacite=capacite,
            emplacement=emplacement,
            niveau = classe
        )

        return redirect("all-salle") 

    return render(request, 'add-salle.html', {"niveaux": niveau})

def modifierSalle(request, nom):
    salle = SalleDeClasse.objects.get(nom=nom)

    if request.method == "POST":
        salle.nom = request.POST["nom"]
        salle.capacite = int(request.POST["capacite"])
        niveau_id = request.POST["niveau"]
        salle.emplacement = request.POST.get("emplacement", "")  # champ facultatif

        salle.niveau = Classe.objects.get(pk=int(niveau_id))

        salle.save()
        return redirect('all-salle')

    return render(request, 'modifier_Salle.html', {"salle": salle, "niveaux": Classe.objects.all()})

def supprimerSalle(request, id):
    SalleDeClasse.objects.get(id=id).delete()
    return redirect('all-salle')

def studentParSalle(request, id, id2):
    salle = SalleDeClasse.objects.get(pk=id)
    anneeScolaire = AnneeScolaire.objects.get(id = id2)
    if request.method == 'POST':
        matricule = request.POST['matricule']
        nom = request.POST.get('nom')        
        
        inscrit = Inscription.objects.filter(salleClasse=salle, anneeAcademique = anneeScolaire)
        
        inscrits = inscrit.filter(etudiant__matricule__icontains=matricule, etudiant__nom__icontains=nom)
        nombre = inscrits.count()
        return render(request, 'studentParSalle.html', {"salle": salle, 'inscrits': inscrits, 'nombre': nombre, 'annee': anneeScolaire})
    else:
        inscrits = Inscription.objects.filter(salleClasse=salle, anneeAcademique = anneeScolaire)
        nombre = inscrits.count()
        return render(request, 'studentParSalle.html', {"salle": salle, 'inscrits': inscrits, 'nombre': nombre, 'annee': anneeScolaire})

def listePresence(request, id, id2):
    salle = SalleDeClasse.objects.get(pk=id)
    anneeScolaire = AnneeScolaire.objects.get(id = id2)

    if request.method == 'POST' and 'dateHeureDebut' in request.POST:
        dateHeureDebut = request.POST.get("dateHeureDebut")
        commentaire = request.POST.get("commentaire")

        inscrits = Inscription.objects.filter(salleClasse=salle, anneeAcademique = anneeScolaire)

        for inscrit in inscrits:
            etudiant = inscrit.etudiant
            presence_key = f"presence_{etudiant.matricule}"
            presence_val = request.POST.get(presence_key)

            if presence_val in ['P', 'A']: 
                Emargement.objects.create(
                    salleClasse=salle,
                    inscrits=inscrit,
                    dateHeureDebut=dateHeureDebut,
                    commentaire=commentaire,
                    presence=(presence_val == 'P')
                )

        # messages.success(request, "Liste de présence enregistrée avec succès.")
        inscrits = Inscription.objects.filter(salleClasse=salle, anneeAcademique = anneeScolaire)
        nombre = inscrits.count()
        # return render(request, 'listePresence.html', {"salle": salle, 'inscrits': inscrits, 'nombre': nombre})
        return redirect('listePresencePasse', id=id, id2 =id2)

    matricule = request.POST.get('matricule', '')
    nom = request.POST.get('nom', '')
    inscrits = Inscription.objects.filter(salleClasse=salle, anneeAcademique = anneeScolaire).filter(
        etudiant__matricule__icontains=matricule,
        etudiant__nom__icontains=nom
    )
    nombre = inscrits.count()
    return render(request, 'listePresence.html', {"salle": salle, 'inscrits': inscrits, 'nombre': nombre, "annee": anneeScolaire})

def listePresencePasse(request, id, id2):
    salleClasse = SalleDeClasse.objects.get(id=id)
    anneeScolaire = AnneeScolaire.objects.get(id=id2)

    inscrits = Inscription.objects.filter(anneeAcademique=anneeScolaire)

    emargements = Emargement.objects.filter(
        salleClasse=salleClasse,
        inscrits__in=inscrits
    ).order_by('-dateHeureDebut')

    filtre = request.POST.get('filtre')
    if filtre:
        emargements = emargements.filter(
            Q(inscrits__etudiant__nom__icontains=filtre) |
            Q(inscrits__etudiant__prenom__icontains=filtre) |
            Q(inscrits__etudiant__matricule__icontains=filtre)
        )

    #  Regrouper les émargements par date
    emargements_par_date = defaultdict(list)
    for em in emargements:
        date_str = localtime(em.dateHeureDebut).date().strftime('%Y-%m-%d')
        emargements_par_date[date_str].append(em)

    return render(request, 'listePresencePasse.html', {
        "emargements_par_date": dict(emargements_par_date),
        "salleClasse": salleClasse,
        "anneeScolaire": anneeScolaire
    })

def presenceEtudiant(request, matricule):
    etudiant = Etudiant.objects.get(matricule=matricule)
    inscrits = etudiant.inscriptions.all()
    # parent = Etudiant.objects.get(parent = etudiant.parent)
    emargements = Emargement.objects.filter(inscrits__in=inscrits).order_by('-id')
    
    
    emargements_par_date = defaultdict(list)
    for em in emargements:
        date_str = localtime(em.dateHeureDebut).date().strftime('%Y-%m-%d')
        emargements_par_date[date_str].append(em)

    return render(request, 'presenceStudent.html', { "emargements_par_date": dict(emargements_par_date),"etudiant": etudiant, "emargements": emargements})

def emploiDuTemps(request):
    return render(request, "emploiTemps.html")

def ajoutEmploiTemps(request):
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    heures = ["1h-2h", "2h-3h", "3h-4h", "4h-5h"]
    cours = Cours.objects.all()
    return render(request, "ajoutEmploiTemps.html", {
        "jours": jours,
        "heures": heures,
        "cours": cours,
    })


# def ajout_emploi_temps(request):
#     jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
#     heures = ["1h-2h", "2h-3h", "3h-4h"]
#     cours = Cours.objects.all()

#     if request.method == "POST":
#         emploi_du_temps = []
#         erreurs = False

#         for i, heure in enumerate(heures, start=1):
#             for jour in jours:
#                 champ = f"{jour.lower()}_{i}"
#                 cours_id = request.POST.get(champ)

#                 if not cours_id:
#                     messages.error(request, f"Le champ {champ} est requis.")
#                     erreurs = True
#                     continue

#                 try:
#                     cours_obj = Cours.objects.get(id=cours_id)
#                 except Cours.DoesNotExist:
#                     messages.error(request, f"Cours introuvable pour {champ}.")
#                     erreurs = True
#                     continue

#                 emploi_du_temps.append({
#                     "jour": jour,
#                     "heure": heure,
#                     "cours": cours_obj
#                 })

#         if not erreurs:
#             for ligne in emploi_du_temps:
#                 EmploiDuTemps.objects.create(
#                     jour=ligne["jour"],
#                     heure=ligne["heure"],
#                     cours=ligne["cours"]
#                 )
#             messages.success(request, "Emploi du temps enregistré avec succès.")
#             return redirect("liste_emplois")  # ou la vue de ton choix

#     return render(request, "emploi/ajoutEmploiTemps.html", {
#         "jours": jours,
#         "heures": heures,
#         "cours": cours,
#     })


#Classe(niveau)
def all_niveau(request):
    niveaux = Classe.objects.all()
    return render(request, 'all-niveau.html', {"niveaux": niveaux})

def add_niveau(request):
    if request.method == "POST":
        classe = request.POST["classe"]
        # capacite = int(request.POST["capacite"])
        # scolarite = request.POST["scolarite"]
        
        if Classe.objects.filter(classe = classe):
             messages.error(request, f"Ce niveau ({classe}) existe déjà")
             return redirect("add_niveau")
        Classe.objects.create(
            classe = classe,
            # capacite = capacite,
            # scolarite = scolarite
        )
        return redirect("all_niveau")
    return render(request, 'add-niveau.html')

def modifierNiveau(request, id):
    classe = Classe.objects.get(pk=id)
    if request.method == "POST":
        classe.classe = request.POST["classe"]
        classe.save()
        return redirect('all_niveau')
    return render(request, 'modifier-niveau.html', {"classe": classe})

def supprimerNiveau(request, id):
    Classe.objects.get(pk=id).delete()
    return redirect('all_niveau')


def all_inscription(request):
    if request.method == "POST":
        matricule = request.POST.get("matricule", "").strip()
        anneeScolaire = request.POST.get("anneeScolaire", "").strip()
        niveau = request.POST.get("niveau", "").strip()

        inscriptions = Inscription.objects.all()

        if matricule:
            inscriptions = inscriptions.filter(etudiant__matricule__icontains=matricule)

        if niveau:
            try:
                classe = Classe.objects.get(pk=int(niveau))
                inscriptions = inscriptions.filter(salleClasse__niveau=classe)
            except (ValueError, Classe.DoesNotExist):
                pass

        if anneeScolaire:
            try:
                anneeAcademique = AnneeScolaire.objects.get(pk=int(anneeScolaire))
                inscriptions = inscriptions.filter(anneeAcademique=anneeAcademique)
            except (ValueError, AnneeScolaire.DoesNotExist):
                pass

        return render(request, 'all-inscription.html', {
            "inscriptions": inscriptions,
            "anneeScolaires": AnneeScolaire.objects.all(),
            "niveaux": Classe.objects.all()
        })
    
    else:
        inscriptions = Inscription.objects.select_related('etudiant', 'salleClasse__niveau').all()
        return render(request, 'all-inscription.html', {
            "inscriptions": inscriptions,
            "anneeScolaires": AnneeScolaire.objects.all(),
            "niveaux": Classe.objects.all()
        })

def ajoutInscription(request):
    if request.method == "POST":
        etudiant_id = request.POST["etudiant"]
        salleClasse_id = request.POST["salleClasse"]
        # coutA = request.POST["coutA"]
        montantVerse = request.POST["montantVerse"]
        anneeScolaire = request.POST["anneeScolaire"]
        
        etudiant = Etudiant.objects.get(pk=int(etudiant_id))
        salleDeClasse = SalleDeClasse.objects.get(pk=int(salleClasse_id))
        anneeAcademique = AnneeScolaire.objects.get(pk=int(anneeScolaire))
        
        if Inscription.objects.filter(etudiant = etudiant, anneeAcademique = anneeAcademique).exists():
            messages.error(request, "Cet élève est déjà inscrit pour cette année scolaire.")
            return redirect("add_inscription")
        
        # if Cout.objects.get(classe = salleDeClasse.niveau).exists():
        #     cout = Cout.objects.get(classe = salleDeClasse.niveau)

        #     if float(montantVerse) <= float(cout.coutInscription):  
        #         Inscription.objects.create(
        #             etudiant = etudiant,
        #             salleClasse = salleDeClasse,
        #             montantVerse = montantVerse,
        #             anneeAcademique = anneeAcademique
        #         )
        #         return redirect("all_inscription")
        #     else:
        #         messages.error(request, "Le montant versé doit être inférieur ou égal au cout d'inscription ")
        #         return redirect("add_inscription")
        # else:
        Inscription.objects.create(
            etudiant = etudiant,
            salleClasse = salleDeClasse,
            montantVerse = montantVerse,
            anneeAcademique = anneeAcademique
        )
        return redirect("all_inscription")
       
    context = {
        'etudiants': Etudiant.objects.all(),
        'salles': SalleDeClasse.objects.all(),
        'anneeScolaires': AnneeScolaire.objects.all(),
    }
    return render(request, 'add-inscription.html', context)
    
def delete_inscription(request, id):
    inscription = Inscription.objects.get(pk=id)
    inscription.delete()
    return redirect("all_inscription")

def modifierInscription(request, id):
    inscription = Inscription.objects.get(pk=id)
    if request.method == 'POST':
        etudiant = request.POST["etudiant"]
        salleDeClasse = request.POST["salleClasse"]
        # inscription.coutA = request.POST["coutA"]
        inscription.montantVerse = request.POST["montantVerse"]
        
        inscription.etudiant_id = Etudiant.objects.get(id =etudiant)
        inscription.salleClasse_id = SalleDeClasse.objects.get(id =salleDeClasse)
        
        inscription.save()
        return redirect("all_inscription")
    context = {
        'etudiants': Etudiant.objects.all(),
        'salles': SalleDeClasse.objects.all(),
        'inscription': inscription
    }
    return render(request, 'modifier-inscription.html', context)
        


#Cours

def all_cours(request):
    cours = Cours.objects.all()
    
    if request.method == "POST":
        matiere = request.POST['matiere']
        classe = request.POST['classe']
        enseignant = request.POST['enseignant']
        
        if matiere:
            cours = Cours.objects.filter(matiere__nom = matiere.strip())
        if classe:
            cours = Cours.objects.filter(classe__classe = classe.strip())
        if enseignant:
            cours = Cours.objects.filter(enseignant__nom = enseignant.strip())
        
        return render(request, 'all-cours.html', {'cours_list': cours})
    
    else:
        context = {'cours_list': cours}
        return render(request, 'all-cours.html', context)

def ajoutCours(request):
    if request.method == 'POST':
        matiere_nom = request.POST["matiere"]
        enseignant_nom = request.POST["enseignant"]
        classe_nom = request.POST["classe"]
        # date_debut = request.POST["dateDebutCours"]
        # duree = request.POST["dureeCours"]
        trimestre = request.POST["trimestre"]
        etat = request.POST["etat"]
        anneeScolaire = request.POST["anneeScolaire"]

        # Récupérer les objets liés à partir des noms
        matiere = Matiere.objects.get(pk=int(matiere_nom))
        # enseignant = Enseignant.objects.get(nom=enseignant_nom.split()[0], prenom=enseignant_nom.split()[1])
        enseignant = Enseignant.objects.get(pk=int(enseignant_nom))
        classe = Classe.objects.get(pk=int(classe_nom))
        anneeAcademique = AnneeScolaire.objects.get(pk=int(anneeScolaire))

        if Cours.objects.filter( enseignant=enseignant, classe=classe, anneeScolaire=anneeAcademique, matiere=matiere).exists():
            messages.error(request, "Cours déjà existant")
            return redirect('add-cours')
        else:
            Cours.objects.create(
                matiere=matiere,
                enseignant=enseignant,
                classe=classe,
                dateDebutCours=timezone.now(),
                trimestre=trimestre,
                etat=etat,
                anneeScolaire=anneeAcademique
            )
            messages.success(request, "Cours ajouté avec succès")
            return redirect('all-cours')  

    context = {
        'matieres': Matiere.objects.all(),
        'enseignants': Enseignant.objects.all(),
        'classes': Classe.objects.all(),
        'anneeScolaires': AnneeScolaire.objects.all(),
    }
    return render(request, 'add-cours.html', context)

def modifier_cours(request, pk):
    cours = Cours.objects.get(pk=pk)
    if request.method == 'POST':
        matiere_nom = request.POST["matiere"]
        enseignant_nom = request.POST["enseignant"]
        classe_nom = request.POST["classe"]
        cours.dateDebutCours = request.POST["dateDebutCours"]
        cours.dureeCours = request.POST["dureeCours"]
        cours.trimestre = request.POST["trimestre"]
        cours.etat = request.POST["etat"]
        anneeScolaire = request.POST["anneeScolaire"]

        # Récupérer les objets liés à partir des noms
        cours.matiere = Matiere.objects.get(nom=matiere_nom)
        # enseignant = Enseignant.objects.get(nom=enseignant_nom.split()[0], prenom=enseignant_nom.split()[1])
        cours.enseignant = Enseignant.objects.get(pk=int(enseignant_nom))
        cours.classe = Classe.objects.get(pk=int(classe_nom))
        cours.anneeScolaire = AnneeScolaire.objects.get(pk=int(anneeScolaire))
        
        cours.save()
        return redirect('all-cours')
    context = {'cours': cours, 'matieres': Matiere.objects.all(), 'enseignants': Enseignant.objects.all(), 'classes': Classe.objects.all(), 'anneeScolaires': AnneeScolaire.objects.all()}
    return render(request, 'modifier-cours.html', context)

def supprimer_cours(request, pk):
    Cours.objects.get(pk=pk).delete()
    return redirect('all-cours')



#Evaluation
def all_evaluation(request):
    # niveaux = Classe.objects.all()
    # evaluations = Evaluation.objects.all()
    # cours = Cours.objects.all()
    salleDeClasse = SalleDeClasse.objects.all()
    # context = {'evaluations': evaluations, 'niveaux': niveaux}
    return render(request, 'all-evaluation.html', {'salleDeClasses': salleDeClasse})

def supprimer_evaluation(request, pk):
    Evaluation.objects.get(pk=pk).delete()
    return redirect('all_evaluation')

def modifier_evaluation(request, id):
    evaluation = Evaluation.objects.get(id=id)
    # etudiant = Etudiant.objects.get(id=id)
    
    if request.method == 'POST':
        cours_id = request.POST["cours"]
        etudiant_id = request.POST["etudiant"]
        
        evaluation.trimestre = request.POST["trimestre"]
        evaluation.typeEvaluation = request.POST["typeEvaluation"]
        evaluation.dateEvaluation = request.POST["dateEvaluation"]
        evaluation.note = request.POST["note"]
        evaluation.pourcentage = request.POST["pourcentage"]

        evaluation.cours = get_object_or_404(Cours, id=cours_id)
        evaluation.etudiant = get_object_or_404(Etudiant, id=etudiant_id)

        evaluation.save()
        
        return redirect('all_evaluation')
    
    cours_list = Cours.objects.all()

    context = {
        'cours_list': cours_list,
        # 'etudiant': etudiant,
        'evaluation': evaluation
    }
    return render(request, 'modifier-evaluation.html', context)

def evaluation_groupee(request, id, id1, id2):
    # classe = Classe.objects.get(id=id)
    anneeScolaire = AnneeScolaire.objects.get(id=id2)
    salleClasse = SalleDeClasse.objects.get(id=id)
    inscrits = Inscription.objects.filter(
        salleClasse=salleClasse, anneeAcademique =anneeScolaire.id
    ).select_related('etudiant', 'salleClasse')

    # matieres = Matiere.objects.filter(niveau=classe)
    # salle = SalleDeClasse.objects.get(niveau=classe)
    courrs = Cours.objects.filter(classe__id = id1, anneeScolaire__id = anneeScolaire.id)
    
    if request.method == 'POST':
        trimestre = request.POST["trimestre"]
        cours_id = request.POST["cours"]
        typeEvaluation = request.POST["typeEvaluation"]
        pourcentage = request.POST["pourcentage"]
        cours = Cours.objects.get(pk=int(cours_id))

        for inscrit in inscrits:
            note_input_name = f"note_{inscrit.etudiant.id}"
            note_val = request.POST.get(note_input_name)

            if note_val:  
                Evaluation.objects.create(
                    cours=cours,
                    etudiant=inscrit.etudiant,
                    typeEvaluation=typeEvaluation,
                    note=note_val,
                    trimestre=trimestre,
                    pourcentage =pourcentage
                )

        return redirect('all_evaluation')  

    context = {
        # 'matieres': matieres,
        # 'salle': salle,
        'salleClasse': salleClasse,
        'inscrits': inscrits,
        'courrs': courrs,
    }
    return render(request, 'liste_inscrits_par_classe.html', context)

def selectClasseEvaluation(request):
    # classe = Classe.objects.all()
    salleClasse = SalleDeClasse.objects.all()
    annee = AnneeScolaire.objects.all().order_by('-id')
    return render(request, 'selectClasseEvaluation.html', {'salleClasses': salleClasse, 'annees': annee})

def selectClasse(request):
    salleClasses = SalleDeClasse.objects.all()
    return render(request, 'selectClasse.html', {'salleClasses': salleClasses, 'annees': AnneeScolaire.objects.all().order_by('-id')})

def filtre_evaluation(request, id):
    salle = get_object_or_404(SalleDeClasse, id=id)
    classe = salle.niveau

    evaluation = Evaluation.objects.filter(cours__classe=classe).order_by('-id')

    if request.method == 'POST':
        typeEvaluation = request.POST.get('typeEvaluation')
        nom = request.POST.get('nom')
        matiere = request.POST.get('matiere')
        trimestre = request.POST.get('trimestre')

        if nom:
            evaluation = evaluation.filter(etudiant__nom__icontains=nom)
        if typeEvaluation:
            evaluation = evaluation.filter(typeEvaluation__icontains=typeEvaluation)
        if trimestre:
            evaluation = evaluation.filter(trimestre__icontains=trimestre)
        if matiere:
            evaluation = evaluation.filter(cours__matiere__nom__icontains=matiere)

    context = {'evaluations': evaluation, 'salle':salle, 'etudiants': Etudiant.objects.all(), 'annees': AnneeScolaire.objects.all()}
    return render(request, 'filtre-evaluation.html', context)

        
def note_individuelle(request, id, id2):
    salleClasse = SalleDeClasse.objects.get(id=id)
    annee = AnneeScolaire.objects.get(id=id2)
    
    inscrits = Inscription.objects.filter(
        salleClasse = salleClasse,
        anneeAcademique = annee,
    ).select_related('etudiant', 'salleClasse')

    # matieres = Matiere.objects.filter(niveau=classe)
    # salle = SalleDeClasse.objects.get(niveau=classe)
    # courrs = Cours.objects.filter(classe=classe)
   
    context = {
        'salleClasse': salleClasse,
        'inscrits': inscrits,
        'annee': annee,
    }
    return render(request, 'note-individuelle.html', context)

def ajout_note_individuelle(request, id, id1, id2):
    etudiant = Etudiant.objects.get(id=id)
    
    if request.method == 'POST':
        cours_id = request.POST["cours"]
        trimestre = request.POST["trimestre"]
        type_evaluation = request.POST["typeEvaluation"]
        # date_evaluation = request.POST["dateEvaluation"]
        note = request.POST["note"]
        etudiant_id = request.POST["etudiant"]
        pourcentage = request.POST["pourcentage"]

        cours = get_object_or_404(Cours, id=cours_id)
        etudiants = get_object_or_404(Etudiant, id=etudiant_id)

        Evaluation.objects.create(
            cours=cours,
            trimestre=trimestre,
            typeEvaluation=type_evaluation,
            note=note,
            pourcentage = pourcentage,
            etudiant=etudiants
        )
        return redirect('all_evaluation')
    
    cours_list = Cours.objects.filter(classe__id = id1, anneeScolaire__id = id2)
    classe = Classe.objects.get(id = id1)

    context = {
        'cours_list': cours_list,
        'etudiant': etudiant, 
        'classe': classe
    }
    return render(request, 'ajout_note_individuelle.html', context)
    
def deleteEvaluation(request, id):
    Evaluation.objects.get(id=id).delete()
    return redirect('all_evaluation')
    
     
    
    
#coût
def all_cout(request):
    if request.method == 'POST':
        classe = request.POST["classe"]
        couts = Cout.objects.filter(classe__classe__icontains = classe)
        
        context = {'couts': couts}
        return render(request, 'all-cout.html', {'couts': couts})
    else:
        couts = Cout.objects.all()
        context = {'couts': couts}
        return render(request, 'all-cout.html', context)

def ajoutCout(request):
    if request.method == 'POST':
        classe_id = request.POST["classe"]
        coutInscription = request.POST['coutInscription']
        coutScolarite = request.POST['coutScolarite']
        fraisEtudeDossier = request.POST['fraisEtudeDossier']
        fraisAssocie = request.POST['fraisAssocie']
        annee = request.POST['anneeScolaire']

        anneeScolaire = AnneeScolaire.objects.get(pk=int(annee))
        
        classe = get_object_or_404(Classe, id=classe_id)
        if Cout.objects.filter(classe = classe, anneeScolaire = anneeScolaire).exists():
            messages.error(request, f"Les coûts de cette classe ont déjà été ajoutés ({classe} ({anneeScolaire})). veuillez modifier les coûts existants")
        
        else:
            Cout.objects.create(
                classe=classe,
                coutInscription=coutInscription,
                coutScolarite=coutScolarite,
                fraisEtudeDossier=fraisEtudeDossier,
                fraisAssocie=fraisAssocie,
                anneeScolaire = anneeScolaire
                )
            return redirect('all_cout')
    context = {'classe_list': Classe.objects.all(), 'anneeScolaires': AnneeScolaire.objects.all()}
    return render(request, 'add-cout.html', context)

def suppCout(request, id):
    cout = get_object_or_404(Cout, id=id)
    cout.delete()
    return redirect('all_cout')

def modifierCout(request, id):
    cout = get_object_or_404(Cout, id=id)
    if request.method == 'POST':
        classe_id = request.POST["classe"]
        cout.coutInscription = request.POST['coutInscription']
        cout.coutScolarite = request.POST['coutScolarite']
        cout.fraisEtudeDossier = request.POST['fraisEtudeDossier']
        cout.fraisAssocie = request.POST['fraisAssocie']

        anneeScolaire = request.POST["anneeScolaire"]

        cout.anneeScolaire = AnneeScolaire.objects.get(pk=int(anneeScolaire))

        cout.classe = get_object_or_404(Classe, id=classe_id)
        
        cout.save()
        return redirect('all_cout')
    context = {'cout': cout, 'classe_list': Classe.objects.all(), 'anneeScolaires': AnneeScolaire.objects.all()}
    return render(request, 'modifier-cout.html', context)




def all_subject(request):
    return render(request, 'all-subject.html')

def class_routine(request):
    return render(request, 'class-routine.html')

def student_attendance(request):
    return render(request, 'student-attendance.html')

def exam_schedule(request):
    return render(request, 'exam-schedule.html')

def exam_grade(request):
    return render(request, 'exam-grade.html')

def notice_board(request):
    return render(request, 'notice-board.html')

def reception_dossier(request):
    return render(request, 'reception-dossier.html')

def messagesDiscussion(request):
    etudiant = Etudiant.objects.all()
    contains = {"etudiants": etudiant}
    return render(request, 'messages.html', contains)

def echangeMessage(request, id):
    etudiant = Etudiant.objects.get(id = id)
    contains = {'etudiant': etudiant}
    return render(request, 'echangeMessage.html', contains)

def account_settings(request):
    return render(request, 'account-settings.html')




from collections import defaultdict
from django.db.models import Avg


def generationBilletin(request, matricule, classe):
    etudiant = Etudiant.objects.get(matricule=matricule)
    cours_classe = Cours.objects.filter(classe__classe=classe)

    # inscrits = etudiant.inscriptions.all()

    # evaluations = Evaluation.objects.filter(
    #     etudiant=etudiant,
    #     trimestre="2e trimestre",
    #     cours__in=cours_classe
    # )
    moyenneCoursDevoirInterrogation = 0.0
    moyenneCoursComposition = 0.0
    moyenneCours= 0.0
    pourcentage = 1.0
    for cours in cours_classe:
        if cours:
            evaluationCours = Evaluation.objects.filter(etudiant = etudiant, trimestre="2e trimestre", cours = cours)
            for evalua in evaluationCours:
                if evalua.typeEvaluation == "Devoir" or evalua.typeEvaluation == "Interrogation":
                    pourcentage +=evalua.pourcentage
                    moyenneCoursDevoirInterrogation = float((evalua.note * evalua.pourcentage)/pourcentage)
                    
                elif evalua.typeEvaluation == "Composition":
                    pourcentage +=evalua.pourcentage
                    moyenneCoursComposition = float((evalua.note * evalua.pourcentage)/(pourcentage))

            moyenneCours = (moyenneCoursComposition+moyenneCoursDevoirInterrogation)/pourcentage
    print(f"moyenne devoir: {moyenneCoursDevoirInterrogation}")


    return render(request, 'generationBilletin.html', {
        "etudiant": etudiant,
        "cours_classes": cours_classe,
        "moyenneCoursDevoirInterrogation":moyenneCoursDevoirInterrogation,
        "moyenneCoursComposition":moyenneCoursComposition,
        "moyenneCours":moyenneCours,
    })


# def generationBilletin(request, matricule, classe):
#     etudiant = Etudiant.objects.get(matricule=matricule)
#     inscrits = etudiant.inscriptions.all()
#     cours_classe = Cours.objects.filter(classe__classe=classe)

#     evaluations = Evaluation.objects.filter(
#         etudiant=etudiant,
#         trimestre="2e Trimestre",
#         cours__in=cours_classe
#     )

#     # Regrouper les moyennes par matière et type d'évaluation
#     notes_par_matiere = defaultdict(lambda: {"Devoir": [], "Composition": [], "Interrogation": [], "coef": 1})

#     for eval in evaluations:
#         matiere = eval.cours.matiere
#         notes_par_matiere[matiere.nom]["coef"] = matiere.coefficient
#         notes_par_matiere[matiere.nom][eval.typeEvaluation].append(float(eval.note))

#     # Calcul des moyennes par matière
#     bulletin = []
#     somme_notes_ponderees = 0.0
#     somme_coefficients = 0.0

#     for matiere, notes in notes_par_matiere.items():
#         coef = notes["coef"]

#         def moyenne(note_list):
#             return round(sum(note_list) / len(note_list), 2) if note_list else 0.0

#         moy_dev = moyenne(notes["Devoir"])
#         moy_int = moyenne(notes["Interrogation"])
#         moy_comp = moyenne(notes["Composition"])

#         moy_globale = round((moy_dev + moy_int + moy_comp) / 3, 2) if (moy_dev or moy_int or moy_comp) else 0.0
#         moy_coef = round(moy_globale * coef, 2)

#         bulletin.append({
#             "matiere": matiere,
#             "coef": coef,
#             "dev": moy_dev,
#             "int": moy_int,
#             "comp": moy_comp,
#             "moyenne": moy_globale,
#             "ponderee": moy_coef
#         })

#         somme_notes_ponderees += moy_coef
#         somme_coefficients += coef

#     moyenne_generale = round(somme_notes_ponderees / somme_coefficients, 2) if somme_coefficients else 0.0

#     return render(request, 'generationBilletin.html', {
#         "etudiant": etudiant,
#         "inscrits": inscrits,
#         "bulletin": bulletin,
#         "moyenne_generale": moyenne_generale,
#         "cours_classes": cours_classe
#     })



from collections import defaultdict

# def generationBilletin(request, matricule, id):
#     etudiant = get_object_or_404(Etudiant, matricule=matricule)
    
#     classe = get_object_or_404(Classe, id = id)
    
#     cours = classe.cours.all()
    
#     # Pour stocker les notes groupées par matière + trimestre
#     notes_groupées = defaultdict(lambda: {"total_notes": 0.0, "coefficient": 0.0, "count": 0})
    
#     evaluations = etudiant.evaluations.all()
    
#     for evaluation in evaluations:
#         cours = evaluation.cours
#         matiere = cours.matiere
#         trimestre = cours.trimestre

#         if matiere and trimestre:
#             key = f"{matiere.nom}_{trimestre}"
#             notes_groupées[key]["total_notes"] += float(evaluation.note)
#             notes_groupées[key]["coefficient"] = matiere.coefficient  # le même pour chaque matière
#             notes_groupées[key]["count"] += 1

#     somme_note_pondérée = 0.0
#     somme_coefficients = 0.0
#     moyenne_matiere = 0.0
#     for valeurs in notes_groupées.values():
#         moyenne_matiere = valeurs["total_notes"] / valeurs["count"]
#         coef = valeurs["coefficient"]
#         somme_note_pondérée += moyenne_matiere * coef
#         somme_coefficients += coef

#     moyenne_generale = somme_note_pondérée / somme_coefficients if somme_coefficients != 0 else 0.0

#     return render(request, 'generationBilletin.html', {
#         "evaluations": evaluations,
#         "moyenne_matiere": moyenne_matiere,
#         "cours": cours,
#         "moyenne_generale": round(moyenne_generale, 2)
#     })



# def generationBilletin(request, matricule, classe):
#     etudiant = Etudiant.objects.get(matricule=matricule)
    
#     inscrits = etudiant.inscriptions.all()
    
#     cours = Cours.objects.filter(classe__classe = classe)
#     somme_note = 0.0
#     moyenne_generale = 0.0
#     somme_coeficient = 0.0
#     # evaluations = etudiant.evaluations.all()
#     evaluations = etudiant.evaluations.filter(trimestre="2e trimestre")
    
    
#     for evaluation in evaluations:
#         if evaluation.cours.matiere.nom.exits() and evaluation.cours.trimestre.exits():
#             coef = evaluation.cours.matiere.coefficient
#             moyene_matiere = float(evaluation.note/coef)
#             somme_coeficient += coef
#             somme_note += moyene_matiere
        
#     moyenne_generale = float(somme_note/somme_coeficient)
            
#     return render(request, 'generationBilletin.html', 
#                   {"inscrits": inscrits, "evaluations": evaluations, "moyenne_generale": moyenne_generale, 
#                    "etudiant": etudiant, "cours":cours})
    



# def echangeMessageEleves(request, id, matricule):
#     eleve = Etudiant.objects.get(matricule=matricule)
#     etudiant = Etudiant.objects.get(id = id)
    
#     if request.method == "POST":
#         print(request.POST)  # Pour debug
#         contenu_message = request.POST['message']
#         message = Messages.objects.create(contenu=contenu_message, expediteur=eleve, destinataire= etudiant, est_lu =False)
#         message.save()
#         return redirect('echangeMessageEleves', id = id, matricule=matricule)
#     discussions_expedi = Messages.objects.filter(expediteur=eleve, destinataire=etudiant).order_by('date_envoi')
#     discussions_desti = Messages.objects.filter(expediteur=etudiant, destinataire=eleve).order_by('date_envoi')
#     contains = {'etudiant': etudiant, 'eleve': eleve, 'discussions_expedi': discussions_expedi, 'discussions_desti': discussions_desti}
#     return render(request, 'eleve/echangeMessageEleves.html', contains)


# def echangeMessageEleves(request, id, matricule):
#     eleve = Etudiant.objects.get(matricule=matricule)
#     etudiant = Etudiant.objects.get(id=id)
    
#     etudiants = Etudiant.objects.exclude(matricule=matricule)
    
#     if request.method == "POST":
#         print(request.POST)  # Pour debug
#         contenu_message = request.POST['message']
#         if contenu_message != '':
#             message = Messages.objects.create(contenu=contenu_message, expediteur=eleve, destinataire=etudiant, est_lu=False)
#             message.save()
#         else:
#             messages = Messages.objects.filter(expediteur=eleve, destinataire=etudiant)
#             for message in messages:
#                 message.est_lu = True
#                 message.save()
#                 return redirect('echangeMessageEleves', id=id, matricule=matricule )
#             return redirect('echangeMessageEleves', id=id, matricule=matricule )
        
#         return redirect('echangeMessageEleves', id=id, matricule=matricule)
    
#     # Récupérer tous les messages entre ces deux utilisateurs
#     tous_messages = Messages.objects.filter(
#         (Q(expediteur=eleve) & Q(destinataire=etudiant)) | 
#         (Q(expediteur=etudiant) & Q(destinataire=eleve))
#     ).order_by('date_envoi')
    
#     contains = {
#         'etudiant': etudiant, 
#         'eleve': eleve, 
#         'tous_messages': tous_messages,
#         "etudiants": etudiants
#     }
#     return render(request, 'eleve/echangeMessageEleves.html', contains)


from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json
from datetime import datetime



# Nouvelle API pour récupérer les nouveaux messages
@require_GET
def get_new_messages(request, id, matricule):
    # Récupérer les objets Etudiant
    eleve = Etudiant.objects.get(matricule=matricule)
    etudiant = Etudiant.objects.get(id=id)
    
    # ID du dernier message connu par le client
    since_id = request.GET.get('since', 0)
    
    # Récupérer tous les nouveaux messages
    messages_query = Messages.objects.filter(
        (Q(expediteur=eleve) & Q(destinataire=etudiant)) | 
        (Q(expediteur=etudiant) & Q(destinataire=eleve)),
        id__gt=since_id  # Uniquement les messages avec un ID supérieur
    ).order_by('date_envoi')
    
    # Formater les messages pour JSON
    messages_list = []
    for msg in messages_query:
        messages_list.append({
            'id': msg.id,
            'contenu': msg.contenu,
            'date_envoi': msg.date_envoi.strftime('%H:%M:%S'),
            'expediteur_id': msg.expediteur.id,
            'expediteur_matricule': msg.expediteur.matricule,
            'est_lu': msg.est_lu
        })
    
    # Déterminer le dernier ID
    last_id = since_id
    if messages_query.exists():
        last_id = messages_query.last().id
    
    return JsonResponse({
        'messages': messages_list,
        'last_id': last_id
    })

# API pour marquer les messages comme lus
@require_POST
@csrf_exempt
def mark_messages_as_read(request, id, matricule):
    eleve = Etudiant.objects.get(matricule=matricule)
    etudiant = Etudiant.objects.get(id=id)
    
    # Marquer tous les messages de l'autre étudiant comme lus
    Messages.objects.filter(expediteur=etudiant, destinataire=eleve, est_lu=False).update(est_lu=True)
    
    return JsonResponse({'success': True})

# API pour envoyer un message
@require_POST
@csrf_exempt
def send_message(request, id, matricule):
    try:
        data = json.loads(request.body)
        contenu_message = data.get('message', '')
        
        if not contenu_message:
            return JsonResponse({'success': False, 'error': 'Message vide'})
        
        eleve = Etudiant.objects.get(matricule=matricule)
        etudiant = Etudiant.objects.get(id=id)
        
        # Créer et sauvegarder le nouveau message
        message = Messages.objects.create(
            contenu=contenu_message,
            expediteur=eleve,
            destinataire=etudiant,
            est_lu=False
        )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'date_envoi': message.date_envoi.strftime('%H:%M:%S')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    
    