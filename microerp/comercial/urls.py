# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'comercial.views.home', name='home'),
    # pre cliente
    url(r'^precliente/adicionar/$', 'comercial.views.precliente_adicionar', name='precliente_adicionar'),
    url(r'^precliente/(?P<pre_cliente_id>[0-9]+)/converter/$', 'comercial.views.precliente_converter', name='precliente_converter'),
    # cliente
    url(r'^clientes/$', 'comercial.views.clientes', name='clientes'),
    url(r'^clientes/(?P<cliente_id>[0-9]+)/$', 'comercial.views.cliente_ver', name='cliente_ver'),
    url(r'^clientes/(?P<cliente_id>[0-9]+)/editar/proposta/(?P<proposta_id>[0-9]+)/$', 'comercial.views.cliente_editar_proposta', name='cliente_editar_proposta'),
    # solicitações
    url(r'^solicitacao/adicionar/$', 'comercial.views.solicitacao_adicionar', name='solicitacao_adicionar'),
    # propostas  cliente
    url(r'^orcamento/novo/$', 'comercial.views.propostas_comerciais_cliente', name='propostas_comerciais_cliente'),
    url(r'^propostas/cliente/(?P<cliente_id>[0-9]+)/$', 'comercial.views.propostas_comerciais_cliente', name='propostas_comerciais_cliente'),
    url(r'^propostas/cliente/(?P<cliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_cliente_adicionar', name='propostas_comerciais_cliente_adicionar'),    
    # adicionar para cliente
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/$', 'comercial.views.propostas_comerciais_precliente', name='propostas_comerciais_precliente'),
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_precliente_adicionar', name='propostas_comerciais_precliente_adicionar'),    
    url(r'^propostas/minhas/$', 'comercial.views.propostas_comerciais_minhas', name='propostas_comerciais_minhas'),    
    # tabela de precos
    url(r'^tabela-de-precos/$', 'comercial.views.tabela_de_precos', name='tabela_de_precos'),
    # atender requisicao
    url(r'^requisicao/proposta/(?P<requisicao_id>[0-9]+)/atender$', 'comercial.views.requisicao_proposta_cliente_atender', name='requisicao_proposta_cliente_atender'),
    # designacoes
    url(r'^requisicao/designacoes/$', 'comercial.views.designacoes', name='designacoes'),
    url(r'^requisicao/designacoes/confirmar/$', 'comercial.views.designacoes_confirmar', name='designacoes_confirmar'),
)

