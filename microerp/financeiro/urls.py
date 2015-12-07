# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from financeiro import views

# urls do Cadastro
urlpatterns = [
    url(r'^$', views.home, name='home'),
    # Contratos
    url(r'^contratos-a-lancar/$', views.contratos_a_lancar, name='contratos_a_lancar'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/ver/$', views.ver_contrato, name='ver_contrato'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/realizar-lancamento/$', views.realizar_lancamento, name='realizar_lancamento'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/adicionar-lancamento/$', views.contrato_adicionar_lancamento, name='contrato_adicionar_lancamento'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/fechar-contrato/$', views.contrato_fechar, name='contrato_fechar'),
    # lancamentos
    url(r'^lancamentos/$', views.lancamentos, name='lancamentos'),
    url(r'^lancamentos/a-receber/$', views.lancamentos_a_receber, name='lancamentos_a_receber'),
    url(r'^lancamentos/a-receber/(?P<lancamento_id>[0-9]+)/receber/$', views.lancamentos_a_receber_receber, name='lancamentos_a_receber_receber'),
    url(r'^lancamentos/a-receber/(?P<lancamento_id>[0-9]+)/comentar/$', views.lancamentos_a_receber_comentar, name='lancamentos_a_receber_comentar'),
    # processo de antecipacao
    url(r'^lancamentos/a-receber/antecipar/$', views.lancamentos_a_receber_antecipar, name='lancamentos_a_receber_antecipar'),
    # ajax
    url(r'^lancamentos/ajax/a-receber/(?P<busca_tipo>[a-z]+)/(?P<offset>[0-9]+)/$', views.ajax_lancamentos_receber, name='ajax_lancamentos_receber'),
    url(r'^lancamentos/ajax/lancamento/(?P<lancamento_id>[0-9]+)/comentarios/$', views.ajax_lancamento_comentarios, name='ajax_lancamento_comentarios'),
    url(r'^lancamentos/ajax/lancamento/(?P<lancamento_id>[0-9]+)/informacao-pagamento/$', views.ajax_lancamento_informacao_pagamento, name='ajax_lancamento_informacao_pagamento'),
    url(r'^lancamentos/ajax/lancamento/buscar/$', views.ajax_lancamento_buscar, name='ajax_lancamento_buscar'),
]
