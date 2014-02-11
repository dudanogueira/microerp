# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Producao
urlpatterns = patterns('',
    url(r'^$', 'programacao.views.home', name='home'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/iniciar/$', 'programacao.views.marcar_contrato_iniciado', name='marcar_contrato_iniciado'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/aguardando-cliente/$', 'programacao.views.marcar_contrato_aguardando_cliente', name='marcar_contrato_aguardando_cliente'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/retorno-cliente/$', 'programacao.views.marcar_contrato_retorno_cliente', name='marcar_contrato_retorno_cliente'),
    
)
