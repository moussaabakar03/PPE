from django.urls import path
from . import views

app_name = "secretaire"

urlpatterns = [
    
    path('', views.index, name='index'),
    path('index3/', views.index3, name='index3'),
    path('index4/', views.index4, name='index4'),
    path('index5/', views.index5, name='index5'),
    path('login/', views.connexion, name='login'),
    
    path('inscription/', views.inscription, name='inscription'),
    # path('connexion/', views.connexion, name='connexion'),
    # path('acceuil/', views.acceuil, name='acceuil'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    
    #Annee scolaire:
    path('affichageAnneeScolaire/', views.affichageAnneeScolaire, name='affichageAnneeScolaire'),
    path('ajoutAnneeScolaire/', views.ajoutAnneeScolaire, name='ajoutAnneeScolaire'),
    path('modifierAnneeScolaire/<int:id>/', views.modifierAnneeScolaire, name='modifierAnneeScolaire'),
    path('supprimer-anneeScolaire/<int:id>/', views.supprimerAnneeScolaire, name='supprimerAnneeScolaire'),
    path('changer-annee-active/<int:annee_id>/', views.changer_annee_active, name='changer_annee_active'),
    path('profil/', views.profil, name='profil'),
    
    
    path('all-student/', views.all_student, name='all-student'),
    path('admit-form/', views.admit_form, name='admit-form'),
    path('student-promotion/', views.student_promotion, name='student-promotion'),
    path('carteScolaire/<str:matricule>/', views.student_detail, name = 'students-detail'),
    path('detailEtudiant/<str:matricule>/<int:id>/', views.detailEtudiant, name = 'detailEtudiant'),
    path('modifier_student/<str:matricule>/', views.modifier_student, name = 'modifier_student'),
    path('supprimer_student/<str:matricule>/', views.supprimer_student, name = 'supprimer_student'),
    path('studentParSalle/<int:id>/', views.studentParSalle, name = 'studentParSalle'),
    path('messageCommunParent/<int:id1>/', views.messageCommunParent, name = 'messageCommunParent'),
    path('bulletins-salle/<int:salle_id>/<int:annee_id>/envoyer-parents/', views.envoyerBulletinsAuxParents, name='envoyerBulletinsAuxParents'),

    path('certificat-inscription/<int:id>/', views.certificatInscription, name = 'certificatInscription'),

    path('exclure-etudiant/<str:matricule>/', views.exclure_etudiant, name = 'exclure_etudiant'),
    path('suspendre-etudiant/<str:matricule>/', views.suspendre_etudiant, name = 'suspendre_etudiant'),
    path('gracier-etudiant/<str:matricule>/', views.gracier_etudiant, name = 'gracier_etudiant'),

    
    
    path('export-excel/<int:salle_id>/<int:annee_id>/', views.export_excel, name='export_excel'),
    path('export-pdf/<int:salle_id>/<int:annee_id>/', views.export_pdf, name='export_pdf'),
    
    
    path('listePresence/<int:id>/', views.listePresence, name = 'listePresence'),
    path('liste-presence-passee/<int:id>/', views.listePresencePasse, name = 'listePresencePasse'),
    path('supprimer-emargement/<int:id>/', views.supprimerEmargement, name = 'supprimerEmargement'),
    path('modifier-emargement/<int:id>/', views.modifier_emargement, name = 'modifier_emargement'),
    
    path('presenceEtudiant/<str:matricule>/', views.presenceEtudiant, name = 'presenceEtudiant'),
    
    path('affichePaiementEleve/<str:matricule>/', views.affichePaiementEleve, name = 'affichePaiementEleve'),
    
    
    # path('ajouter_etudiant/', views.ajouter_etudiant, name = 'ajouter_etudiant'),

    path('all-teacher/', views.all_teacher, name='all-teacher'),
    path('add-teacher/', views.add_teacher, name='add-teacher'),
    path('teacher-detail/', views.teacher_detail, name = 'teachers-detail'),
    path('detailEnseignant/<str:matricule>/', views.detailEnseignant, name = 'detailEnseignant'),
    path('modifier_teacher/<str:matricule>/', views.modifier_teacher, name = 'modifier_teacher'),
    path('supprimer_teacher/<str:matricule>/', views.supprimer_teacher, name = 'supprimer_teacher'),
    path('cvEnseignants/<int:id>/', views.cvEnseignants, name = 'cvEnseignants'),
    path('listeCvEnseignant/<int:id>/', views.listeCvEnseignant, name = 'listeCvEnseignant'),
    path('suppCvEnseignant/<int:id>/', views.suppCvEnseignant, name = 'suppCvEnseignant'),


    path('all-parents/', views.all_parents, name='all-parents'),
    path('add-parents/', views.ajout_parents, name='add-parents'),
    # path('parents-detail/', views.parents_detail, name = 'parents-detail'),
    path('modifier_parent/<int:id>/', views.modifier_parent, name = 'modifier_parent'),
    path('supprimer_parent/<int:id>/', views.supprimer_parent, name = 'supprimer_parent'),


    path('all-class/', views.all_class, name='all-class'),
    path('ajoutMatiere/', views.ajoutMatiere, name='add-class'),
    path('supprimer_matiere/<int:id>/', views.supprimer_matiere, name='supprimer_matiere'),
    path('modifier_matiere/<int:id>/', views.modifier_matiere, name='modifier_matiere'),


    path('all-salle/', views.all_salle, name='all-salle'),
    path('add-salle/', views.add_salle, name='add-salle'),
    path('modifierSalle/<str:nom>/', views.modifierSalle, name='modifierSalle'),
    path('supprimerSalle/<int:id>/', views.supprimerSalle, name='supprimerSalle'),
    path('emploiDuTemps/<int:id1>/', views.emploiDuTemps, name='emploiDuTemps'),
    path('ajoutEmploiTemps/<int:id1>/<int:id3>/', views.ajoutEmploiTemps, name='ajoutEmploiTemps'),
    path('supprimerEmploiTemps/<int:id1>/', views.supprimerEmploiTemps, name='supprimerEmploiTemps'),
    path('bulletinsSalleDeClasse/<int:salleClasseId>/', views.bulletinsSalleDeClasse, name='bulletinsSalleDeClasse'),
    path('cartesEleveSalleDeClasse/<int:salleClasseId>/', views.cartesEleveSalleDeClasse, name='cartesEleveSalleDeClasse'),
    path("etendre-salle/<int:idEleve>/<int:idSalleClasse>/<int:idAnnee>/", views.etendreSalleClasse, name="etendreSalleClasse"),

    
    
    

    path('all_niveau/', views.all_niveau, name='all_niveau'),
    path('add_niveau/', views.add_niveau, name='add_niveau'),
    path('modifierNiveau/<int:id>/', views.modifierNiveau, name='modifierNiveau'),
    path('supprimerNiveau/<int:id>/', views.supprimerNiveau, name='supprimerNiveau'),
    
    
    path('all-inscription', views.all_inscription, name='all_inscription'),
    path('add_inscription', views.ajoutInscription, name='add_inscription'),
    path('modifierInscription/<int:id>/', views.modifierInscription, name='modifierInscription'),
    path('delete_inscription/<int:id>/', views.delete_inscription, name='delete_inscription'),
    
    
    
    path('all_cours/', views.all_cours, name='all-cours'),
    path('add_cours/', views.ajoutCours, name='add-cours'),
    path('supprimer_cours/<int:pk>/', views.supprimer_cours, name='supprimer_cours'),
    path('modifier_cours/<int:pk>/', views.modifier_cours, name='modifier_cours'),
    
    
    path('all_evaluation/', views.all_evaluation, name='all_evaluation'),
    # path('add_evaluation/', views.add_evaluation, name='add_evaluation'),
    path('supprimer_evaluation/<int:pk>/', views.supprimer_evaluation, name='supprimer_evaluation'),
    path('modifier_evaluation/<int:id>/', views.modifier_evaluation, name='modifier_evaluation'),
    
    path('evaluation-groupee/<int:id>/<int:id1>/', views.evaluation_groupee, name='evaluation_groupee'),
    path('filtre_evaluation/<int:id>/', views.filtre_evaluation, name='filtre_evaluation'),
    path('selectClasseEvaluation/', views.selectClasseEvaluation, name='selectClasseEvaluation'),
    path('evaluationGroupee/<int:id>/', views.evaluationGroupee, name='evaluationGroupee'),

    path('supprimer-evaluation-groupee/<int:id>/', views.supprimerEvaluationGroupee, name='supprimerEvaluationGroupee'),
    
    
    
    path('selectClasse/', views.selectClasse, name='selectClasse'),
    path('note_individuelle/<int:id>/', views.note_individuelle, name='note_individuelle'),
    path('ajout_note_individuelle/<int:id>/<int:id1>/', views.ajout_note_individuelle, name='ajout_note_individuelle'),
    
    
    
    path('all_cout/', views.all_cout, name='all_cout'),
    path('add_cout/', views.ajoutCout, name='add_cout'),
    path('delete_cout/<int:id>/', views.suppCout, name='delete_cout'),
    path('update_cout/<int:id>/', views.modifierCout, name='update_cout'),
    
    path('detail_cout/<int:id>/', views.detail_cout, name='detail_cout'),

    path('all-subject/', views.all_subject, name='all-subject'),
    path('class-routine/', views.class_routine, name='class-routine'),
    path('student-attendance/', views.student_attendance, name='student-attendance'),

    path('exam-schedule/', views.exam_schedule, name='exam-schedule'),
    path('exam-grade/', views.exam_grade, name='exam-grade'),

    path('notice-board/', views.notice_board, name='notice-board'),
    path('reception-dossier/', views.reception_dossier, name='reception-dossier'),

    path('messages/', views.messagesDiscussion, name='messages'),
    path('echangeMessage/<int:id>/', views.echangeMessage, name='echangeMessage'),
    
    path('account-settings/', views.account_settings, name='account-settings'),
    
    
    
    path('generationBulletin/<str:matricule>/<int:salleClasse>/', views.generationBulletin, name='generationBilletin'),
    
    
    path('alertCompteEleve/', views.alertCompteEleve, name="alertCompteEleve"),
    
    
    
    # path('api/messages/<int:id>/<str:matricule>/', views.get_new_messages, name='get_new_messages'),
    # path('api/messages/<int:id>/<str:matricule>/read/', views.mark_messages_as_read, name='mark_messages_as_read'),
    # path('api/messages/<int:id>/<str:matricule>/send/', views.send_message, name='send_message'),
    
    path('all-comptable/', views.all_comptable, name='all-comptable'),
    path('ajoutComptable/', views.ajoutComptable, name='ajoutComptable'),
    path('detailComptable/<str:matricule>/', views.detailComptable, name='detailComptable'),
    path('modifier_comptable/<str:matricule>/', views.modifier_comptable, name='modifier_comptable'),
    path('supprimer_comptable/<str:matricule>/', views.supprimer_comptable, name='supprimer_comptable'),

]

