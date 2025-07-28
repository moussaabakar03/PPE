from django.urls import path
from . import views

app_name = "eleve"
urlpatterns = [
    path('notes/', views.notes, name='notes'),
    path('presence/', views.presence, name='presence'),
    path('inscriptionPayement/', views.inscriptionPayement, name="inscriptionPayement"),
    path('messagesEleves/', views.messagesEleves, name="messagesEleves"),
    # path('echangeMessageEleves/<int:id>/', views.echangeMessageEleves, name="echangeMessageEleves"),
    path('navBarEleve/', views.navBarEleve, name="navBarEleve"),
    path('header/', views.header, name="header"),
    path('emploiDuTempsEtudiant/', views.emploiDuTempsEtudiant, name="emploiDuTempsEtudiant"),
    path('affichageEmploiTemps/<int:id1>/<int:id2>/', views.affichageEmploiTemps, name="affichageEmploiTemps"),
    
    
    
    path('echangeEleveEleve/<int:id>/', views.echangeEleveEleve, name="echangeEleveEleve"),
    path('messages/api/<int:id>/<str:matricule>/', views.messages_api, name='api_messages'),
    path('messages/marquer-lu/<int:message_id>/', views.marquer_message_lu, name='marquer_message_lu'),
    

]