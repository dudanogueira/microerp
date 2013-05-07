# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Ocorrencia
urlpatterns = patterns('',
    url(r'^$', 'ocorrencia.views.home', name='home'),
)
