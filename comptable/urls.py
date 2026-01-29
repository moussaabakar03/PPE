from django.urls import path
from . import views

app_name = "comptable"

urlpatterns = [
    path('', views.indexComptable, name='indexComptable'),
    path('listePaiments/', views.listePaiments, name='listePaiments'),
    path('selectionSalle/', views.selectionSalle, name='selectionSalle'),
    path('liste_eleve/<int:id_salle>/', views.liste_eleve, name='liste_eleve'),
    path('ajouter-paiement/<int:id_inscription>/', views.ajouter_paiement, name='ajouter_paiement'),
    path('enretardSurPaiement/', views.enretardSurPaiement, name='enretardSurPaiement'),
    
    path('alerte-retard-paiement/<int:id_classe>/', views.alerte_retard_paiement, name='alerte_retard_paiement'),
    
    path('changer-annee-active/<int:annee_id>/', views.changer_annee_active, name='changer_annee_active'),
    
    path('paiement/pdf/<int:id_inscription>/', 
         views.export_paiement_pdf, 
         name='export_paiement_pdf'),
    
    
    # path('liste-personnel/', views.liste_personnel, name='liste_personnel'),
    # path('enseignant/<int:enseignant_id>/', views.detail_enseignant, name='detail_enseignant'),
    # path('personnel/<int:enseignant_id>/ajouter-paiement/', views.ajouter_paiement_personnel, name='ajouter_paiement_personnel'),



]