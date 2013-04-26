# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import user_passes_test
from django.core.mail import EmailMessage

# SITES
from django.contrib.sites.models import Site
from account.models import User
# RH
from rh.models import Funcionario
# Cadastro
from cadastro.models import Cliente, PreCliente
from cadastro.models import Recado

from django import forms
#
# FORMS
#

from django_select2.widgets import Select2Widget

from django_select2 import AutoModelSelect2Field


class AdicionarRecadoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        destinatario = kwargs.pop('destinatario')    
        remetente = kwargs.pop('remetente')
        super(AdicionarRecadoForm, self).__init__(*args, **kwargs)
        self.fields['cliente'].empty_label = 'Nenhum Cliente'
        self.fields['remetente'].empty_label = 'Escolha um Remetente'
        self.fields['remetente'].required = True
        self.fields['remetente'].initial = remetente
        self.fields['destinatario'].empty_label = 'Escolha um Destinatario'
        self.fields['destinatario'].required = True
        self.fields['destinatario'].initial = destinatario
    
    class Meta:
        model = Recado
        fields = ('texto', 'remetente', 'cliente', 'destinatario')
    

class PreClienteAdicionarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        sugestao = kwargs.pop('sugestao')
        super(PreClienteAdicionarForm, self).__init__(*args, **kwargs)

#
# DECORATORS
#

def possui_perfil_acesso_recepcao(user, login_url="/"):
    try:
        return user.perfilacessorecepcao
    except:
        return False


@user_passes_test(possui_perfil_acesso_recepcao)
def home(request):
    # widget funcionario
    funcionario_q = request.GET.get('funcionario', False)
    if funcionario_q:
        funcionarios = Funcionario.objects.filter(nome__contains=funcionario_q)
    # widget cliente
    cliente_q = request.GET.get('cliente', False)
    if cliente_q:
        clientes = Cliente.objects.filter(nome__icontains=cliente_q)
        preclientes = PreCliente.objects.filter(nome__icontains=cliente_q, cliente_convertido=None) 
    return render_to_response('frontend/cadastro/cadastro-home.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_recepcao)
def funcionarios_contatos_ver(request, funcionario_id):
    return render_to_response('frontend/cadastro/cadastro-funcionario-ver-contatos.html', locals(), context_instance=RequestContext(request),)
    
@user_passes_test(possui_perfil_acesso_recepcao)
def funcionarios_listar(request):
    funcionarios = Funcionario.objects.exclude(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/cadastro/cadastro-funcionario-listar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_recepcao)
def funcionarios_recados_listar(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)
    return render_to_response('frontend/cadastro/cadastro-funcionario-recados.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_recepcao)   
def funcionarios_recados_adicionar(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)
    try:
        remetente_id = request.user.funcionario.id
    except:
        remetente_id = None
    if request.POST:            
        form = AdicionarRecadoForm(request.POST, destinatario=funcionario.id, remetente=remetente_id)
        if form.is_valid():
            recado = form.save(commit=False)
            recado.adicionado_por = request.user
            recado.save()
            messages.success(request, u'Recado Adicionado com sucesso!')
            # MANDA EMAIL, SE POSSÍVEL
            dest = []
            if funcionario.email or funcionario.user.email:
                dest.append(funcionario.email or funcionario.user.email)
                assunto = u'Novo Recado'
                template = loader.get_template('template_de_email/novo-recado.html')
                d = locals()
                c = Context(d)
                conteudo = template.render(c)
            
                email = EmailMessage(
                        assunto, 
                        conteudo,
                        'SISTEMA',
                        dest,
                    )
                try:
                    email.send(fail_silently=False)
                    messages.success(request, u'Sucesso! Uma mensagem de email foi enviada para este recado!')
                except:
                    messages.error(request, u'Atenção! Não foi enviado uma mensagem por email para este recado!')
            else:
                messages.error(request, u'Informação: Não foi enviado um email para este recado.')

            return redirect(reverse('cadastro:funcionarios_recados_listar', args=[funcionario_id]))

    else:    
        form = AdicionarRecadoForm(destinatario=funcionario.id, remetente=remetente_id)
    return render_to_response('frontend/cadastro/cadastro-funcionario-recados-adicionar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_recepcao)
def preclientes_adicionar(request):
        return render_to_response('frontend/cadastro/cadastro-preclientes-adicionar.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_recepcao)
def preclientes_listar(request):
        return render_to_response('frontend/cadastro/cadastro-preclientes-listar.html', locals(), context_instance=RequestContext(request),)