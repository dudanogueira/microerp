# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import datetime
from rh.models import Funcionario

class Command(BaseCommand):
    help = "Cria as folhas de Ponto do mês corrente para todos os funcionários"

    def handle(self, *args, **options):
        today = datetime.date.today()
        funcionarios = Funcionario.objects.exclude(periodo_trabalhado_corrente=None)
        criados = []
        for funcionario in funcionarios:
            folha,create = funcionario.folhadeponto_set.get_or_create(data_referencia__month=today.month, data_referencia__year=today.year, periodo_trabalhado=funcionario.periodo_trabalhado_corrente)
            if create:
                criados.append(folha) 
                print "%s - criar_folhas.py - CRIADO %s" % (folha, today)
        if len(criados) == 0:
            print "%s - criar_folhas.py - NENHUMA FOLHA CRIADA" % today