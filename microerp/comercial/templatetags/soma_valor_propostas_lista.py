from django import template

register = template.Library()

# app_filters.py
@register.filter
def total_propostas(lista_propostas):
    return sum(d.valor_proposto for d in lista_propostas)
    
register.filter('total_propostas', total_propostas)