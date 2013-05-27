# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'estoque.views.home', name='home'),
    # etiquetas
    url(r'^etiquetas/$', 'estoque.views.etiquetas', name='etiquetas'),
    url(r'^etiquetas/configurar/$', 'estoque.views.etiquetas_configurar', name='etiquetas_configurar'),
    url(r'^etiquetas/gerar/$', 'estoque.views.etiquetas_gerar', name='etiquetas_gerar'),
)
