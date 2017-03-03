# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from cadastro import views

# urls do Cadastro
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^funcionarios/$', views.funcionarios_listar, name='funcionarios_listar'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/ver/$', views.funcionarios_contatos_ver, name='funcionarios_contatos_ver'),
    # recados
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/recados/adicionar/$', views.funcionarios_recados_adicionar, name='funcionarios_recados_adicionar'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/recados/$', views.funcionarios_recados_listar, name='funcionarios_recados_listar'),
    # pre clientes
    url(r'^preclientes/adicionar/$', views.preclientes_adicionar, name='preclientes_adicionar'),
    # solicitaçõs
    url(r'^solicitacoes/adicionar/$', views.solicitacao_adicionar, name='solicitacao_adicionar'),
    # requisicao de proposta
    url(r'^requisicao/proposta/adicionar/$', views.requisicao_proposta_cliente, name='requisicao_proposta_cliente'),
]
