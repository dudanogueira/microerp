# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'comercial.views.home', name='home'),
    url(r'^precliente/(?P<pre_cliente_id>[0-9]+)/converter/$', 'comercial.views.precliente_converter', name='precliente_converter'),
    # cliente
    url(r'^cliente/(?P<cliente_id>[0-9]+)/$', 'comercial.views.cliente_ver', name='cliente_ver'),
    # solicitações
    url(r'^solicitacao/adicionar/$', 'comercial.views.solicitacao_adicionar', name='solicitacao_adicionar'),
    # propostas  cliente
    url(r'^propostas/cliente/(?P<cliente_id>[0-9]+)/$', 'comercial.views.propostas_comerciais_cliente', name='propostas_comerciais_cliente'),
    url(r'^propostas/cliente/(?P<cliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_cliente_adicionar', name='propostas_comerciais_cliente_adicionar'),    
    # adicionar para cliente
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/$', 'comercial.views.propostas_comerciais_precliente', name='propostas_comerciais_precliente'),
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_precliente_adicionar', name='propostas_comerciais_precliente_adicionar'),    
    url(r'^propostas/minhas/$', 'comercial.views.propostas_comerciais_minhas', name='propostas_comerciais_minhas'),    
)
