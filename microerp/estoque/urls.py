# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'estoque.views.home', name='home'),
    # etiquetas
    url(r'^etiquetas/$', 'estoque.views.etiquetas', name='etiquetas'),
    url(r'^etiquetas/configurar/$', 'estoque.views.etiquetas_configurar', name='etiquetas_configurar'),
    url(r'^etiquetas/gerar/$', 'estoque.views.etiquetas_gerar', name='etiquetas_gerar'),
    # importacao de estoque
    url(r'^importacao/$', 'estoque.views.importacao_ver', name='importacao_ver'),
    url(r'^importacao/(?P<arquivo_id>[0-9]+)/apagar/$', 'estoque.views.importacao_apagar_arquivo', name='importacao_apagar_arquivo'),
    url(r'^importacao/importar/$', 'estoque.views.importacao_importar', name='importacao_importar'),
    # lista de materiais
    url(r'^listas-de-materiais/$', 'estoque.views.listas_materiais_ver', name='listas_materiais_ver'),
    url(r'^listas-de-materiais/(?P<lista_id>[0-9]+)/alterar$', 'estoque.views.listas_materiais_alterar', name='listas_materiais_alterar'),
)
