# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from cadastro.models import Cliente, Cidade, Ramo, Bairro

from optparse import make_option
import os, csv, datetime

from django.utils.encoding import smart_unicode, smart_str

class Command(BaseCommand):
    help = '''
        Sincroniza para a base de clientes uma planilha conforme:
        
        CODIGO,NOME,FANTASIA,CONTATO,TELEFONE,CELULAR,CNPJ,CPF,IE,RG,ENDERECO,COMPLEMENTO,BAIRRO,NUMERO,CEP,CIDADE,UF,EMAIL,FIS_JUR,TIPO,COD_CONVENIO,CONVENIO,ULTIMA_VENDA,NASCIMENTO,DATA_CADASTRO,A_RECEBER,ATRASADO,RECEBIDO,LIMITE_CREDITO,CONCEDER_CREDITO,ATIVO
        
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
                    reader = csv.DictReader(open(f, 'r'))
                    for row in reader:
                        print '-'*50
                        id_referencia = int(row['CODIGO'])
                        cidade = str(row['CIDADE']) or u"Não informado"
                        estado = str(row['UF'])
                        nome_bairro = str(row['BAIRRO']) or u"Não informado"
                        nome_cliente = str(row['NOME'])
                        nome_fantasia = str(row['FANTASIA'])
                        email = str(row['EMAIL'])
                        # data cadastro
                        data_cadastro = datetime.datetime.strptime(str(row['DATA_CADASTRO']), "%d.%m.%Y")
                        nascimento = str(row['NASCIMENTO'])
                        if nascimento == '':
                            nascimento = None
                        else:
                            nascimento = datetime.datetime.strptime(nascimento, "%d.%m.%Y")
                        contato = str(row['CONTATO'])
                        fantasia = str(row['FANTASIA'])
                        rua = str(row['ENDERECO'])
                        complemento = str(row['COMPLEMENTO'])
                        numero = str(row['NUMERO'])
                        cep = str(row['CEP'])
                        tipo_cliente = str(row['FIS_JUR'])
                        telefone = str(row['TELEFONE']) or None
                        celular = str(row['CELULAR']) or None
                        conceder_credito = str(row['CONCEDER_CREDITO']) or None
                        limite_credito = str(row['LIMITE_CREDITO']) or 0
                        ie = str(row['IE']) or None
                        rg = str(row['RG']) or None
                        try:
                            ativo = str(row['ATIVO'])
                        except:
                            ativo = "Sim"
                        print "ID LEGADO:",id_referencia
                        print "NOME CLIENTE:",nome_cliente
                        # DEFINE CIDADE
                        cidade,created = Cidade.objects.get_or_create(
                            nome=cidade, estado=estado
                        )
                        cidade_nome = smart_unicode(cidade.nome)
                        if created:
                            print "CIDADE *CRIADA*:",cidade_nome
                        else:
                            print "CIDADE:",cidade_nome
                        # DEFINE BAIRRO
                        bairro = Bairro.objects.filter(
                            cidade=cidade, nome=nome_bairro
                        ).first()
                        if bairro:
                            print "BAIRRO:",nome_bairro
                        else:
                            print "BAIRRO *CRIADO*:",nome_bairro
                            bairro = Bairro.objects.create(
                                cidade=cidade, nome=nome_bairro
                            )
                        # DEFINE TIPO DE CLIENTE
                        print "TIPO:",tipo_cliente
                        if tipo_cliente[0] == u"F":
                            tipo = 'pf'
                            cpf = str(row['CPF'])
                            print "CPF:",cpf
                        else:
                            tipo = 'pj'
                            cnpj = str(row['CNPJ'])
                            print "CNPJ",cnpj
                        # DEFINO ATIVO OU NAO
                        if ativo.lower() == "sim":
                            cliente_ativo = True
                        else:
                            cliente_ativo = False
                        print "ATIVO", ativo
                        # DEFINE CREDITO
                        if conceder_credito.lower() == "sim":
                            conceder_credito = True
                        else:
                            conceder_credito = False
                        print "CONCEDER CREDITO", conceder_credito
                        print "LIMITE DE CREDITO", limite_credito
                        # DEFINE CLIENTE
                        try:
                            cliente = Cliente.objects.get(
                                id_referencia=id_referencia
                            )
                            print "CLIENTE %s Já importado. Atualizando" % cliente
                        except Cliente.DoesNotExist:
                            print "NOVO CLIENTE!"
                            cliente = Cliente.objects.create(
                                id_referencia=id_referencia
                            )
                        cliente.nome = nome_cliente
                        cliente.fantasia = nome_fantasia
                        cliente.nascimento = nascimento
                        cliente.tipo = tipo
                        cliente.email = email
                        cliente.contato = contato
                        cliente.criado = data_cadastro
                        cliente.ativo = cliente_ativo
                        cliente.conceder_credito = conceder_credito
                        cliente.limite_credito = limite_credito
                        if cliente.tipo == 'pj':
                            cliente.cnpj = cnpj
                        else:
                            cliente.cpf = cpf
                        cliente.rg = rg
                        cliente.inscricao_estadual = ie
                        print "CONTATO",contato
                        print "TELEFONE:",telefone
                        print "CELULAR:",celular
                        cliente.telefone_fixo = telefone
                        cliente.telefone_celular = celular
                        # CRIAR ENDEREÇO
                        telelefone_associado = telefone or celular
                        endereco,created = cliente.enderecocliente_set.get_or_create(bairro=bairro, rua=rua, numero=numero, telefone=telelefone_associado, cep=cep, complemento=complemento)
                        if created:
                            print "ENDERECO CRIADO"
                        #cliente.clean()
                        cliente.save()

            except:
                raise
        else:
            print self.help
            print self.args
