# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'comercial.views.home', name='home'),
    # pre cliente
    url(r'^precliente/adicionar/$', 'comercial.views.precliente_adicionar', name='precliente_adicionar'),
    url(r'^precliente/(?P<pre_cliente_id>[0-9]+)/converter/$', 'comercial.views.precliente_converter', name='precliente_converter'),
    # cliente
    url(r'^clientes/$', 'comercial.views.clientes', name='clientes'),
    url(r'^clientes/(?P<cliente_id>[0-9]+)/$', 'comercial.views.cliente_ver', name='cliente_ver'),
    # solicitações
    url(r'^solicitacao/adicionar/$', 'comercial.views.solicitacao_adicionar', name='solicitacao_adicionar'),
    # propostas  cliente
    url(r'^orcamento/novo/$', 'comercial.views.propostas_comerciais_cliente', name='propostas_comerciais_cliente'),
    url(r'^propostas/cliente/(?P<cliente_id>[0-9]+)/$', 'comercial.views.propostas_comerciais_cliente', name='propostas_comerciais_cliente'),
    url(r'^propostas/cliente/(?P<cliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_cliente_adicionar', name='propostas_comerciais_cliente_adicionar'),    
    url(r'^propostas/(?P<proposta_id>[0-9]+)/imprimir/$', 'comercial.views.proposta_comercial_imprimir', name='proposta_comercial_imprimir'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/$', 'comercial.views.editar_proposta', name='editar_proposta'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/inativar/$', 'comercial.views.editar_proposta_inativar_orcamento', name='editar_proposta_inativar_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/ativar/$', 'comercial.views.editar_proposta_ativar_orcamento', name='editar_proposta_ativar_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/editar/$', 'comercial.views.editar_proposta_editar_orcamento', name='editar_proposta_editar_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/fechar/$', 'comercial.views.editar_proposta_fechar', name='editar_proposta_fechar'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/converter/$', 'comercial.views.editar_proposta_converter', name='editar_proposta_converter'),
    # propostas pre cliente
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/$', 'comercial.views.propostas_comerciais_precliente', name='propostas_comerciais_precliente'),
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_precliente_adicionar', name='propostas_comerciais_precliente_adicionar'),    
    # todas
    url(r'^propostas/minhas/$', 'comercial.views.propostas_comerciais_minhas', name='propostas_comerciais_minhas'),    
    # tabela de precos
    url(r'^tabela-de-precos/$', 'comercial.views.tabela_de_precos', name='tabela_de_precos'),
    # designacoes
    url(r'^requisicao/designacoes/$', 'comercial.views.designacoes', name='designacoes'),
    url(r'^requisicao/designacoes/confirmar/$', 'comercial.views.designacoes_confirmar', name='designacoes_confirmar'),
    # modelos de Orçamento de proposta
    url(r'^orcamento/modelos/$', 'comercial.views.orcamentos_modelo', name='orcamentos_modelo'),
    url(r'^orcamento/modelos/novo/$', 'comercial.views.orcamentos_modelo_novo', name='orcamentos_modelo_novo'),
    url(r'^orcamento/modelos/(?P<modelo_id>[0-9]+)/editar/$', 'comercial.views.orcamentos_modelo_editar', name='orcamentos_modelo_editar'),
)

