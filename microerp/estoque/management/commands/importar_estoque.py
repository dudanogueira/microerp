# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from estoque.models import Produto
from estoque.models import TipoDeProduto
from estoque.models import TabelaDePreco
from estoque.models import CodigoDeBarra

from django.utils.encoding import smart_text, smart_unicode

from optparse import make_option
import os, csv, datetime

import xlrd

from django.utils.encoding import smart_unicode, smart_str

class Command(BaseCommand):
    help = '''
        Sincroniza para a base de estoque uma planilha conforme:
        
        CODIGO,NOME,FANTASIA,CONTATO,TELEFONE,CELULAR,CNPJ,CPF,IE,RG,ENDERECO,COMPLEMENTO,BAIRRO,NUMERO,CEP,CIDADE,UF,EMAIL,FIS_JUR,TIPO,COD_CONVENIO,CONVENIO,ULTIMA_VENDA,NASCIMENTO,DATA_CADASTRO,A_RECEBER,ATRASADO,RECEBIDO,LIMITE_CREDITO,CONCEDER_CREDITO
        
        '''
    args = "--file arquivo.csv,"
    option_list = BaseCommand.option_list + (
    make_option('--file',
            action='store_true',
            dest='arquivo',
            help='Importa uma lista de Clientes em formato CSV',
        ),
    make_option('--format',
            action='store_true',
            dest='formato',
            help=u'Especificar o formato. Padrão CSV, alternativo: xls',
        ),
    make_option('--delete_after',
            action='store_true',
            dest='delete_after',
            help=u'Apagar após importar',
        ),    
    make_option('--rename_after',
            action='store_true',
            dest='rename_after',
            help=u'Renomear após importar',
        ),    
        
    )


    def handle(self, *args, **options):
        arquivo = options.get('arquivo')
        formato = options.get('formato')
        delete_after = options.get('delete_after')
        rename_after = options.get('rename_after')
        if options['arquivo']:
            f = args[0]
            formato_tipo = args[1]
            try:
                if os.path.isfile(f):
                    if formato:
                        if formato_tipo == "xls":
                            print "Formato XLS"
                            # abre o arquivp
                            print u"ARQUIVO: %s" f
                            workbook = xlrd.open_workbook(f)
                            worksheet = workbook.sheet_by_name('Plan1')
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
                                        tabela_id = tabela_nome.split()[0]
                                        print "TABELA ID:", tabela_id
                                        print u"TABELA NOME: %s" % tabela_nome
                                        if str(tabela_id).isdigit() and tabela_id != 0:
                                            tabela,created = TabelaDePreco.objects.get_or_create(id=tabela_id)
                                        else:
                                            tabela,created = TabelaDePreco.objects.get_or_create(nome=tabela_nome)
                                        print "TABELA CRIADA:",created
                                        produto.tabela = tabela
                                        
                                        
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
                                        
                                        produto.save()
                                
                            # trata o arquivo
                            if rename_after:
                                timestamp = datetime.datetime.now().strftime("%Y%m%d-%H_%M_%S")
                                print "TIMESTAMP",timestamp                                
                                novo_arquivo = "IMPORTADO-EM-%s-%s" % (timestamp, os.path.basename(f))
                                print "NOVOARQUIVO",novo_arquivo
                                novo_caminho = os.path.join(os.path.dirname(f), novo_arquivo)
                                print "NOVOCAMINHO",novo_caminho
                                os.rename(f, novo_caminho)
                            if delete_after:
                                if not rename_after:
                                    os.remove(f)
                        else:
                            print u"Formato Inválido. suportado: xls"
                            
                     # padrao CSV   
                    else:
                        reader = csv.DictReader(open(f, 'r'), delimiter=';')
                        for row in reader:
                            print '-'*50
                            codigo = row['CODIGO']
                            print "CODIGO", codigo
                            produto,created = Produto.objects.get_or_create(codigo=codigo)
                            print "PRODUTO: %s" % produto
                            print "PRODUTO CREATED: %s" % created

                            # ATUALIZAVEIS
                            print "** ATUALIZAVEIS **"
                            # TABELA
                            tabela_nome = row['TABELA_PRECO']
                            tabela_id = tabela_nome.split()[0]
                            print "TABELA ID:", tabela_id
                            print "TABELA NOME: %s" % tabela_nome
                            if str(tabela_id).isdigit() and tabela_id != 0:
                                tabela,created = TabelaDePreco.objects.get_or_create(id=tabela_id)
                            else:
                                tabela,created = TabelaDePreco.objects.get_or_create(nome=tabela_nome)
                            print "TABELA CRIADA: %s" % created
                            produto.tabela = tabela
                        
                            # TIPO / GRUPO
                            tipo_id = row['GRUPO']
                            if tipo_id == 0 or tipo_id == '0':
                                tipo = None
                            else:
                                tipo,created = TipoDeProduto.objects.get_or_create(id=tipo_id)
                                tipo.nome = "GRUPO %s" % tipo.id
                                tipo.save()
                            print "TIPO:,",tipo
                            produto.tipo = tipo
                        
                            relacoes = (
                                # CAMPO CSV, CAMPO BD, LOWER/STRIP, 
                                ('NOME', 'nome', False),
                                ('DESCRICAO', 'descricao', False),
                                ('UND_V', 'unidade_de_venda', True),
                                ('UND_C', 'unidade_de_compra', True),
                                ('FATOR', 'fator', False),
                                ('QTD_ESTOQUE', 'quantidade_em_estoque', False),
                                ('NCM', 'ncm', False)
                            )
                        
                            print "### REALIZANDO RELACOES"      
                            for relacao in relacoes:
                                valor_antigo = getattr(produto, relacao[1], None)
                                valor_novo = str(row[relacao[0]])
                                print "CHAVES: %s > %s" % (relacao[0], relacao[1])
                                print "VALORES: %s > %s" % (valor_antigo, smart_unicode(valor_novo))
                            
                                if relacao[2]:
                                    valor_novo = valor_novo.strip().lower()
                            

                                if valor_novo == 'nulo' or valor_novo == '' or valor_novo == 'NULO':
                                    valor_novo = None
                                
                                setattr(produto, relacao[1], valor_novo)
                        
                            produto.preco_custo = float(row['PRECO_CUSTO'])
                            print "PRECO DE CUSTO:", produto.preco_custo
                            produto.save()



                else:
                    print u"ERRO. Arquivo não encontrado. %s" % f
            except:
                raise
        else:
            print self.help
            print self.args
