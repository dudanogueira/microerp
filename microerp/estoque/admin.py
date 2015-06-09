# -*- coding: utf-8 -*-
"""This file is part of the microerp project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Duda Nogueira <dudanogueira@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Duda Nogueira'
__version__ = '2.0.0'

from django.contrib import admin

from estoque.models import Produto
from estoque.models import TipoDeProduto
from estoque.models import TabelaDePreco
from estoque.models import PerfilAcessoEstoque
from estoque.models import PerfilAcessoEstoque
from estoque.models import ArquivoImportacaoProdutos

class ProdutoAdmin(admin.ModelAdmin):
    
    list_display = 'codigo', 'nome', 'preco_custo', 'preco_venda',
    list_display_link = list_display
    list_filter = 'tipo', 'tabela', 'unidade_de_compra', 'unidade_de_venda'
    search_fields = 'codigo', 'descricao', 'nome', 'ncm', 'preco_venda', 'preco_custo'

class ArquivoImportacaoProdutosAdmin(admin.ModelAdmin):
    list_display = 'tipo', 'importado', 'importado_em', 'enviado_por'

admin.site.register(Produto, ProdutoAdmin)
admin.site.register(TipoDeProduto)
admin.site.register(TabelaDePreco)
admin.site.register(PerfilAcessoEstoque)
admin.site.register(ArquivoImportacaoProdutos, ArquivoImportacaoProdutosAdmin)
