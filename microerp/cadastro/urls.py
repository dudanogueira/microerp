# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do RH
urlpatterns = patterns('',
    url(r'^$', 'cadastro.views.home', name='home'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/ver/$', 'cadastro.views.ver_contatos_funcionario', name='ver_contatos_funcionario'),
)
