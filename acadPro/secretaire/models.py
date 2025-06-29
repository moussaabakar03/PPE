from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.

from django.db import models

class AnneeScolaire(models.Model):
    debutAnnee = models.DateField()
    fintAnnee = models.DateField()

    def __str__(self):
        return f"{self.debutAnnee}/{self.fintAnnee}"

class Classe(models.Model):
    classe = models.CharField(max_length=100, unique=True)
    # capacite = models.PositiveIntegerField(default=1)  
    # scolarite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.classe}"
    
    
class SalleDeClasse(models.Model):
    niveau = models.ForeignKey(Classe, on_delete=models.CASCADE, null =True, blank=True, related_name='salle_de_classe')
    nom = models.CharField(max_length=50)
    capacite = models.PositiveIntegerField()
    emplacement = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.niveau}- {self.nom}- {self.capacite}"
    
    
class Parent(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    genre = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    lien_de_parente = models.CharField(
        max_length=50,
        choices=[
            ('Père', 'Père'),
            ('Mère', 'Mère'),
            ('Tuteur', 'Tuteur'),
        ]
    )
    photo = models.ImageField(upload_to='parents/', null=True, blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"  
    
class Utilisateur(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='utilisateur_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='utilisateur_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
            
    )
        
        
class Etudiant(Utilisateur):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True, related_name= 'etudiant')
    # salleDeClasse_id = models.ForeignKey(SalleDeClasse, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=50, unique=True, null=True, blank=True)
    genre = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    date_naissance = models.DateField(null=True, blank=True)

    groupe_sanguin = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'), 
        ('B+', 'B+'), ('B-', 'B-'), 
        ('AB+', 'AB+'), ('AB-', 'AB-'), 
        ('O+', 'O+'), ('O-', 'O-')
    ])
    mail = models.EmailField()
    niveau = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    nationnalite = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='photos/etudiants/', null=True, blank=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    lieuDeNaissance = models.CharField(max_length=100)
    # motDePasse = models.CharField(max_length=100, null= True, blank=True)


   
    
    def __str__(self):
        return f"{self.username}"
    
    def detailEtudiant(self):
        return reverse("detailEtudiant", kwargs={"matricule": self.matricule, "id": self.parent.id})
    

class Enseignant(models.Model):
    matricule = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    tel = models.CharField(max_length=15)
    diplome = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='photos/enseignants/', null=True, blank=True)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    mail = models.EmailField()
    lieuDeNaissance = models.CharField(max_length=100)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    salaire = models.DecimalField(max_digits=10, decimal_places=2)
    typeDeContrat = models.CharField(max_length=100)
    date_debut_contrat = models.DateField()
    date_fin_contrat = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"


class cvEnseignant(models.Model):
    cv = models.FileField(upload_to='cvEnseignant')
    dateHeure = models.DateTimeField(auto_now_add=True)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, null=True, blank=True, related_name="cvEnseignant")


class Matiere(models.Model):
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=100)
    # enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, null=True, blank=True)
    # niveau = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True, related_name='niveau')
    description = models.TextField(null=True, blank=True)
    coefficient = models.PositiveIntegerField()


class Inscription(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True,  related_name='inscriptions')
    salleClasse = models.ForeignKey(SalleDeClasse, on_delete=models.CASCADE, null=True, blank=True, related_name='inscris')
    dateEnregistrement = models.DateTimeField(auto_now_add=True)
    # coutA = models.DecimalField(max_digits=10, decimal_places=2)
    montantVerse = models.DecimalField(max_digits=10, decimal_places=2)
    # montantRestant = models.DecimalField(max_digits=10, decimal_places=2)
    anneeAcademique = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name= 'anneeAcad' )
    
    
class Scolarite(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True)
    coutScolarite = models.DecimalField(max_digits=10, decimal_places=2)
    montantPaye = models.DecimalField(max_digits=10, decimal_places=2)
    montantRestant = models.DecimalField(max_digits=10, decimal_places=2)
    etat = models.CharField(max_length=100, choices=[('Reglé', 'Reglé'), ('A completé', 'A completé')])
    
    
class Cours(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, null=True, blank=True, related_name='cours')
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, null=True, blank=True, related_name="cours")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True, related_name="cours")
    dateDebutCours = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=100, choices=[('En cours', 'En cours'), ('Effectué', 'Effectué'), ('Planifié', 'Planifié')])

    anneeScolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='anneeScolaire')


class Evaluation(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, null=False, blank=True, related_name='evaluations')
    trimestre = models.CharField(max_length=100, choices=[('Trimestre 1', 'Trimestre 1'), ('Trimestre 2', 'Trimestre 2'), ('Trimestre 3', 'Trimestre 3')])
    typeEvaluation = models.CharField(max_length=100, choices=[('Devoir', 'Devoir'), ('Interrogation', 'Interrogation'), ('Composition', 'Composition')])
    dateEvaluation = models.DateTimeField(auto_now_add=True)
    note = models.DecimalField(max_digits=10, decimal_places=2)
    pourcentage = models.DecimalField (max_digits=10, decimal_places=2)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True, related_name='evaluations')
    

class Cout(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True, related_name='couts')
    anneeScolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, null=False, blank=True, related_name='cout')
    coutInscription = models.DecimalField(max_digits=10, decimal_places=2)
    coutScolarite = models.DecimalField(max_digits=10, decimal_places=2)
    fraisEtudeDossier = models.DecimalField(max_digits=10, decimal_places=2)
    fraisAssocie = models.DecimalField(max_digits=10, decimal_places=2)


class Emargement(models.Model):
    salleClasse = models.ForeignKey(SalleDeClasse, on_delete=models.CASCADE, null=True, blank=True, related_name='emargements')
    # etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True, related_name ='emargements')
    inscrits = models.ForeignKey(Inscription, on_delete=models.CASCADE, null=True, blank=True, related_name='emargements')
    dateHeureDebut = models.DateTimeField()
    date_heure_fin = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField( blank=True, null=True)
    presence = models.BooleanField(default=False)
    dateJour = models.DateField(auto_now_add=True)


class Messages(models.Model):
    expediteur = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True, related_name='messages_expediteurs')
    destinataire = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="messages_destinataires", null=True, blank=True)
    contenu = models.TextField(blank=True, null=True)
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire} le {self.date_envoi}"


class depotDossierEtudiant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=100)
    dateheure = models.DateTimeField(auto_now_add=True)
    mail = models.EmailField()
    dossier = models.FileField(upload_to='dossiers_etudiants')
    numero_telephone = models.CharField(max_length=20)


class EmploiDuTemps(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    salle = models.ForeignKey(SalleDeClasse, on_delete = models.CASCADE, null=True)
    annee = models.ForeignKey(AnneeScolaire, on_delete = models.CASCADE, null=True)

    jour = models.CharField(max_length=30)
    heure = models.CharField(max_length=30)
    # heure_debut = models.TimeField()
    # heure_fin = models.TimeField()
