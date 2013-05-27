# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from estoque.models import Produto
from estoque.models import TipoDeProduto
from estoque.models import TabelaDePreco
from estoque.models import CodigoDeBarra

from optparse import make_option
import os, csv, datetime

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
    )


    def handle(self, *args, **options):
        arquivo = options.get('arquivo')
        if options['arquivo']:
            f = args[0]
            try:
                if os.path.isfile(f):
                    reader = csv.DictReader(open(f, 'r'), delimiter=';')
                    for row in reader:
                        print '-'*50
                        codigo = row['CODIGO']
                        print "CODIGO", codigo
                        produto,created = Produto.objects.get_or_create(codigo=codigo)
                        print "PRODUTO:", produto
                        print "PRODUTO CREATED:",created

                        # ATUALIZAVEIS
                        print "** ATUALIZAVEIS **"
                        # TABELA
                        tabela_nome = row['TABELA_PRECO']
                        tabela_id = tabela_nome.split()[0]
                        print "TABELA ID:", tabela_id
                        print "TABELA NOME:", tabela_nome
                        if str(tabela_id).isdigit() and tabela_id != 0:
                            tabela,created = TabelaDePreco.objects.get_or_create(id=tabela_id)
                        else:
                            tabela,created = TabelaDePreco.objects.get_or_create(nome=tabela_nome)
                        print "TABELA CRIADA:",created
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
                        
                        produto.preco_custo = row['PRECO_CUSTO']
                        print "PRECO DE CUSTO:", produto.preco_custo
                        produto.save()


            except:
                raise
        else:
            print self.help
            print self.args
