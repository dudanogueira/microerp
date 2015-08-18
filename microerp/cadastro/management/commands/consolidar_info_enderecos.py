# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from cadastro.models import EnderecoCliente

class Command(BaseCommand):
    help = '''
        Consolida Informações do Endereco, copiando pra modo texto o campo de Bairro, Cidade e UF:
        
        '''

    
    def handle(self, *args, **options):
        for endereco in EnderecoCliente.objects.all():
            endereco.bairro_texto = endereco.bairro.nome
            endereco.cidade_texto = endereco.bairro.cidade.nome
            endereco.uf_texto = endereco.bairro.cidade.estado
            endereco.save()