
from secretaire.models import AnneeScolaire


def annees_scolaires(request):
    return {
        "annees": AnneeScolaire.objects.all(),
        "annee_active": AnneeScolaire.objects.filter(est_active=True).first()
    }