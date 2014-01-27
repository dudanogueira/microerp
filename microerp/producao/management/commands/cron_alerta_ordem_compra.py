# -*- coding: utf-8 -*-
from django.utils import translation
from django.core.management.base import BaseCommand
from producao.models import PerfilAcessoProducao
from producao.models import ControleDeCompra
from producao.models import AtividadeDeCompra
from django.template import RequestContext, loader, Context
from django.core.mail import EmailMessage
from django.db.models import Count
import datetime

class Command(BaseCommand):
    help = "Comando para gerar alertas de Controle de Compras com Atividades Atrasadas"

    def handle(self, *args, **options):
        # puxa todas as ordem com atividades atrasadas,
        # ou seja, com data_fechado=None e data__gte=today
        translation.activate('pt_BR')
        ordens_abertas = ControleDeCompra.objects.filter(
            data_fechado=None,
        )
        
        total_atividades_atrasadas = AtividadeDeCompra.objects.filter(
            controle_de_compra__data_fechado=None,
            data_fechado=None,
            data__lt=datetime.datetime.now(),
        )
        
        total_ordens = len(total_atividades_atrasadas.annotate(total=Count('controle_de_compra')))
    
        # envia email
        if ordens_abertas.count() and total_atividades_atrasadas.count():
            print "ORDENS ABERTAS:", ordens_abertas.count()
            print "ATIVIDADES ATRASADAS", total_atividades_atrasadas.count()
            # puxa os gerentes
            gerentes = PerfilAcessoProducao.objects.filter(gerente=True)
            dest = []
            for gerente in gerentes:
                if gerente.user.email:
                    dest.append(gerente.user.email)
                if gerente.user.funcionario.email:
                    dest.append(gerente.user.funcionario.email)
        
            print "Avisando Gerentes: %s" % dest
            
            template = loader.get_template('template_de_email/ordem-de-compra-atrasada.html')
            d = locals()
            c = Context(d)
            content = template.render(c)
            email = EmailMessage(
                    'Alerta em %s: %s Ordens Abertas com %s Atividades' % (datetime.date.today().strftime("%d/%m/%Y"), total_ordens, total_atividades_atrasadas.count() ), 
                    content,
                    'Sistema MicroERP',
                    dest,
                )
            try:
                email.send(fail_silently=False)
                print "Email Enviado."
            except:
                print "Email não Enviado"
            
            # avisa os responsáveis pelo controle, não gerentes
            for ordem in ordens_abertas:
                dest = []
                if ordem.atrasada():
                    dest.append(ordem.funcionario.user.email or ordem.funcionario.email)
                    template = loader.get_template('template_de_email/ordem-de-compra-atrasada-nao-gerente.html')
                    d = locals()
                    c = Context(d)
                    content = template.render(c)
                    email = EmailMessage(
                            'Alerta em %s: Controle de Compra %s' % (datetime.date.today().strftime("%d/%m/%Y"), ordem.id), 
                            content,
                            'Sistema MicroERP',
                            dest,
                        )
                    try:
                        email.send(fail_silently=False)
                        print "Email Enviado."
                    except:
                        print "Email não Enviado"
                    
            
        else:
            print "Nenhuma Ordem de Compra Atrasada"
        

        