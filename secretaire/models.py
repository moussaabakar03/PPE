from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.

from django.db import models

class AnneeScolaire(models.Model):
    debutAnnee = models.DateField()
    fintAnnee = models.DateField()
    est_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.est_active:
            # Désactiver toutes les autres années
            AnneeScolaire.objects.exclude(pk=self.pk).update(est_active=False)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.debutAnnee.year}-{self.fintAnnee.year}"
    
    
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
    
    capacite_etendue = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.niveau}- {self.nom}- {self.capacite}"

    
class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('parent', 'Parent'),
        ('eleve', 'Eleve'),
        ('enseignant', 'Enseignant'),
        ('admin', 'Administrateur'),
        ('secretaire', 'Secretaire'),
        ('comptable', 'Comptable'),
    ]
    
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Comptable(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete= models.CASCADE, null = True, blank= True, related_name= "comptable")
    email = models.EmailField(max_length=165)
    telephone = models.CharField(max_length=65)    
    date_ajout = models.DateTimeField(auto_now_add = True)
    date_modification = models.DateTimeField(auto_now= True)        
        
class Parent(models.Model):
        
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, null=True, blank=True, related_name="parent")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    genre = models.CharField(max_length=10, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    telephone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    profession = models.CharField(max_length=100, null=True, blank=True)

    photo = models.ImageField(upload_to='parents/', null=True, blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"  
    
class Etudiant(models.Model):
    
    statutEleve = [
        ('Exclu', 'Exclu'),
        ('Actif', 'Actif'),
        ('Suspendu', 'Suspendu'),
    ]
        
    
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name="eleve", null=True, blank=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True, related_name= 'etudiant')
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
    mail = models.EmailField(max_length=100)

    niveau = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    nationnalite = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='photos/etudiants/', null=True, blank=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    lieuDeNaissance = models.CharField(max_length=100)
    # motDePasse = models.CharField(max_length=100, null= True, blank=True)
    cheminCodeQr = models.ImageField(null=True, blank=True)
    lien_de_parente = models.CharField(
        max_length=50,
        choices=[
            ('Père', 'Père'),
            ('Mère', 'Mère'),
            ('Tuteur', 'Tuteur'),
        ]
    )
    
    statut = models.CharField(max_length=20, choices=statutEleve, default='Actif')
    
    def __str__(self):
        return f"{self.matricule}"
    
    def detailEtudiant(self):
        return reverse("detailEtudiant", kwargs={"matricule": self.matricule, "id": self.parent.id})
    

class Enseignant(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, null=True, blank=True, related_name="enseignant")
    matricule = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    tel = models.CharField(max_length=15, null=True, blank=True)
    diplome = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='photos/enseignants/', null=True, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=50, choices=[('M', 'Masculin'), ('F', 'Féminin')], null=True, blank=True)
    mail = models.EmailField(max_length=100, blank=True)
    lieuDeNaissance = models.CharField(max_length=100, null=True, blank=True)
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    salaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    typeDeContrat = models.CharField(max_length=100, null=True, blank=True)
    date_debut_contrat = models.DateField(null=True, blank=True)
    date_fin_contrat = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"


class cvEnseignant(models.Model):
    cv = models.FileField(upload_to='cvEnseignant')
    dateHeure = models.DateTimeField(auto_now_add=True)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, null=True, blank=True, related_name="cvEnseignant")
    
    def __str__(self):
        return f"CV de {self.enseignant} - {self.dateHeure.strftime('%d/%m/%Y %H:%M')}"


class Matiere(models.Model):
    code = models.CharField(max_length=10)
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.nom}"


class Inscription(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True,  related_name='inscriptions')
    salleClasse = models.ForeignKey(SalleDeClasse, on_delete=models.CASCADE, null=True, blank=True, related_name='inscris')
    dateEnregistrement = models.DateTimeField(auto_now_add=True)
    anneeAcademique = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name= 'anneeAcad' )
    
    def __str__(self):
        return f"Inscription: {self.etudiant} en {self.salleClasse} ({self.anneeAcademique})"
    
    def get_cout_inscription(self):
        return Cout.objects.filter(
            classe=self.salleClasse.niveau,
            anneeScolaire=self.anneeAcademique
        ).first()


class Scolarite(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True)
    coutScolarite = models.DecimalField(max_digits=10, decimal_places=2)
    montantPaye = models.DecimalField(max_digits=10, decimal_places=2)
    montantRestant = models.DecimalField(max_digits=10, decimal_places=2)
    etat = models.CharField(max_length=100, choices=[('Reglé', 'Reglé'), ('A completé', 'A completé')])
    
    def __str__(self):
        return f"Scolarité {self.classe} - {self.etat} - Restant: {self.montantRestant}"


class Cours(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, null=True, blank=True, related_name='cours')
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, null=True, blank=True, related_name="cours")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, null=True, blank=True, related_name="cours")
    dateDebutCours = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=100, choices=[('En cours', 'En cours'), ('Effectué', 'Effectué'), ('Planifié', 'Planifié')])
    coefficient = models.PositiveIntegerField()
    anneeScolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='anneeScolaire')

    def __str__(self):
        return f"{self.matiere} par {self.enseignant} - {self.classe} ({self.anneeScolaire})"

class EvaluationGroupee(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, null=False, blank=True, related_name='evaluationsGroupee')
    trimestre = models.CharField(max_length=100, choices=[('Trimestre 1', 'Trimestre 1'), ('Trimestre 2', 'Trimestre 2'), ('Trimestre 3', 'Trimestre 3')])
    typeEvaluation = models.CharField(max_length=100, choices=[('Devoir', 'Devoir'), ('Interrogation', 'Interrogation'), ('Composition', 'Composition')])
    pourcentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Groupe évaluation #{self.id} - {self.created_at}"


class Evaluation(models.Model):
    evaluation_groupe = models.ForeignKey(
        EvaluationGroupee,
        on_delete=models.CASCADE,
        related_name="evaluations",
        null=True,
        blank=True
    )
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, null=False, blank=True, related_name='evaluations')
    trimestre = models.CharField(max_length=100, choices=[('Trimestre 1', 'Trimestre 1'), ('Trimestre 2', 'Trimestre 2'), ('Trimestre 3', 'Trimestre 3')])
    typeEvaluation = models.CharField(max_length=100, choices=[('Devoir', 'Devoir'), ('Interrogation', 'Interrogation'), ('Composition', 'Composition')])
    dateEvaluation = models.DateTimeField(auto_now_add=True)
    note = models.DecimalField(max_digits=10, decimal_places=2)
    pourcentage = models.DecimalField(max_digits=10, decimal_places=2)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True, related_name='evaluations')
    
    def __str__(self):
        note = self.note*(self.pourcentage/100)
        return f"Évaluation {self.typeEvaluation} - {self.etudiant} - Note: {note}"


class Cout(models.Model):
    classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        related_name="couts"
    )
    anneeScolaire = models.ForeignKey(
        AnneeScolaire,
        on_delete=models.CASCADE,
        related_name="couts"
    )

    coutScolarite = models.DecimalField(max_digits=10, decimal_places=2)
    coutInscription = models.DecimalField(max_digits=10, decimal_places=2)
    fraisEtudeDossier = models.DecimalField(max_digits=10, decimal_places=2)
    fraisAssocie = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Coûts {self.classe} - {self.anneeScolaire}"
        
    def total_general(self):
        return (
            self.coutInscription +
            self.fraisEtudeDossier +
            self.fraisAssocie +
            self.coutScolarite
        )
        

class TrancheCout(models.Model):
    cout = models.ForeignKey(
        Cout,
        on_delete=models.CASCADE,
        related_name="tranches"
    )

    libelle = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_echeance = models.DateField()
    
    
    def __str__(self):
        return f"Tranche {self.libelle} - {self.montant} - Échéance: {self.date_echeance}"
    
    
    def clean(self):
        total_tranches = sum(
            t.montant for t in self.cout.tranches.exclude(id=self.id)
        )
        if total_tranches + self.montant > self.cout.coutScolarite:
            raise ValidationError(
                "La somme des tranches ne doit pas dépasser le coût de la scolarité"
            )

    
    
class Emargement(models.Model):
    salleClasse = models.ForeignKey(SalleDeClasse, on_delete=models.CASCADE, null=True, blank=True, related_name='emargements')
    inscrits = models.ForeignKey(Inscription, on_delete=models.CASCADE, null=True, blank=True, related_name='emargements')
    dateHeureDebut = models.DateTimeField()
    date_heure_fin = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True, null=True)
    presence = models.BooleanField(default=False)
    dateJour = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Émargement {self.inscrits} - {self.dateJour} - Présent: {self.presence}"


class Messages(models.Model):
    expediteur = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True, related_name='messages_expediteurs')
    destinataire = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name="messages_destinataires", null=True, blank=True)
    contenu = models.TextField(blank=True, null=True)
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_lu = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire} le {self.date_envoi}"


# class AlertCompteEleve(models.Model):

#     STATUT_CHOICES = [
#         ('Vue', 'Vue'),
#         ('Non_vue', 'Non vue'),
#     ]

#     eleve_expedi = models.ForeignKey(
#         Etudiant,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='alertes_envoyees'
#     )

#     eleve_destinat = models.ForeignKey(
#         Etudiant,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='alertes_recues'
#     )

#     contenu = models.TextField()

#     statut = models.CharField(
#         max_length=20,
#         choices=STATUT_CHOICES,
#         default='Non_vue'
#     )


#     def __str__(self):
#         return f"Signalement - {self.eleve_expedi} -> {self.eleve_destinat}"



class AlertCompteEleve(models.Model):

    TYPE_CHOICES = [
        ('harcelement', 'Harcèlement'),
        ('insulte', 'Insulte / Langage inapproprié'),
        ('menace', 'Menace'),
        ('contenu_inapproprie', 'Contenu inapproprié'),
        ('autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('non_vue', 'Non vue'),
        # ('en_cours', 'En cours de traitement'),
        ('vue', 'Vue'),
        # ('rejetee', 'Rejetée'),
    ]

    GRAVITE_CHOICES = [
        ('faible', 'Faible'),
        ('moderee', 'Modérée'),
        ('grave', 'Grave'),
    ]

    eleve_expedi = models.ForeignKey(
        Etudiant,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertes_envoyees'
    )

    eleve_signale = models.ForeignKey(       #  renommé pour plus de clarté
        Etudiant,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertes_recues'
    )

    # message_reference = models.ForeignKey(   #  lier au message exact signalé
    #     'Message',
    #     on_delete=models.SET_NULL,
    #     null=True, blank=True,
    #     related_name='alertes'
    # )

    type_signalement = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='autre'
    )

    gravite = models.CharField(
        max_length=10,
        choices=GRAVITE_CHOICES,
        default='moderee'
    )

    contenu = models.TextField()          

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='non_vue'
    )

    # note_admin = models.TextField(blank=True, null=True)  # commentaire de l'admin

    date_signalement = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_signalement']
        verbose_name = "Alerte compte élève"
        verbose_name_plural = "Alertes comptes élèves"

    def __str__(self):
        return f"[{self.get_statut_display()}] {self.eleve_expedi} signale {self.eleve_signale} – {self.date_signalement:%d/%m/%Y}"
    

    

class depotDossierEtudiant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=100)
    dateheure = models.DateTimeField(auto_now_add=True)
    mail = models.EmailField(max_length=100)
    dossier = models.FileField(upload_to='dossiers_etudiants')
    numero_telephone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Dossier de {self.prenom} {self.nom} - {self.niveau}"


class PlageHoraire(models.Model):
    salle = models.ForeignKey(SalleDeClasse, on_delete=models.CASCADE, null=True)
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, null=True, related_name="plageHoraire")
    debut = models.PositiveIntegerField()
    fin = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.debut} - {self.fin}"


class EmploiDuTemps(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    salle = models.ForeignKey(SalleDeClasse, on_delete=models.CASCADE, null=True)
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, null=True, related_name="emploiDuTemps")
    heure = models.CharField(max_length=30)
    jour = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.cours} - {self.jour} à {self.heure}"
    
    
    
    