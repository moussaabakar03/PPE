from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name='index'),
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
    path('supprimerAnneeScolaire/<int:id>/', views.supprimerAnneeScolaire, name='supprimerAnneeScolaire'),
    
    
    path('all-student/', views.all_student, name='all-student'),
    path('admit-form/', views.admit_form, name='admit-form'),
    path('student-promotion/', views.student_promotion, name='student-promotion'),
    path('student-detail/<str:matricule>', views.student_detail, name = 'students-detail'),
    path('detailEtudiant/<str:matricule>/<int:id>', views.detailEtudiant, name = 'detailEtudiant'),
    path('modifier_student/<str:matricule>', views.modifier_student, name = 'modifier_student'),
    path('supprimer_student/<str:matricule>', views.supprimer_student, name = 'supprimer_student'),
    path('studentParSalle/<int:id>/<int:id2>', views.studentParSalle, name = 'studentParSalle'),
    
    path('listePresence/<int:id>/<int:id2>', views.listePresence, name = 'listePresence'),
    path('listePresencePasse/<int:id>/<int:id2>', views.listePresencePasse, name = 'listePresencePasse'),
    
    path('presenceEtudiant/<str:matricule>', views.presenceEtudiant, name = 'presenceEtudiant'),
    
    # path('ajouter_etudiant/', views.ajouter_etudiant, name = 'ajouter_etudiant'),

    path('all-teacher/', views.all_teacher, name='all-teacher'),
    path('add-teacher/', views.add_teacher, name='add-teacher'),
    path('teacher-detail/', views.teacher_detail, name = 'teachers-detail'),
    path('detailEnseignant/<str:matricule>', views.detailEnseignant, name = 'detailEnseignant'),
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
    path('add-class/', views.add_class, name='add-class'),
    path('supprimer_matiere/<int:id>', views.supprimer_matiere, name='supprimer_matiere'),
    path('modifier_matiere/<int:id>', views.modifier_matiere, name='modifier_matiere'),


    path('all-salle/', views.all_salle, name='all-salle'),
    path('add-salle/', views.add_salle, name='add-salle'),
    path('modifierSalle/<str:nom>', views.modifierSalle, name='modifierSalle'),
    path('supprimerSalle/<int:id>', views.supprimerSalle, name='supprimerSalle'),
    path('emploiDuTemps/<int:id1>/<int:id2>', views.emploiDuTemps, name='emploiDuTemps'),
    path('ajoutEmploiTemps/<int:id1>/<int:id2>/<int:id3>', views.ajoutEmploiTemps, name='ajoutEmploiTemps'),
    

    
    path('all_niveau/', views.all_niveau, name='all_niveau'),
    path('add_niveau/', views.add_niveau, name='add_niveau'),
    path('modifierNiveau/<int:id>', views.modifierNiveau, name='modifierNiveau'),
    path('supprimerNiveau/<int:id>', views.supprimerNiveau, name='supprimerNiveau'),
    
    
    path('all_inscription', views.all_inscription, name='all_inscription'),
    path('add_inscription', views.ajoutInscription, name='add_inscription'),
    path('modifierInscription/<int:id>', views.modifierInscription, name='modifierInscription'),
    path('delete_inscription/<int:id>', views.delete_inscription, name='delete_inscription'),
    
    
    
    path('all_cours/', views.all_cours, name='all-cours'),
    path('add_cours/', views.ajoutCours, name='add-cours'),
    path('supprimer_cours/<int:pk>', views.supprimer_cours, name='supprimer_cours'),
    path('modifier_cours/<int:pk>', views.modifier_cours, name='modifier_cours'),
    
    
    path('all_evaluation/', views.all_evaluation, name='all_evaluation'),
    # path('add_evaluation/', views.add_evaluation, name='add_evaluation'),
    path('supprimer_evaluation/<int:pk>', views.supprimer_evaluation, name='supprimer_evaluation'),
    path('modifier_evaluation/<int:id>', views.modifier_evaluation, name='modifier_evaluation'),
    
    path('evaluation-groupee/<int:id>/<int:id1>/<int:id2>/', views.evaluation_groupee, name='evaluation_groupee'),
    path('filtre_evaluation/<int:id>', views.filtre_evaluation, name='filtre_evaluation'),
    path('selectClasseEvaluation/', views.selectClasseEvaluation, name='selectClasseEvaluation'),
    
    path('selectClasse/', views.selectClasse, name='selectClasse'),
    path('note_individuelle/<int:id>/<int:id2>/', views.note_individuelle, name='note_individuelle'),
    path('ajout_note_individuelle/<int:id>/<int:id1>/<int:id2>/', views.ajout_note_individuelle, name='ajout_note_individuelle'),
    
    
    
    path('all_cout/', views.all_cout, name='all_cout'),
    path('add_cout/', views.ajoutCout, name='add_cout'),
    path('delete_cout/<int:id>', views.suppCout, name='delete_cout'),
    path('update_cout/<int:id>', views.modifierCout, name='update_cout'),
    
    

    path('all-subject/', views.all_subject, name='all-subject'),
    path('class-routine/', views.class_routine, name='class-routine'),
    path('student-attendance/', views.student_attendance, name='student-attendance'),

    path('exam-schedule/', views.exam_schedule, name='exam-schedule'),
    path('exam-grade/', views.exam_grade, name='exam-grade'),

    path('notice-board/', views.notice_board, name='notice-board'),
    path('reception-dossier/', views.reception_dossier, name='reception-dossier'),

    path('messages/', views.messagesDiscussion, name='messages'),
    path('echangeMessage/<int:id>', views.echangeMessage, name='echangeMessage'),
    
    path('account-settings/', views.account_settings, name='account-settings'),
    
    
    
    path('generationBilletin/<str:matricule>/<str:classe>', views.generationBilletin, name='generationBilletin'),
    
    
    # path('recuperationDossierEleve/', views.recuperationDossierEleve, name="recuperationDossierEleve"),
    
    
    
    
    path('api/messages/<int:id>/<str:matricule>/', views.get_new_messages, name='get_new_messages'),
    path('api/messages/<int:id>/<str:matricule>/read/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('api/messages/<int:id>/<str:matricule>/send/', views.send_message, name='send_message'),
]

