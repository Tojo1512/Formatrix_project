from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Récupère une valeur d'un dictionnaire avec une clé donnée"""
    return dictionary.get(key, 0)

@register.filter
def div(value, arg):
    """Division avec gestion des divisions par zéro"""
    try:
        return float(value) / float(arg) if arg != 0 else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiplication de deux nombres"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 