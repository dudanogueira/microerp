# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from django.contrib.sites.models import Site

from cadastro.models import Cidade, Bairro
from rh.models import Funcionario, PeriodoTrabalhado, Cargo, Departamento

from account.models import User

from optparse import make_option
import os, csv, datetime

from django.utils.encoding import smart_unicode, smart_str

def parse_string_de_data(string):
    bits = str(string).split('-')
    if len(bits) == 3:
        data = datetime.date(int(bits[0]), int(bits[1]), int(bits[2]))
        return data
    else:
        return None

class Command(BaseCommand):
    help = '''
        Sincroniza para a base de Funcionários uma planilha como em:
        USUARIO,SENHA,ADMISSAO,NOME,NASCIMENTO,SEXO,RG,CPF,ESTUDOS_FIM,EMAIL,TEL_FIXO,TEL_CELULAR,BAIRRO,CIDADE,ESTADO,CEP,RUA,NUMERO,CARGO,DEPARTAMENTO
    '''
    args = "--file arquivo.csv,"
    option_list = BaseCommand.option_list + (
    make_option('--file',
            action='store_true',
            dest='arquivo',
            help='Importa uma lista de Funcionários em CSV',
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
                        # usuario
                        usuario = str(row['USUARIO'])
                        senha = str(row['SENHA'])
                        email = str(row['EMAIL'])
                        status = str(row['STATUS'])
                        if usuario:
                            dominio = 'teste.com'
                            user,created = User.objects.get_or_create(username=usuario)
                            print "CRIADO:%s, User:%s" % (created, user)
                            user.set_password(senha)
                            if email == '':
                                email = "%s@%s" % (user.username, dominio)
                                print "EMAIL:",email
                            user.email = email
                            user.save()
                        else:
                            user = None
                        print "USERNAME", user
                        print "SENHA", senha
                        print "EMAIL",email
                        print "STATUS:",status
                        # admissao
                        admissao = str(row['ADMISSAO'])
                        admissao = parse_string_de_data(admissao)
                        print "ADMISSAO", admissao
                        # demissao
                        demissao = str(row['DEMISSAO'])
                        demissao = parse_string_de_data(demissao)
                        print "DEMISSAO", demissao

                        # funcionario
                        nome = str(row['NOME'])
                        print "NOME", nome
                        bits = str(row['NASCIMENTO']).split('-')
                        nascimento = datetime.date(int(bits[0]), int(bits[1]), int(bits[2]))
                        print "NASCIMENTO", nascimento
                        sexo = str(row['SEXO']).lower()
                        print "SEXO", sexo
                        rg = str(row['RG'])
                        print "RG",rg
                        cpf = str(row['CPF'])
                        print "CPF",cpf
                        telefone_fixo = str(row['TEL_FIXO'])
                        print "FIXO", telefone_fixo
                        telefone_celular = str(row['TEL_CELULAR'])
                        print "CELULAR", telefone_celular
                        bairro_str = str(row['BAIRRO'])
                        print "BAIRRO", row['BAIRRO']
                        cidade_str = str(row['CIDADE'])
                        estado_str = str(row['ESTADO'])
                        cep = str(row['CEP'])
                        rua = str(row['RUA'])
                        numero = str(row['NUMERO'])
                        pis = str(row['PIS'])
                        cargo_str = str(row['CARGO'])
                        departamento_str = str(row['DEPARTAMENTO'])
                        # ADICIONA FUNCIONARIO
                        print "Adicionando: %s" % nome
                        # Pega ou Cria Cidade
                        print "ESTADO: %s" % (estado_str)
                        print "CIDADE: %s" % (cidade_str)
                        cidade,created = Cidade.objects.get_or_create(nome=cidade_str, estado=estado_str)
                        print "CIDADE: %s, Criado: %s" % (cidade, created)
                        # Pega ou Cria Bairro
                        bairro,created = Bairro.objects.get_or_create(nome=bairro_str, cidade=cidade)
                        # PEGA ou Cria Departamento
                        departamento,created = Departamento.objects.get_or_create(nome=departamento_str)
                        cargo,created = Cargo.objects.get_or_create(
                            nome=cargo_str,
                            departamento=departamento,
                            salario_referencia=0,
                            periculosidade=0,
                            gratificacao=0,
                        )
                        # cria funcionario
                        if user:
                            funcionario,created = Funcionario.objects.get_or_create(
                                user=user,
                                nascimento=nascimento,
                                bairro=bairro,
                                cargo_inicial=cargo,
                            )
                        else:
                            funcionario,created = Funcionario.objects.get_or_create(
                                nome=nome,
                                nascimento=nascimento,
                                bairro=bairro,
                                cargo_inicial=cargo,
                            )
                            
                        funcionario.nome=nome
                        funcionario.sexo=sexo
                        funcionario.rg=rg
                        funcionario.cpf=cpf
                        funcionario.telefone_fixo=telefone_fixo
                        funcionario.telefone_celular=telefone_celular
                        funcionario.cep=cep
                        funcionario.rua=rua
                        funcionario.pis=pis
                        funcionario.email=email
                        funcionario.numero=numero
                        funcionario.bairro=bairro
                        funcionario.cargo_inicial = cargo
                        funcionario.salario_inicial=0
                        funcionario.valor_hora=0
                        funcionario.user = user
                        # Periodo Trabalhado
                        periodo,created = PeriodoTrabalhado.objects.get_or_create(inicio=admissao, funcionario=funcionario)
                        if demissao:
                            periodo.fim = demissao
                            periodo.save()
                            funcionario.periodo_trabalhado_corrente = None
                        else:
                            funcionario.periodo_trabalhado_corrente = periodo
                        funcionario.save()
                        
                        
                        


            except:
                raise
        else:
            print self.help
            print self.args
