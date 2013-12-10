# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from optparse import make_option

import os
import xlrd

from producao.models import SubProduto, Componente

class Command(BaseCommand):
    help = "Importa os SubProdutos 2 com Base na Planilha Mestria"
    option_list = BaseCommand.option_list + (
    make_option('--directory',
            action='store_true',
            dest='diretorio',
            help='Importa uma pasta inteira com panilha de subprodutos',
        ),
    )
    def handle(self, *args, **options):
        diretorio = options.get('diretorio')
        if diretorio:
            d = args[0]
            print u"Diretório: %s" % d
            arquivos = os.listdir(d)
            for arquivo in arquivos:
                if arquivo.endswith('.xlsx'):
                    print "#" * 20
                    print "ARQUIVO", arquivo
                    caminho_do_arquvo = os.path.join(d, arquivo)
                    workbook = xlrd.open_workbook(caminho_do_arquvo)
                    worksheet = workbook.sheets()[0]
                    part_number = worksheet.row(1)[13].value
                    nome = worksheet.row(0)[13].value
                    print "SUBPRODUTO:", part_number
                    print "NOME", nome
                    subproduto,created = SubProduto.objects.get_or_create(part_number=part_number)
                    subproduto.nome = nome
                    subproduto.save()
                    i = 0
                    for curr_row in range(worksheet.nrows):
                        if curr_row > 3:
                            i += 1
                            print '--' * 10
                            print "LINHA", i
                            row = worksheet.row(curr_row)
                            
                            quantidade = row[13].value
                            try:
                                quantidade = int(quantidade)
                            except:
                                quantidade = 1
                            print "QUANTIDADE:", quantidade
                            
                            part_number_linha = row[0].value
                            if part_number_linha and "SUB" in part_number_linha:
                                print "SUBPRODUTO: ", part_number_linha
                                # tratar como subproduto agregado
                                subproduto_da_linha,created = SubProduto.objects.get_or_create(
                                    part_number=part_number_linha
                                )
                                subproduto.linhasubprodutos_agregados.create(
                                    subproduto_agregado=subproduto_da_linha,
                                    quantidade=quantidade,
                                    )
                            else:
                                # tratar como componente
                                print "COMPONENTE: ", part_number_linha
                                tag = row[16].value
                                print "TAG", tag
                                tags = str(tag).split(":")
                                if len(tags) == 1:
                                    quantidade = row[13].value
                                    if quantidade == '-':
                                        quantidade=1
                                else:
                                    quantidade = 1
                                
                                for tag in tags:
                                    linha,created = subproduto.linhasubproduto_set.get_or_create(tag=tag)
                                    if part_number_linha:
                                        componente_da_linha = Componente.objects.get(part_number=part_number_linha)
                                        opcao = linha.opcaolinhasubproduto_set.create(
                                            quantidade=quantidade,
                                            componente=componente_da_linha,
                                            padrao=None
                                        )
                                        if row[15].value:
                                            linha.opcaolinhasubproduto_set.all().update(padrao=None)
                                            # define a opcao escolhida como padrao
                                            opcao.padrao = True
                                            opcao.save()
                                
                            
                    

        else:
            print "Deve fornecer um diretorio usando --directory"
