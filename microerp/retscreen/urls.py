# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from retscreen import views

# urls da Solicitacao
urlpatterns = [
    url(r'^$', views.home, name='home'),
]
