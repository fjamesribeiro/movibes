from django import template

register = template.Library()

@register.filter
def format_phone(value):
    """Formata número tipo 85999999999 → (85) 99999-9999"""
    if not value:
        return ""
    value = ''.join(filter(str.isdigit, str(value)))  # mantém só os números
    if len(value) == 11:
        return f"({value[:2]}) {value[2:7]}-{value[7:]}"
    elif len(value) == 10:
        return f"({value[:2]}) {value[2:6]}-{value[6:]}"
    else:
        return value
