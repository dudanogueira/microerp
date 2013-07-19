# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from django.contrib.sites.models import Site

from cadastro.models import Cidade, Bairro
from rh.models import Funcionario, PeriodoTrabalhado, Cargo, Departamento

from account.models import User

from optparse import make_option
import os, csv, datetime

from django.utils.encoding import smart_unicode, smart_str

from xml.dom import minidom

from producao.models import FabricanteFornecedor
from producao.models import NotaFiscal

class Command(BaseCommand):
    help = '''
        Importa Nota Fiscal
    '''
    args = "--file notafiscal.xml,"
    option_list = BaseCommand.option_list + (
    make_option('--file',
            action='store_true',
            dest='arquivo',
            help='Importa uma nota fiscal',
        ),
    )

    def handle(self, *args, **options):
        arquivo = options.get('arquivo')
        if options['arquivo']:
            f = args[0]
            try:
                xmldoc = minidom.parse(f)
                infNFE = xmldoc.getElementsByTagName('chNFe')[0]
                idnfe = infNFE.firstChild.nodeValue[22:34]
                nome_emissor = xmldoc.getElementsByTagName('xNome')[0]
                nome = nome_emissor.firstChild.nodeValue
                print "NOME DO EMISSOR: %s" % nome
                print "ID NOTA FISCAL %s" % idnfe
                emissor = xmldoc.getElementsByTagName('emit')[0]
                cnpj_emissor = xmldoc.getElementsByTagName('CNPJ')[0].firstChild.nodeValue
                # busca emissor
                fornecedor,created = FabricanteFornecedor.objects.get_or_create(cnpj=cnpj_emissor)
                fornecedor.nome = nome
                fornecedor.save()
                if created:
                    print "Fornecedor CRIADO: %s" % fornecedor
                else:
                    print "Fornecedor encrontrado: %s" % fornecedor

                total = xmldoc.getElementsByTagName('total')[0]
                frete = total.getElementsByTagName('vFrete')[0].firstChild.nodeValue
                # criando NFE no sistema
                nfe_sistema,created = NotaFiscal.objects.get_or_create(fabricante_fornecedor=fornecedor, numero=idnfe)
                nfe_sistema.taxas_diversas = frete
                nfe_sistema.save()
                # pega itens da nota
                itens = xmldoc.getElementsByTagName('det')
                for item in itens:
                    # cada item da nota...
                    codigo_produto = item.getElementsByTagName('cProd')[0].firstChild.nodeValue
                    quantidade = item.getElementsByTagName('qCom')[0].firstChild.nodeValue
                    valor_unitario = item.getElementsByTagName('vUnCom')[0].firstChild.nodeValue
                    print u"ITEM: %s" % codigo_produto
                    print u"Quantidade: %s" % quantidade
                    print u"Valor Unitário: %s" % valor_unitario
                    # impostos
                    try:
                        aliquota_icms = float(item.getElementsByTagName('pICMS')[0].firstChild.nodeValue)
                    except:
                        aliquota_icms = 0
                    try:
                        aliquota_ipi = float(item.getElementsByTagName('pIPI')[0].firstChild.nodeValue)
                    except:
                        aliquota_ipi = 0
                    try:
                        aliquota_pis = float(item.getElementsByTagName('pPIS')[0].firstChild.nodeValue)
                    except:
                        aliquota_pis = 0
                    try:
                        aliquota_cofins = float(item.getElementsByTagName('pCOFINS')[0].firstChild.nodeValue)
                    except:
                        aliquota_cofins = 0

                        
                    total_impostos = aliquota_ipi + aliquota_icms + aliquota_cofins + aliquota_cofins
                    total_impostos = aliquota_ipi
                    print "Valor %% ICMS: %s" % aliquota_icms
                    print "Valor %% IPI: %s" % aliquota_ipi
                    print "Valor %% COFNS: %s" % aliquota_cofins
                    print "Valor %% PIS: %s" % aliquota_pis
                    print "Incidência de %% impostos: %s" % total_impostos
                    
                    # busca o lancamento, para evitar dois lancamentos iguais do mesmo partnumber
                    item_lancado,created = nfe_sistema.lancamentocomponente_set.get_or_create(part_number_fornecedor=codigo_produto)
                    # atualiza
                    item_lancado.quantidade= quantidade
                    item_lancado.valor_unitario= valor_unitario
                    item_lancado.impostos= total_impostos
                    # salva
                    item_lancado.save()
                    # busca na memoria automaticamente
                    item_lancado.busca_part_number_na_memoria()

                # calcula total da nota
                nfe_sistema.calcula_totais_nota()
                # printa tudo
                print "#"*10
                print "NOTA %s importada" % nfe_sistema.numero
                frete = nfe_sistema.taxas_diversas 
                produtos = nfe_sistema.total_com_imposto
                print "TOTAL DA NOTA: %s (Frete) + %s (Produtos + Impostos)" % (frete, produtos)
                print "Produtos"
                for lancamento in nfe_sistema.lancamentocomponente_set.all():
                    print u"----- PN-FORNECEDOR: %s, QTD: %s VALOR: %s, Impostos: %s%% = TOTAL: %s Unitário (considerando frete proporcional) %s" % (lancamento.part_number_fornecedor, lancamento.quantidade, lancamento.valor_unitario, lancamento.impostos, lancamento.valor_total_com_imposto, lancamento.valor_unitario_final)
                    

            except FabricanteFornecedor.DoesNotExist:
                print u"Erro. Não encontrado Fornecedor com este CNPJ"
            except:
                raise
        else:
            print self.help
            print self.args
