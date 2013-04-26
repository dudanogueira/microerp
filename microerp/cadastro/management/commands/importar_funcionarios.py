# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from cadastro.models import Cidade, Bairro
from rh.models import Funcionario, PeriodoTrabalhado, Cargo, Departamento

from account.models import User

from optparse import make_option
import os, csv, datetime

from django.utils.encoding import smart_unicode, smart_str

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
                        if usuario:
                            user,created = User.objects.get_or_create(username=usuario, email=email)
                            user.set_password(senha)
                            user.save()
                        else:
                            user = None
                        # admissao
                        bits = str(row['ADMISSAO']).split('/')
                        admissao = datetime.date(int(bits[2]), int(bits[1]), int(bits[0]))
                        # funcionario
                        nome = str(row['NOME'])
                        bits = str(row['NASCIMENTO']).split('/')
                        nascimento = datetime.date(int(bits[2]), int(bits[1]), int(bits[0]))
                        sexo = str(row['SEXO']).lower()
                        rg = str(row['RG'])
                        cpf = str(row['CPF'])
                        telefone_fixo = str(row['TEL_FIXO'])
                        telefone_celular = str(row['TEL_CELULAR'])
                        bairro_str = str(row['BAIRRO'])
                        cidade_str = str(row['CIDADE'])
                        estado = str(row['ESTADO'])
                        cep = str(row['CEP'])
                        rua = str(row['RUA'])
                        numero = str(row['NUMERO'])
                        cargo_str = str(row['CARGO'])
                        departamento_str = str(row['DEPARTAMENTO'])
                        # ADICIONA FUNCIONARIO
                        print "Adicionando: %s" % nome
                        # Pega ou Cria Cidade
                        cidade,created = Cidade.objects.get_or_create(nome=cidade_str, estado=estado)
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
                        funcionario.email=email
                        funcionario.numero=numero
                        funcionario.bairro=bairro
                        funcionario.cargo_inicial = cargo
                        funcionario.salario_inicial=0
                        funcionario.valor_hora=0
                        funcionario.user = user
                        # Periodo Trabalhado
                        periodo,created = PeriodoTrabalhado.objects.get_or_create(inicio=admissao, funcionario=funcionario)
                        funcionario.periodo_trabalhado_corrente = periodo
                        funcionario.save()
                        
                        
                        


            except:
                raise
        else:
            print self.help
            print self.args
