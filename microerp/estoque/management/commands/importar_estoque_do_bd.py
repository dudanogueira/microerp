# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from estoque.models import ArquivoImportacaoProdutos
from estoque.models import Produto
from estoque.models import TipoDeProduto
from estoque.models import TabelaDePreco
from estoque.models import CodigoDeBarra

import os, datetime, xlrd

from django.utils.encoding import smart_text, smart_unicode

from django.core import management

class Command(BaseCommand):
    help = u'''
        Realiza importação conforme arquivo do bando de dados, modelo ArquivoImportacaoProdutos
        '''
    def handle(self, *args, **options):
        # get latest file path
        latest_file = ArquivoImportacaoProdutos.objects.filter(importado=False).last()
        
        try:
            if latest_file:
                if latest_file.tipo == 'digisat':
                    latest_file_path = latest_file.arquivo.path
                    # abre o arquivp
                    print u"ARQUIVO: %s" % latest_file_path
                    workbook = xlrd.open_workbook(latest_file_path)
                    worksheet = workbook.sheet_by_index(0)
                    # checa validade do cabecalho
                    row = worksheet.row(0)
                    assinatura_cabecalho = u'CODIGO,BARRAS,PADRAO_BARRAS,NOME,DESCRICAO,UND_V,UND_C,FATOR,GRUPO,USA_GRADE,QTD_ESTOQUE,QTD_CONSIGNACAO,QTD_PEDIDO,QTD_OS,QTD_COMANDA,QTD_MINIMO,QTD_MAXIMO,PRECO_CUSTO,PRECO_CONSUMIDOR,PRECO_REVENDA,PRECO_PRAZO_CONS,PRECO_PRAZO_REV,USA_INDICE,ATIVO,SELECIONA,TIPO,USA_UF,LOCALIZACAO,TABELA_PRECO,NCM,TRIBUTACAO,ST,CF,IPI,ICMS_REDUCAO,ICMS_SUBSTITUICAO,ICMS,ULTIMA_COMPRA,ULTIMA_VENDA'
                    cabecalho = ','.join([i.value for i in row])
                    if cabecalho == assinatura_cabecalho:
                        i = 0
                        for curr_row in range(worksheet.nrows):
                            if i == 0:
                                i += 1
                            else:
                                row = worksheet.row(curr_row)
                                codigo = int(row[0].value)
                                print '-'*50
                                print "LINHA", curr_row
                                if codigo:
                                    print "CODIGO", codigo
                                    produto,created = Produto.objects.get_or_create(codigo=codigo)
                                    print u"PRODUTO: %s" % produto
                                    print "PRODUTO CREATED:",created
                                    # ATUALIZAVEIS
                                    produto.nome = smart_text(row[3].value)
                                    produto.descricao = smart_text(row[4].value)
                                    produto.unidade_de_venda = smart_text(row[5].value)
                                    produto.unidade_de_compra = smart_text(row[6].value)
                        
                                    # TABELA
                                    tabela_nome = smart_text(row[28].value)
                                    if tabela_nome:
                                        try:
                                            tabela_id = tabela_nome.split()[0]
                                            print u"TABELA ID: %s" % tabela_id
                                            print u"TABELA NOME: %s" % tabela_nome
                                            if str(tabela_id).isdigit() and tabela_id != 0:
                                                tabela,created = TabelaDePreco.objects.get_or_create(id=tabela_id)
                                            else:
                                                tabela,created = TabelaDePreco.objects.get_or_create(nome=tabela_nome)
                                            print "TABELA CRIADA:",created
                                            produto.tabela = tabela
                                        except:
                                            pass
                        
                                    # TIPO / GRUPO
                                    tipo_id = int(row[8].value)
                                    if tipo_id == 0 or tipo_id == '0':
                                        tipo = None
                                    else:
                                        tipo,created = TipoDeProduto.objects.get_or_create(id=tipo_id)
                                        tipo.nome = u"GRUPO %s" % tipo.id
                                        tipo.save()
                                    print u"TIPO: %s" % tipo
                                    produto.tipo = tipo
                        
                                    # FATOR
                                    if row[7].value == 'nulo' or row[7].value == '' or row[7].value == 'NULO':
                                        valor_novo = None
                                    else:
                                        valor_novo = row[7].value
                                    produto.fator = valor_novo
                                    print "FATOR",valor_novo
                        
                                    print "ESTOQUE",row[10].value
                                    produto.quantidade_em_estoque = row[10].value
                        
                                    print "NCM",row[29].value
                                    if row[29].value:
                                        produto.ncm = row[29].value
                        
                                    print "PRECO_CONSUMIDOR",row[18].value
                                    if row[18].value:
                                        produto.preco_consumo = row[18].value
                                        produto.preco_venda = row[18].value

                                    if row[17].value:
                                        print "PRECO_CUSTO",row[17].value
                                        produto.preco_custo = row[17].value
                        
                                    print "ATIVO",row[23].value
                                    if row[23].value == "Sim":
                                        produto.ativo = True
                                    else:
                                        produto.ativo = False
                        
                                    produto.save()
            
                    else:
                        print u"ERRO! Formato inválido"
                latest_file.importado = True
                latest_file.importado_em = datetime.datetime.now()
                latest_file.save()

            else:
                print "nenhum arquivo a importar"
        except:
            raise
