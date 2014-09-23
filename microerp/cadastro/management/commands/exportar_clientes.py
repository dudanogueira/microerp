# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from cadastro.models import Cliente

from optparse import make_option
import os, csv, datetime
import codecs

class Command(BaseCommand):
    help = u'''
        Exporta a base de clientes para importação em sistemas terceiros
        
        FORMATO == ['DIGISAT']
        DIR == ['DIRETORIO QUE QUISER']
        
        '''
    args = "--formato FORMATO --dir DIRETORIO"
    option_list = BaseCommand.option_list + (
    make_option('--formato',
            action='store_true',
            dest='formato',
            help='Define o formato de exportacao',
        ),
    make_option('--dir',
            action='store_true',
            dest='diretorio',
            help='Define o diretorio de exportacao',
        ),
    )

    
    def handle(self, *args, **options):
        formato = args[0]
        diretorio = args[1]
        
        
        # DEFINE ID para todos os registros sem id_referencia
        # descobre o maior id_referencia
        ultimo_id = Cliente.objects.exclude(id_referencia=None).order_by('-id_referencia').first().id_referencia
        print "ULTIMO_ID", ultimo_id
        clientes_sem_id_referencia = Cliente.objects.filter(id_referencia=None)
        for cliente in clientes_sem_id_referencia:
            novo_id = Cliente.objects.exclude(id_referencia=None).order_by('-id_referencia').first().id_referencia + 1
            cliente.id_referencia = novo_id
            cliente.save()
        
        print u"EXPORTANDO para formato: %s no Diretorio: %s" % (args[0], args[1])
        if os.access(args[1], os.W_OK):
            print "OK! Acesso permitido"
            if formato == "DIGISAT":
                clientes = Cliente.objects.filter(ativo=True)
                for cliente in clientes:
                    print cliente.nome
                    id_legado = cliente.id_referencia
                    zero_id_legado = "%05d" % id_legado
                    print 'ID_LEGADO', id_legado, "-->", zero_id_legado
                    nome_arquivo = "C%s.TXT" % zero_id_legado
                    caminho_arquivo = os.path.join(diretorio, nome_arquivo)
                    file = codecs.open(caminho_arquivo, "w", encoding='utf8')
                    # estado / uf
                    try:
                        estado = cliente.endereco_principal().bairro.cidade.estado.strip()
                        if estado == '':
                            estado = 'Null'
                    except: 
                        estado = 'Null'
                    if cliente.conceder_credito:
                        conceder_credito = 1
                    else:
                        conceder_credito = 0
                    
                    
                    endereco = cliente.endereco_principal()
                    if endereco:
                        bairro = endereco.bairro.nome or 'Null'
                        cidade = endereco.bairro.cidade.nome or 'Null'
                        cep = endereco.cep or "Null"
                    
                    if cliente.limite_credito == 0:
                        limite_credito = 0
                    else:
                        limite_credito = cliente.limite_credito
                        
                    file.write(
                            u'''%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\nNull\n%s\nNull\n0\n0\n0\n%s\n%s\n%s\n%s\n%s''' %
                        (
                        zero_id_legado,
                        cliente.nome,
                        cliente.cpf or "Null",
                        cliente.cnpj or "Null",
                        cliente.inscricao_estadual or "Null",
                        cliente.rg or "Null",
                        estado,
                        cliente.qualquer_telefone() or 'Null',
                        cliente.tipo[1].upper() or 'Null',
                        limite_credito,
                        cliente.conceder_credito,
                        conceder_credito,
                        bairro,
                        cep,
                        cidade,
                        
                        )
                    )
                    file.close()
            
        else:
            print u"ERRO! Acesso não permitido ao diretório %s" % diretorio

                    
                
            
            