from django.conf.urls import patterns, include, url

urlpatterns = patterns('comercial',
    # comercial home
    url(r'^$', 'views.home', name='home'),
    # contato comercial
    url(r'^contato-comercial/$', 'views.contato_comercial_list', name='contato-comercial-list'),
    url(r'^contato-comercial/adicionar/$', 'views.contato_comercial_adicionar', name='contato-comercial-adicionar'),
    url(r'^api/agenda/(?P<agenda_id>\d+)/agenda.json', 'views.contato_comercial_agenda_api', name='contato-comercial-agenda-api'),
    url(r'^api/agenda/evento/detalhes/agenda.html', 'views.detalhes_evento_html', name='detalhes_evento_html'),
    # cadastro
    url(r'^cadastro/clients/(?P<id>\d+)/$', 'views.cadastro_clientes_detalhe', name='cadastro-clientes-detalhe'),
    url(r'^cadastro/clientes/$', 'views.cadastro_clientes_list', name='cadastro-clientes-list'),
)
