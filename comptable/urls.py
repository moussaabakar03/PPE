from django.urls import path
from . import views

app_name = "comptable"

urlpatterns = [
    
    path('selectionSalle/', views.selectionSalle, name='selectionSalle'),
    path('liste_eleve/<int:id_salle>/<int:id_annee>/', views.liste_eleve, name='liste_eleve'),
    path('ajouter-paiement/<int:id_inscription>/', views.ajouter_paiement, name='ajouter_paiement'),
    path('liste-personnel/', views.liste_personnel, name='liste_personnel'),
    path('enseignant/<int:enseignant_id>/', views.detail_enseignant, name='detail_enseignant'),
    path('personnel/<int:enseignant_id>/ajouter-paiement/', views.ajouter_paiement_personnel, name='ajouter_paiement_personnel'),



]