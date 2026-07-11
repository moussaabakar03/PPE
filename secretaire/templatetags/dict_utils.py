from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key) if d else None





# register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Permet d'accéder aux valeurs d'un dictionnaire avec une clé variable dans les templates Django
    Usage: {{ mon_dict|lookup:ma_cle }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key, None)

@register.filter
def get_appreciation(moyenne):
    """
    Retourne l'appréciation correspondant à une moyenne
    """
    if moyenne >= 18:
        return "Excellent"
    elif moyenne >= 16:
        return "Très bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Insuffisant"

@register.filter
def get_decision_conseil(moyenne):
    """
    Retourne une proposition de décision du conseil de classe à partir d'une moyenne générale.
    """
    if moyenne >= 16:
        return "Tableau d'honneur - Félicitations"
    elif moyenne >= 14:
        return "Encouragements"
    elif moyenne >= 10:
        return "Travail satisfaisant"
    elif moyenne >= 8:
        return "Avertissement travail"
    else:
        return "Blâme travail"