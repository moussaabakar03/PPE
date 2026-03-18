
from secretaire.models import AlertCompteEleve, AnneeScolaire


#annees_scolaires, nombreCompteAlerter....
#Elements globaux
def header_elements_globaux(request):
    return {
        "annees": AnneeScolaire.objects.all(),
        "annee_active": AnneeScolaire.objects.filter(est_active=True).first(),
        "nbre_alerts_comptes_eleves": AlertCompteEleve.objects.filter(statut="non_vue").count(),
        "alerts_comptes_eleves": AlertCompteEleve.objects.filter(statut="non_vue")[:3]
    }