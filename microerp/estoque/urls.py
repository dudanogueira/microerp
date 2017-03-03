# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from estoque import views

# urls do Cadastro
urlpatterns = [
    url(r'^$', views.home, name='home'),
    # etiquetas
    url(r'^etiquetas/$', views.etiquetas, name='etiquetas'),
    url(r'^etiquetas/configurar/$', views.etiquetas_configurar, name='etiquetas_configurar'),
    url(r'^etiquetas/gerar/$', views.etiquetas_gerar, name='etiquetas_gerar'),
    # importacao de estoque
    url(r'^importacao/$', views.importacao_ver, name='importacao_ver'),
    url(r'^importacao/(?P<arquivo_id>[0-9]+)/apagar/$', views.importacao_apagar_arquivo, name='importacao_apagar_arquivo'),
    url(r'^importacao/importar/$', views.importacao_importar, name='importacao_importar'),
    # lista de materiais
    url(r'^listas-de-materiais/$', views.listas_materiais_ver, name='listas_materiais_ver'),
    url(r'^listas-de-materiais/(?P<lista_id>[0-9]+)/alterar$', views.listas_materiais_alterar, name='listas_materiais_alterar'),
]
