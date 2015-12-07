# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from solicitacao import views

# urls da Solicitacao
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^despachar/$', views.despachar, name='despachar'),
    url(r'^despachar/(?P<solicitacao_id>[0-9]+)/$', views.despachar_solicitacao, name='despachar_solicitacao'),
]
