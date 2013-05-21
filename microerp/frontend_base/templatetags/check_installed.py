from django import template
register = template.Library()

from django.conf import settings

def is_installed_app(value):
    return value in settings.INSTALLED_APPS

register.filter('is_installed_app', is_installed_app)