# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Ocorrencia
urlpatterns = patterns('',
    url(r'^$', 'ocorrencia.views.home', name='home'),
    url(r'^despachar/$', 'ocorrencia.views.despachar', name='despachar'),
    url(r'^despachar/(?P<ocorrencia_id>[0-9]+)/$', 'ocorrencia.views.despachar_ocorrencia', name='despachar_ocorrencia'),
)
