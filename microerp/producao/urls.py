# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls da Producao
urlpatterns = patterns('',
    url(r'^$', 'producao.views.home', name='home'),
    url(r'^notafiscal/lancar_nota$', 'producao.views.lancar_nota', name='lancar_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/calcular$', 'producao.views.calcular_nota', name='calcular_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/apagar$', 'producao.views.apagar_nota', name='apagar_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/editar$', 'producao.views.editar_nota', name='editar_nota'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/ver$', 'producao.views.ver_nota', name='ver_nota'),    
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/lancar$', 'producao.views.lancar_nota_fechar', name='lancar_nota_fechar'),
    url(r'^notafiscal/adicionar$', 'producao.views.adicionar_nota', name='adicionar_nota'),
    # editar lancamentos
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/lancamento/(?P<lancamento_id>[0-9]+)/editar$', 'producao.views.editar_lancamento', name='editar_lancamento'),
    url(r'^notafiscal/(?P<notafiscal_id>[0-9]+)/lancamento/adicionar$', 'producao.views.adicionar_lancamento', name='adicionar_lancamento'),
    # componentes e categorias
    url(r'^componentes$', 'producao.views.listar_componentes', name='listar_componentes'),
    url(r'^componentes/adicionar$', 'producao.views.adicionar_componentes', name='adicionar_componentes'),
    url(r'^componentes/(?P<componente_id>[0-9]+)/ver$', 'producao.views.ver_componente', name='ver_componente'),
    # Fabricantes e Fornecedores
    url(r'^fabricantes_fornecedores/(?P<fabricante_fornecedor_id>[0-9]+)/editar$', 'producao.views.editar_fabricantes_fornecedores', name='editar_fabricantes_fornecedores'),
    url(r'^fabricantes_fornecedores/(?P<fabricante_fornecedor_id>[0-9]+)/ver$', 'producao.views.ver_fabricantes_fornecedores', name='ver_fabricantes_fornecedores'),    
    url(r'^fabricantes_fornecedores/adicionar$', 'producao.views.adicionar_fabricantes_fornecedores', name='adicionar_fabricantes_fornecedores'),
    url(r'^fabricantes_fornecedores$', 'producao.views.listar_fabricantes_fornecedores', name='listar_fabricantes_fornecedores'),
    
)
