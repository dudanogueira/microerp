# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do RH
urlpatterns = patterns('',
    url(r'^$', 'cadastro.views.home', name='home'),
    url(r'^funcionarios/$', 'cadastro.views.funcionarios_list', name='funcionarios_list'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/ver/$', 'cadastro.views.funcionarios_contatos_ver', name='funcionarios_contatos_ver'),
    # recados
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/recados/$', 'cadastro.views.funcionarios_ver_recados', name='funcionarios_ver_recados'),
)
