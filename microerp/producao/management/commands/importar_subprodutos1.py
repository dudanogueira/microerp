# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from optparse import make_option

import os
import xlrd

from producao.models import SubProduto, Componente

class Command(BaseCommand):
    help = "Importa os SubProdutos 1 com Base na Planilha Mestria"
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
                    if "PCI" in arquivo:
                        taggeavel = True
                    else:
                        taggeavel = False
                    print "TAGGEAVEL", taggeavel
                    id_inicial = int(part_number[7:])
                    subproduto,created = SubProduto.objects.get_or_create(part_number=part_number, id=id_inicial)
                    subproduto.nome = nome
                    subproduto.possui_tags = taggeavel
                    subproduto.save()
                    # para cada linha
                    i = 0
                    for curr_row in range(worksheet.nrows):
                        if curr_row > 3:
                            i += 1
                            print '--' * 10
                            print "LINHA", i
                            row = worksheet.row(curr_row)
                            componente_part_number = row[0].value
                            if componente_part_number:
                                print "COMPONENTE PART_NUMBER", componente_part_number
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
                                    componente_da_linha = Componente.objects.get(part_number=componente_part_number)
                                    opcao = linha.opcaolinhasubproduto_set.create(quantidade=quantidade, componente=componente_da_linha, padrao=None)
                                    if row[15].value:
                                        linha.opcaolinhasubproduto_set.all().update(padrao=None)
                                        # define a opcao escolhida como padrao
                                        opcao.padrao = True
                                        opcao.save()

                            
                            


        else:
            print "Deve fornecer um diretorio usando --directory"
