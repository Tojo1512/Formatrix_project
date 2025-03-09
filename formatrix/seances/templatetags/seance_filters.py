from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Soustrait l'argument de la valeur."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value 