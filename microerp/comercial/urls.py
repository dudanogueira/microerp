# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'comercial.views.home', name='home'),
    # pre cliente
    url(r'^precliente/adicionar/$', 'comercial.views.precliente_adicionar', name='precliente_adicionar'),
    url(r'^precliente/(?P<pre_cliente_id>[0-9]+)/converter/$', 'comercial.views.precliente_converter', name='precliente_converter'),
    url(r'^precliente/(?P<pre_cliente_id>[0-9]+)/ver/$', 'comercial.views.precliente_ver', name='precliente_ver'),
    # cliente
    url(r'^clientes/$', 'comercial.views.clientes', name='clientes'),
    url(r'^clientes/(?P<cliente_id>[0-9]+)/$', 'comercial.views.cliente_ver', name='cliente_ver'),
    url(r'^clientes/precliente/(?P<precliente_id>[0-9]+)/sem-interesse/$', 'comercial.views.clientes_precliente_sem_interesse', name='clientes_precliente_sem_interesse'),
    # solicitações
    url(r'^solicitacao/adicionar/$', 'comercial.views.solicitacao_adicionar', name='solicitacao_adicionar'),
    # propostas  cliente
    url(r'^propostas/cliente/(?P<cliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_cliente_adicionar', name='propostas_comerciais_cliente_adicionar'),    
    url(r'^propostas/(?P<proposta_id>[0-9]+)/ver/$', 'comercial.views.propostas_comerciais_ver', name='propostas_comerciais_ver'),
    url(r'^propostas/(?P<proposta_id>[0-9]+)/adicionar-follow-up/$', 'comercial.views.adicionar_follow_up', name='adicionar_follow_up'),
    url(r'^propostas/(?P<proposta_id>[0-9]+)/imprimir2/$', 'comercial.views.proposta_comercial_imprimir2', name='proposta_comercial_imprimir2'),
    url(r'^propostas/(?P<proposta_id>[0-9]+)/imprimir/$', 'comercial.views.proposta_comercial_imprimir', name='proposta_comercial_imprimir'),
    url(r'^propostas/(?P<proposta_id>[0-9]+)/imprimir/gerar_documento/(?P<documento_id>[0-9]+)$', 'comercial.views.proposta_comercial_imprimir_gerar_documento', name='proposta_comercial_imprimir_gerar_documento'),
    url(r'^propostas/(?P<proposta_id>[0-9]+)/reabrir/$', 'comercial.views.proposta_comercial_reabrir', name='proposta_comercial_reabrir'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/$', 'comercial.views.editar_proposta', name='editar_proposta'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/inativar/$', 'comercial.views.editar_proposta_inativar_orcamento', name='editar_proposta_inativar_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/ativar/$', 'comercial.views.editar_proposta_ativar_orcamento', name='editar_proposta_ativar_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/reajustar/$', 'comercial.views.editar_proposta_reajustar_orcamento', name='editar_proposta_reajustar_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/imprimir/$', 'comercial.views.editar_proposta_imprimir_orcamento', name='editar_proposta_imprimir_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/imprimir/orcamentos$', 'comercial.views.editar_proposta_imprimir_orcamentos_da_proposta', name='editar_proposta_imprimir_orcamentos_da_proposta'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/editar/orcamento/(?P<orcamento_id>[0-9]+)/editar/$', 'comercial.views.editar_proposta_editar_orcamento', name='editar_proposta_editar_orcamento'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/fechar/$', 'comercial.views.editar_proposta_fechar', name='editar_proposta_fechar'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/converter/$', 'comercial.views.editar_proposta_converter', name='editar_proposta_converter'),
    url(r'^proposta/(?P<proposta_id>[0-9]+)/converter_novo/$', 'comercial.views.editar_proposta_converter_novo', name='editar_proposta_converter_novo'),
    url(r'^proposta/gerente/aprovar/fechamentos/$', 'comercial.views.gerencia_aprovar_fechamentos', name='gerencia_aprovar_fechamentos'),
    # propostas pre cliente
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/$', 'comercial.views.propostas_comerciais_precliente', name='propostas_comerciais_precliente'),
    url(r'^propostas/precliente/(?P<precliente_id>[0-9]+)/adicionar/$', 'comercial.views.propostas_comerciais_precliente_adicionar', name='propostas_comerciais_precliente_adicionar'),    
    # todas
    url(r'^propostas/minhas/$', 'comercial.views.propostas_comerciais_minhas', name='propostas_comerciais_minhas'),    
    url(r'^propostas/minhas/expiradas/ajax/$', 'comercial.views.propostas_comerciais_minhas_expiradas_ajax', name='propostas_comerciais_minhas_expiradas_ajax'),    
    # tabela de precos
    url(r'^tabela-de-precos/$', 'comercial.views.tabela_de_precos', name='tabela_de_precos'),
    # designacoes
    url(r'^requisicao/designacoes/$', 'comercial.views.designacoes', name='designacoes'),
    url(r'^requisicao/designacoes/confirmar/$', 'comercial.views.designacoes_confirmar', name='designacoes_confirmar'),
    # modelos de Orçamento de proposta
    url(r'^orcamento/modelos/$', 'comercial.views.orcamentos_modelo', name='orcamentos_modelo'),
    url(r'^orcamento/modelos/novo/$', 'comercial.views.orcamentos_modelo_novo', name='orcamentos_modelo_novo'),
    url(r'^orcamento/modelos/(?P<modelo_id>[0-9]+)/editar/$', 'comercial.views.orcamentos_modelo_editar', name='orcamentos_modelo_editar'),
    url(r'^orcamento/modelos/(?P<modelo_id>[0-9]+)/reajustar/$', 'comercial.views.orcamentos_modelo_reajustar', name='orcamentos_modelo_reajustar'),
    url(r'^orcamento/modelos/(?P<modelo_id>[0-9]+)/gerenciar/$', 'comercial.views.orcamentos_modelo_gerenciar', name='orcamentos_modelo_gerenciar'),
    url(r'^orcamento/modelos/(?P<modelo_id>[0-9]+)/apagar/$', 'comercial.views.orcamentos_modelo_apagar', name='orcamentos_modelo_apagar'),
    # indicadores
    url(r'^indicadores/$', 'comercial.views.indicadores_do_comercial', name='indicadores_do_comercial'),
    # relatorios
    url(r'^relatorios/$', 'comercial.views.relatorios_comercial', name='relatorios_comercial'),
    url(r'^relatorios/probabilidade/$', 'comercial.views.relatorios_comercial_probabilidade', name='relatorios_comercial_probabilidade'),
    url(r'^relatorios/propostas/declinadas/$', 'comercial.views.relatorios_comercial_propostas_declinadas', name='relatorios_comercial_propostas_declinadas'),
    url(r'^relatorios/propostas/followups/$', 'comercial.views.relatorios_comercial_propostas_e_followups', name='relatorios_comercial_propostas_e_followups'),
    url(r'^relatorios/propostas/periodo/$', 'comercial.views.relatorios_comercial_propostas_por_periodo_e_vendedor', name='relatorios_comercial_propostas_por_periodo_e_vendedor'),
    url(r'^relatorios/propostas/visitas/$', 'comercial.views.relatorios_comercial_propostas_visitas', name='relatorios_comercial_propostas_visitas'),
    
    # contratos
    url(r'^contrato/analises/$', 'comercial.views.analise_de_contratos', name='analise_de_contratos'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/analisar/$', 'comercial.views.analise_de_contratos_analisar', name='analise_de_contratos_analisar'),
    url(r'^contrato/meus/$', 'comercial.views.contratos_meus', name='contratos_meus'),
    url(r'^contrato/meus/revalidar/(?P<contrato_id>[0-9]+)/$', 'comercial.views.contratos_meus_revalidar', name='contratos_meus_revalidar'),
    url(r'^contrato/meus/definir-assinado/(?P<contrato_id>[0-9]+)/$', 'comercial.views.contratos_meus_definir_assinado', name='contratos_meus_definir_assinado'),
    url(r'^contrato/meus/arquivar/(?P<contrato_id>[0-9]+)/$', 'comercial.views.contratos_meus_arquivar', name='contratos_meus_arquivar'),
    url(r'^contrato/meus/gerar-impressao/(?P<contrato_id>[0-9]+)/$', 'comercial.views.contratos_gerar_impressao', name='contratos_gerar_impressao'),
    # comissoes - gerencia
    url(r'^gerencia/comissoes/$', 'comercial.views.gerencia_comissoes', name='gerencia_comissoes'),
    url(r'^gerencia/comissoes/novo/fechamento/$', 'comercial.views.gerencia_comissoes_novo_fechamento', name='gerencia_comissoes_novo_fechamento'),
    
)

