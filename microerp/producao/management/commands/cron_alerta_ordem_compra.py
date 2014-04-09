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

from optparse import make_option

class Command(BaseCommand):
    help = "Comando para gerar alertas de Controle de Compras com Atividades Atrasadas"
    option_list = BaseCommand.option_list + (
        make_option('--resumido',
                action='store_true',
                dest='resumido',
                help='Resumo o alerta dos não gerentes',
            ),
        )
    

    def handle(self, *args, **options):
        # puxa todas as ordem com atividades atrasadas,
        # ou seja, com data_fechado=None e data__gte=today
        resumido = options.get('resumido')
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
                try:
                    if gerente.user.email:
                        dest.append(gerente.user.email)
                    elif gerente.user.funcionario.email:
                        dest.append(gerente.user.funcionario.email)
                except:
                    pass
        
            print "Avisando Gerentes: %s" % dest
            
            template = loader.get_template('template_de_email/ordem-de-compra-atrasada.html')
            d = locals()
            c = Context(d)
            content = template.render(c)
            assunto = 'Alerta em %s: %s Ordens Abertas com %s Atividades' % (datetime.date.today().strftime("%d/%m/%Y"), total_ordens, total_atividades_atrasadas.count() )
            email = EmailMessage(
                    assunto, 
                    content,
                    'Sistema MicroERP',
                    dest,
                )
            try:
                email.send(fail_silently=False)
                print "ASSUNTO:",assunto
                print content
                print "Email Enviado."
            except:
                print "Email não Enviado"

            print "######## ALERTA DE NÃO GERENTES #########"
            dest = []
            if resumido:
                print '# MODO RESUMIDO #'
                nao_gerentes = PerfilAcessoProducao.objects.filter(gerente=False)
                for perfil in nao_gerentes:
                    print '#' * 10
                    print "PERFIL: %s" % perfil
                    funcionario = perfil.user.funcionario
                    controles_atrasados = funcionario.controledecompra_set.filter(data_fechado=None, atividadedecompra__data_fechado=None, atividadedecompra__data__lt=datetime.datetime.now())
                    if controles_atrasados:
                        try:
                            email = funcionario.user.email or funcionario.email
                        except:
                            email = None
                        if controles_atrasados and email:
                            dest.append(email)
                            template = loader.get_template('template_de_email/ordem-de-compra-atrasada-nao-gerente-resumido.html')
                            d = locals()
                            c = Context(d)
                            content = template.render(c)
                            assunto = 'Alerta em %s: %s Controle de Compras Atrasado' % (datetime.date.today().strftime("%d/%m/%Y"), controles_atrasados.count())
                            email = EmailMessage(
                                    assunto, 
                                    content,
                                    'Sistema MicroERP',
                                    dest,
                                )
                            try:
                                email.send(fail_silently=False)
                                print "Email Enviado para %s" % dest
                                print "ASSUNTO: %s" % assunto
                                print content
                            except:
                                print "Email não Enviado"
                            
                    else:
                        print "NENHUM CONTROLE ATRASADO"
                    

                
            else:
            # avisa os responsáveis pelo controle, não gerentes
                for ordem in ordens_abertas:
                    if ordem.atrasada():
                        print "\n##### NOVO EMAIL\n"
                        print "FUNCIONÁRIO:",ordem.funcionario
                        try:
                            email = ordem.funcionario.user.email or ordem.funcionario.email
                        except:
                            email = None
                            pass
                        if email:
                            dest.append(email)
                            template = loader.get_template('template_de_email/ordem-de-compra-atrasada-nao-gerente.html')
                            d = locals()
                            c = Context(d)
                            content = template.render(c)
                            assunto = 'Alerta em %s: Controle de Compra ID#%s' % (datetime.date.today().strftime("%d/%m/%Y"), ordem.id)
                            email = EmailMessage(
                                    assunto, 
                                    content,
                                    'Sistema MicroERP',
                                    dest,
                                )
                            try:
                                #email.send(fail_silently=False)
                                print "Email Enviado para %s" % dest
                                print "ASSUNTO: %s" % assunto
                                print content
                            except:
                                print "Email não Enviado"

        else:
            print "Nenhuma Ordem de Compra Atrasada"
