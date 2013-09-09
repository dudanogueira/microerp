# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Producao
urlpatterns = patterns('',
    url(r'^$', 'producao.views.home', name='home'),
    url(r'^notafiscal/lancar_nota/$', 'producao.views.lancar_nota', name='lancar_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/calcular/$', 'producao.views.calcular_nota', name='calcular_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/apagar/$', 'producao.views.apagar_nota', name='apagar_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/editar/$', 'producao.views.editar_nota', name='editar_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/ver/$', 'producao.views.ver_nota', name='ver_nota'),    
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/lancar/$', 'producao.views.lancar_nota_fechar', name='lancar_nota_fechar'),
    url(r'^notafiscal/adicionar/$', 'producao.views.adicionar_nota', name='adicionar_nota'),
    # editar lancamentos
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/lancamento/(?P<lancamento_id>[0-9]+)/editar/$', 'producao.views.editar_lancamento', name='editar_lancamento'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/lancamento/adicionar/$', 'producao.views.adicionar_lancamento', name='adicionar_lancamento'),
    # componentes e categorias
    url(r'^componentes/$', 'producao.views.listar_componentes', name='listar_componentes'),
    url(r'^componentes/adicionar/$', 'producao.views.adicionar_componentes', name='adicionar_componentes'),
    url(r'^componentes/(?P<componente_id>[0-9]+)/ver/$', 'producao.views.ver_componente', name='ver_componente'),
    url(r'^componentes/(?P<componente_id>[0-9]+)/anexo/(?P<anexo_id>[0-9]+)/apagar/$', 'producao.views.ver_componente_apagar_anexo', name='ver_componente_apagar_anexo'),
    url(r'^componentes/(?P<componente_id>[0-9]+)/memoria/(?P<memoria_id>[0-9]+)/apagar/$', 'producao.views.apagar_memoria_componente', name='apagar_memoria_componente'),
    url(r'^componentes/(?P<componente_id>[0-9]+)/memoria/adicionar/$', 'producao.views.adicionar_memoria_componente', name='adicionar_memoria_componente'),
    # Fabricantes e Fornecedores
    url(r'^fabricantes_fornecedores/(?P<fabricante_fornecedor_id>[0-9]+)/editar/$', 'producao.views.editar_fabricantes_fornecedores', name='editar_fabricantes_fornecedores'),
    url(r'^fabricantes_fornecedores/(?P<fabricante_fornecedor_id>[0-9]+)/ver/$', 'producao.views.ver_fabricantes_fornecedores', name='ver_fabricantes_fornecedores'),    
    url(r'^fabricantes_fornecedores/adicionar/$', 'producao.views.adicionar_fabricantes_fornecedores', name='adicionar_fabricantes_fornecedores'),
    url(r'^fabricantes_fornecedores/$', 'producao.views.listar_fabricantes_fornecedores', name='listar_fabricantes_fornecedores'),
    # Estoque e Movimentação
    url(r'^estoque/$', 'producao.views.listar_estoque', name='listar_estoque'),
    # sub produto
    url(r'^subproduto/adicionar/$', 'producao.views.adicionar_subproduto', name='adicionar_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/ver/$', 'producao.views.ver_subproduto', name='ver_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/editar/$', 'producao.views.editar_subproduto', name='editar_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/anexo/(?P<anexo_id>[0-9]+)/apagar/$', 'producao.views.ver_subproduto_apagar_anexo', name='ver_subproduto_apagar_anexo'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/linha/adicionar/$', 'producao.views.adicionar_linha_subproduto', name='adicionar_linha_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/linha/(?P<linha_subproduto_id>[0-9]+)/editar/$', 'producao.views.editar_linha_subproduto', name='editar_linha_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/linha/(?P<linha_subproduto_id>[0-9]+)/apagar/$', 'producao.views.apagar_linha_subproduto', name='apagar_linha_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/linha/(?P<linha_subproduto_id>[0-9]+)/adicionar/opcao/$', 'producao.views.editar_linha_subproduto_adicionar_opcao', name='editar_linha_subproduto_adicionar_opcao'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/linha/(?P<linha_subproduto_id>[0-9]+)/opcao/(?P<opcao_linha_subproduto_id>[0-9]+)/tornar_padrao/$', 'producao.views.tornar_padrao_opcao_linha_subproduto', name='tornar_padrao_opcao_linha_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/linha/(?P<linha_subproduto_id>[0-9]+)/opcao/(?P<opcao_linha_subproduto_id>[0-9]+)/apagar/$', 'producao.views.apagar_opcao_linha_subproduto', name='apagar_opcao_linha_subproduto'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/subproduto-agregado/(?P<linha_subproduto_agregado_id>[0-9]+)/apagar$', 'producao.views.subproduto_apagar_linha_subproduto_agregado', name='subproduto_apagar_linha_subproduto_agregado'),
    url(r'^subproduto/$', 'producao.views.listar_subprodutos', name='listar_subprodutos'),
    url(r'^subproduto/(?P<subproduto_id>[0-9]+)/relatorios/composicao/$', 'producao.views.ver_subproduto_relatorios_composicao', name='ver_subproduto_relatorios_composicao'),    
    #produto
    url(r'^produto/$', 'producao.views.listar_produtos', name='listar_produtos'),
    url(r'^produto/adicionar/$', 'producao.views.adicionar_produto', name='adicionar_produto'),
    url(r'^produto/(?P<produto_id>[0-9]+)/editar/$', 'producao.views.editar_produto', name='editar_produto'),
    url(r'^produto/(?P<produto_id>[0-9]+)/ver/$', 'producao.views.ver_produto', name='ver_produto'),
    url(r'^produto/(?P<produto_id>[0-9]+)/linha-subproduto/(?P<linha_id>[0-9]+)/apagar$', 'producao.views.apagar_linha_subproduto_de_produto', name='apagar_linha_subproduto_de_produto'),
    url(r'^produto/(?P<produto_id>[0-9]+)/linha-componente-avulso/(?P<linha_id>[0-9]+)/apagar$', 'producao.views.apagar_linha_componente_avulso_de_produto', name='apagar_linha_componente_avulso_de_produto'),
    url(r'^produto/(?P<produto_id>[0-9]+)/anexo/(?P<anexo_id>[0-9]+)/apagar$', 'producao.views.ver_produto_apagar_anexo', name='ver_produto_apagar_anexo'),
    url(r'^produto/(?P<produto_id>[0-9]+)/relatorios/composicao/$', 'producao.views.ver_produto_relatorios_composicao', name='ver_produto_relatorios_composicao'),    
    # ordem de producao
    url(r'^ordem-de-producao/$', 'producao.views.ordem_de_producao', name='ordem_de_producao'),
    url(r'^ordem-de-producao/subproduto/(?P<subproduto_id>[0-9]+)/produzir/(?P<quantidade_solicitada>[0-9]+)/$', 'producao.views.ordem_de_producao_subproduto', name='ordem_de_producao_subproduto'),
    url(r'^ordem-de-producao/subproduto/(?P<subproduto_id>[0-9]+)/produzir/(?P<quantidade_solicitada>[0-9]+)/confirmar/$', 'producao.views.ordem_de_producao_subproduto_confirmar', name='ordem_de_producao_subproduto_confirmar'),    
    url(r'^ordem-de-producao/produto/(?P<produto_id>[0-9]+)/produzir/(?P<quantidade_solicitada>[0-9]+)/$', 'producao.views.ordem_de_producao_produto', name='ordem_de_producao_produto'),
    url(r'^ordem-de-producao/produto/(?P<produto_id>[0-9]+)/produzir/(?P<quantidade_solicitada>[0-9]+)/confirmar/$', 'producao.views.ordem_de_producao_produto_confirmar', name='ordem_de_producao_produto_confirmar'),
    # ajax auxs
    url(r'^ordem-de-producao/ajax/totalizador-de-producao/$', 'producao.views.totalizador_de_producao', name='totalizador_de_producao'),
    url(r'^ordem-de-producao/ajax/producao-combinada/$', 'producao.views.producao_combinada', name='producao_combinada'),
    url(r'^ordem-de-producao/ajax/producao-combinada/calcular$', 'producao.views.producao_combinada_calcular', name='producao_combinada_calcular'),
    url(r'^ordem-de-producao/ajax/qeps/componentes$', 'producao.views.qeps_componentes', name='qeps_componentes'),
    url(r'^ordem-de-producao/ajax/preparar-producao-semana/$', 'producao.views.preparar_producao_semanal', name='preparar_producao_semanal'),
    # arvore de produtos
    url(r'^arvore-de-produto/$', 'producao.views.arvore_de_produto', name='arvore_de_produto'),
    url(r'^arvore-de-produto/ajax/subproduto/(?P<subproduto_id>[0-9]+)/parente/(?P<parente>[0-9]+)/$', 'producao.views.arvore_de_produto_ajax_subproduto', name='arvore_de_produto_ajax_subproduto'),
    # registro de testes
    url(r'^registro-de-testes/$', 'producao.views.registro_de_testes', name='registro_de_testes'),
    # ordem de compra
    url(r'^ordem-de-compra/$', 'producao.views.ordem_de_compra', name='ordem_de_compra'),
    url(r'^ordem-de-compra/(?P<ordem_de_compra_id>[0-9]+)/editar/$', 'producao.views.ordem_de_compra_editar', name='ordem_de_compra_editar'),
    url(r'^ordem-de-compra/(?P<ordem_de_compra_id>[0-9]+)/fechar/$', 'producao.views.ordem_de_compra_fechar', name='ordem_de_compra_fechar'),
    url(r'^ordem-de-compra/(?P<ordem_de_compra_id>[0-9]+)/atividade/(?P<atividade_id>[0-9]+)/fechar/$', 'producao.views.ordem_de_compra_atividade_fechar', name='ordem_de_compra_atividade_fechar'),
    url(r'^ordem-de-compra/(?P<ordem_de_compra_id>[0-9]+)/componente-comprado/(?P<vinculacao_id>[0-9]+)/remover/$', 'producao.views.ordem_de_compra_componente_comprado_remover', name='ordem_de_compra_componente_comprado_remover'),
)
