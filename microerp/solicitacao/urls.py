# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Solicitacao
urlpatterns = patterns('',
    url(r'^$', 'solicitacao.views.home', name='home'),
    url(r'^despachar/$', 'solicitacao.views.despachar', name='despachar'),
    url(r'^despachar/(?P<solicitacao_id>[0-9]+)/$', 'solicitacao.views.despachar_solicitacao', name='despachar_solicitacao'),
)
