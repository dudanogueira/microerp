# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'financeiro.views.home', name='home'),
    url(r'^contratos-a-lancar$', 'financeiro.views.contratos_a_lancar', name='contratos_a_lancar'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/ver$', 'financeiro.views.ver_contrato', name='ver_contrato'),
)
