from django.db import models

from secretaire.models import Etudiant, Inscription

# Create your models here.



class PaiementEleve(models.Model):
    inscription_Etudiant = models.ForeignKey(Inscription, on_delete=models.CASCADE, related_name='paiements')
    montantVerse = models.DecimalField(max_digits=10, decimal_places=2)
    datePaiement = models.DateField(editable=False, auto_now_add=True)
    typePaiement = models.CharField(max_length=150)
    modePaiment = models.CharField(max_length=150)
    periodeConcerne = models.CharField(max_length=150)
    
    def __str__(self):
        return f"Paiement #{self.id} - {self.etudiant} ({self.montant}€)"



# class PaiementPersonnel(models.Model):
#     enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
#     montant = models.DecimalField(max_digits=10, decimal_places=2)
#     date_paiement = models.DateField(auto_now_add=True)
#     mode_paiement = models.CharField(max_length=50)

#     def __str__(self):
#         return f"{self.enseignant} - {self.montant} F"
    
