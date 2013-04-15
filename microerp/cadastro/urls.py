# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'cadastro.views.home', name='home'),
    url(r'^funcionarios/$', 'cadastro.views.funcionarios_listar', name='funcionarios_listar'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/ver/$', 'cadastro.views.funcionarios_contatos_ver', name='funcionarios_contatos_ver'),
    # recados
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/recados/adicionar/$', 'cadastro.views.funcionarios_recados_adicionar', name='funcionarios_recados_adicionar'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/recados/$', 'cadastro.views.funcionarios_recados_listar', name='funcionarios_recados_listar'),
)
