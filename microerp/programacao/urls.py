# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from programacao import views

# urls da Producao
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/iniciar/$', views.marcar_contrato_iniciado, name='marcar_contrato_iniciado'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/aguardando-cliente/$', views.marcar_contrato_aguardando_cliente, name='marcar_contrato_aguardando_cliente'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/retorno-cliente/$', views.marcar_contrato_retorno_cliente, name='marcar_contrato_retorno_cliente'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/editar/$', views.editar_programacao_contrato, name='editar_programacao_contrato'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/editar/adicionar-tarefa/$', views.editar_programacao_contrato_adicionar_tarefa, name='editar_programacao_contrato_adicionar_tarefa'),
]
