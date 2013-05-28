# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError
from django_localflavor_br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField


from django.db import models
from django import forms

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.db.models import Count

# APPS MODELS
from rh.models import Departamento
from cadastro.models import Cliente, PreCliente
from solicitacao.models import Solicitacao
from comercial.models import PropostaComercial

from django.conf import settings

from rh import utils

from django.http import HttpResponse

#
# FORMULARIOS
#


from django_select2.widgets import Select2Widget

from django_select2 import AutoModelSelect2Field


class AdicionarPropostaForm(forms.ModelForm):
    
    class Meta:
        model = PropostaComercial
        fields = 'status', 'probabilidade', 'valor_proposto', 'observacoes'
    
    

class AdicionarSolicitacaoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente')    
        precliente = kwargs.pop('precliente')
        super(AdicionarSolicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['contato'].label = "Contato / Reclamante"
        self.fields['cliente'].widget.attrs['class'] = 'select2'
        self.fields['precliente'].widget.attrs['class'] = 'select2'
        if cliente:
            self.fields['cliente'].initial = cliente
            self.fields['precliente'].widget = forms.HiddenInput()
            self.fields['contato'].widget = forms.HiddenInput()
        elif precliente:
            self.fields['precliente'].initial = precliente
            self.fields['cliente'].widget = forms.HiddenInput()
            self.fields['contato'].widget = forms.HiddenInput()
        else:
            self.fields['cliente'].widget = forms.HiddenInput()
            self.fields['precliente'].widget = forms.HiddenInput()
            
        
    
    class Meta:
        model = Solicitacao
        fields = 'descricao', 'cliente', 'precliente', 'contato', 'tipo',



class AdicionarCliente(forms.ModelForm):
    
    def clean_telefone_fixo(self):
        telefone_fixo = self.cleaned_data['telefone_fixo']
        if not telefone_fixo:
            raise forms.ValidationError("Preencha este campo")
    
    def clean_cpf(self):
        tipo = self.cleaned_data.get('tipo', None)
        cpf = self.cleaned_data.get('cpf', None)
        if tipo == 'pf' and not cpf:
            raise ValidationError(u"Para Clientes do tipo PF (Pessoa Física) é necessário informar o CPF")
        elif tipo =='pf' and cpf:
            try:
                cpf = BRCPFField().clean(cpf)
            except:
                raise ValidationError(u"Número do CPF Inválido!")
            
        
    def clean_cnpj(self):
        tipo = self.cleaned_data.get('tipo', None)
        cnpj = self.cleaned_data.get('cnpj', None)
        if tipo == 'pj' and not cnpj:
            raise ValidationError(u"Para Clientes do tipo PJ (Pessoa Jurídica) é necessário informar o CNPJ")
        elif tipo == 'pj' and cnpj:
            try:
                cnpj = BRCNPJField().clean(cnpj)
            except:
                raise ValidationError(u"Número do CNPJ Inválido!")

    
    def __init__(self, *args, **kwargs):
        precliente = kwargs.pop('precliente')
        super(AdicionarCliente, self).__init__(*args, **kwargs)
        self.fields['tipo'].required = True
        if precliente:
            self.fields['nome'].initial = precliente.nome
            self.fields['observacao'].initial = precliente.dados
    
    class Meta:
        model = Cliente
        fields = 'nome', 'tipo', 'fantasia', 'cnpj', 'inscricao_estadual', \
        'cpf', 'rg', 'nascimento', 'ramo', 'observacao', 'origem',\
        'contato', 'email', 'telefone_fixo', 'telefone_celular', 'fax',\
        'funcionario_responsavel'
        

#
# DECORADORES
#

def possui_perfil_acesso_comercial(user, login_url="/"):
    try:
        if user.perfilacessocomercial and user.funcionario.periodo_trabalhado_corrente:
            return True
    except:
        return False


def possui_perfil_acesso_comercial_gerente(user, login_url="/"):
    try:
        if user.perfilacessocomercial and user.funcionario.periodo_trabalhado_corrente and user.perfilacessocomercial.gerente and user.funcionario:
            return True
    except:
        return False


#
# VIEWS
#

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def home(request):
    # widget cliente
    cliente_q = request.GET.get('cliente', False)
    if cliente_q:
        clientes = Cliente.objects.filter(nome__icontains=cliente_q)
        preclientes = PreCliente.objects.filter(nome__icontains=cliente_q, cliente_convertido=None) 
        if not request.user.perfilacessocomercial.gerente:
            clientes = clientes.filter(funcionario_responsavel=request.user.funcionario)
    
    return render_to_response('frontend/comercial/comercial-home.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def cliente_ver(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    return render_to_response('frontend/comercial/comercial-cliente-ver.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def precliente_converter(request, pre_cliente_id):
    precliente = get_object_or_404(PreCliente, id=pre_cliente_id)
    if request.POST:
        form = AdicionarCliente(request.POST, precliente=precliente)
        if form.is_valid():
            cliente_novo = form.save()
            precliente.cliente_convertido = cliente_novo
            precliente.save()
            return redirect(reverse('comercial:cliente_ver', args=[cliente_novo.id]))
    else:
        form = AdicionarCliente(precliente=precliente)
    return render_to_response('frontend/comercial/comercial-precliente-converter.html', locals(), context_instance=RequestContext(request),)


def propostas_comerciais_cliente(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    propostas_abertas = PropostaComercial.objects.filter(cliente=cliente, status='aberta')
    return render_to_response('frontend/comercial/comercial-propostas-cliente.html', locals(), context_instance=RequestContext(request),)

def propostas_comerciais_cliente_adicionar(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    if request.POST:
        form = AdicionarPropostaForm(request.POST)
        if form.is_valid:
            proposta = form.save(commit=False)
            proposta.cliente = cliente
            proposta.adicionado_por = request.user
            proposta.save()
            return redirect(reverse('comercial:propostas_comerciais_cliente', args=[cliente.id]))
    else:
        form = AdicionarPropostaForm()
    return render_to_response('frontend/comercial/comercial-propostas-cliente-adicionar.html', locals(), context_instance=RequestContext(request),)


# PRECLIENTE

def propostas_comerciais_precliente(request, precliente_id):
    precliente = PreCliente.objects.get(pk=precliente_id)
    propostas_abertas = PropostaComercial.objects.filter(precliente=precliente, status='aberta')
    return render_to_response('frontend/comercial/comercial-propostas-precliente.html', locals(), context_instance=RequestContext(request),)
    


def propostas_comerciais_precliente_adicionar(request, precliente_id):
    precliente = PreCliente.objects.get(pk=precliente_id)
    if request.POST:
        form = AdicionarPropostaForm(request.POST)
        if form.is_valid():
            proposta = form.save(commit=False)
            proposta.precliente = precliente
            proposta.adicionado_por = request.user
            proposta.save()
            return redirect(reverse('comercial:propostas_comerciais_precliente', args=[precliente.id]))
    else:
        form = AdicionarPropostaForm()
    return render_to_response('frontend/comercial/comercial-propostas-precliente-adicionar.html', locals(), context_instance=RequestContext(request),)
    

def propostas_comerciais_minhas(request):
    minhas_propostas = PropostaComercial.objects.filter(adicionado_por=request.user, status="aberta")
    propostas_em_meus_clientes = PropostaComercial.objects.filter(cliente__funcionario_responsavel=request.user.funcionario, status="aberta").exclude(adicionado_por=request.user)
    return render_to_response('frontend/comercial/comercial-propostas-minhas.html', locals(), context_instance=RequestContext(request),)

#
# VIEWS EXTERNAS / MODULOS
#

@user_passes_test(possui_perfil_acesso_comercial)
def solicitacao_adicionar(request):
    if not 'solicitacao' in settings.INSTALLED_APPS:
            messages.error(request, u'Modulo de Solicitação não instalado')
            return redirect(reverse('comercial:home'))
    cliente_id = request.GET.get('cliente', None)
    precliente_id = request.GET.get('precliente', None)
    if request.POST:
        form = AdicionarSolicitacaoForm(request.POST, cliente=cliente_id, precliente=precliente_id)
        if form.is_valid():
            solicitacao = form.save()
            messages.success(request, 'Solicitação #%d criada com sucesso!' % solicitacao.id)
            return redirect(reverse('comercial:home'))
    else:
        form = AdicionarSolicitacaoForm(cliente=cliente_id, precliente=precliente_id)
    return render_to_response('frontend/comercial/comercial-solicitacao-adicionar.html', locals(), context_instance=RequestContext(request),)



