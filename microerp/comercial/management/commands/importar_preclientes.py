from django.core.management.base import BaseCommand
from optparse import make_option
from rh.models import Funcionario
from cadastro.models import PreCliente
import xlrd, datetime


class Command(BaseCommand):
    help = "Importa os Pre Clientes com Base numa Planilha"
    option_list = BaseCommand.option_list + (
    make_option('--file',
            action='store_true',
            dest='arquivo',
            help='Importa Pre Clientes',
        ),
    )
    
    def handle(self, *args, **options):
        arquivo = options.get('arquivo')
        if arquivo:
            f = args[0]
            print "Arquivo: %s" % f
            workbook = xlrd.open_workbook(f)
            worksheet = workbook.sheets()[0]
            for curr_row in range(worksheet.nrows):
                if curr_row > 1:
                    row = worksheet.row(curr_row)
                    
                    print '-'*50
                    print "LINHA:", curr_row
                    #
                    nome = row[0].value
                    print "NOME:",nome
                    #
                    contato = row[1].value
                    print "CONTATO:",contato
                    #
                    dados = row[2].value
                    print "DADOS:",dados
                    #
                    funcionario_id = row[3].value
                    try:
                        funcionario = Funcionario.objects.get(pk=funcionario_id)
                    except:
                        funcionario = Funcionario.objects.first()
                    print "Funcionario:",funcionario
                    #
                    probabilidade = row[4].value
                    print "PROBABILIDADE:",probabilidade
                    #
                    valor = row[5].value
                    print "VALOR:",valor
                    #
                    observacoes = row[6].value
                    print "OBSERVACOES:",observacoes
                    #
                    texto = row[7].value
                    print "TEXTO FOLLOW UP:",texto
                    #
                    data = xlrd.xldate_as_tuple(row[8].value, 0)
                    print "DATA FOLLOW UP:",data
                    
                    # registra
                    precliente,created = PreCliente.objects.get_or_create(nome=nome.title(), contato=contato, dados=dados, adicionado_por=funcionario)
                    proposta,created = precliente.propostacomercial_set.get_or_create(valor_proposto=valor, probabilidade=probabilidade, criado_por=funcionario, observacoes=dados)
                    followup, crated = proposta.followupdepropostacomercial_set.get_or_create(criado_por=funcionario, texto=texto, probabilidade=probabilidade, criado=datetime.date(data[0], data[1], data[2]))
                    
                    
                    