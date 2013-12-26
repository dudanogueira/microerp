# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'cadastro.views.home', name='home'),
    url(r'^funcionarios/$', 'cadastro.views.funcionarios_listar', name='funcionarios_listar'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/ver/$', 'cadastro.views.funcionarios_contatos_ver', name='funcionarios_contatos_ver'),
    # recados
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/recados/adicionar/$', 'cadastro.views.funcionarios_recados_adicionar', name='funcionarios_recados_adicionar'),
    url(r'^recados/gerenciar/$', 'cadastro.views.recados_gerenciar', name='recados_gerenciar'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/recados/$', 'cadastro.views.funcionarios_recados_listar', name='funcionarios_recados_listar'),
    # pre clientes
    url(r'^preclientes/adicionar/$', 'cadastro.views.preclientes_adicionar', name='preclientes_adicionar'),
    # solicitaçõs
    url(r'^solicitacoes/adicionar/$', 'cadastro.views.solicitacao_adicionar', name='solicitacao_adicionar'),
    # requisicao de proposta
    url(r'^requisicao/proposta/adicionar/$', 'cadastro.views.requisicao_proposta_cliente', name='requisicao_proposta_cliente'),
)
