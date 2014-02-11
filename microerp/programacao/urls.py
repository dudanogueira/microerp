# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Producao
urlpatterns = patterns('',
    url(r'^$', 'programacao.views.home', name='home'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/iniciar/$', 'programacao.views.marcar_contrato_iniciado', name='marcar_contrato_iniciado'),
)
