# -*- coding: utf-8 -*-
"""This file is part of the microerp project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Duda Nogueira <dudanogueira@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Duda Nogueira'
__version__ = '0.0.1'

#
# VIEWS
#
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.urlresolvers import reverse
from django import forms

from django.db.models import Sum

from rh.utils import get_weeks

from comercial.models import ContratoFechado
from financeiro.models import Lancamento

import datetime

def possui_perfil_acesso_financeiro(user, login_url="/"):
    try:
        if user.perfilacessofinanceiro and user.funcionario.ativo():
            return True
    except:
        return False

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def home(request):
    # widget do contratos
    contratos_tipo_fechado = ContratoFechado.objects.filter(status="emaberto", tipo="fechado", receber_apos_conclusao=False)
    contratos_tipo_aberto = ContratoFechado.objects.filter(status="emaberto", tipo="aberto")
    contratos_tipo_mensal = ContratoFechado.objects.filter(status="emaberto", tipo="mensal")
    contratos_receber_apos_conclusao = ContratoFechado.objects.filter(status="emaberto", tipo="fechado", receber_apos_conclusao=True)
    total_aberto = ContratoFechado.objects.filter(status="emaberto").count()
    return render_to_response('frontend/financeiro/financeiro-home.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def contratos_a_lancar(request):
    contratos_fechados_a_receber = ContratoFechado.objects.filter(status="emaberto", tipo="fechado", receber_apos_conclusao=False)
    contratos_fechados_receber_apos_conclusao = ContratoFechado.objects.filter(status="emaberto", tipo="fechado", receber_apos_conclusao=True)
    contratos_abertos = ContratoFechado.objects.filter(status="emaberto", tipo="aberto")
    contratos_mensais = ContratoFechado.objects.filter(status="emaberto", tipo="mensal")
    return render_to_response('frontend/financeiro/financeiro-contratos-a-lancar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def ver_contrato(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    return render_to_response('frontend/financeiro/financeiro-ver-contrato.html', locals(), context_instance=RequestContext(request),)

# Adicionar Lancamento em Contrato
class AdicionarLancamentoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        contrato = kwargs.pop('contrato')
        proximo_peso = kwargs.pop('proximo_peso')
        super(AdicionarLancamentoForm, self).__init__(*args, **kwargs)
        if contrato:
            self.fields['contrato'].widget = forms.HiddenInput()
            self.fields['contrato'].initial = contrato.id
            self.fields['data_cobranca'].widget.attrs['class'] = 'datepicker'
            self.fields['data_recebido'].widget.attrs['class'] = 'datepicker'
            self.fields['data_recebido_em_conta'].widget.attrs['class'] = 'datepicker'
        if proximo_peso:
            self.fields['peso'].initial = proximo_peso
    
    class Meta:
        model = Lancamento

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def realizar_lancamento(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    if contrato.status == 'emaberto':
        messages.success(request, u'Sucesso! Contrato #%s Lançado!' % contrato.id)
        contrato.lancar(request)
        
    else:
        messages.error(request, u'Erro! Contrato não está em Aberto')
    return redirect(reverse('financeiro:contratos_a_lancar'))

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def contrato_adicionar_lancamento(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    if contrato.status == 'emaberto':
        if request.POST:
            form = AdicionarLancamentoForm(request.POST, contrato=contrato, proximo_peso=contrato.proximo_peso_lancamento())
            if form.is_valid():
                lancamento = form.save()
                messages.success(request, "Sucesso! Lançamento realizado!" )
                return(redirect("financeiro:contratos_a_lancar"))
        else:
            form = AdicionarLancamentoForm(contrato=contrato, proximo_peso=contrato.proximo_peso_lancamento())
        
    else:
        messages.error(request, u'Erro! Contrato não está em Aberto')
    return render_to_response('frontend/financeiro/financeiro-contrato-adicionar-lancamento.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def contrato_fechar(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    contrato.status = "lancado"
    contrato.concluido = True
    contrato.save()
    return(redirect("financeiro:contratos_a_lancar"))

# Lancamentos a Receber
@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def lancamentos_a_receber_receber(request, lancamento_id):
    lancamento = get_object_or_404(Lancamento, pk=lancamento_id, data_recebido=None)
    if request.POST:
        form = FormIdentificarRecebido(request.POST, instance=lancamento)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.situacao = "r"
            lancamento.recebido_por = request.user
            lancamento.save()

            return(redirect("financeiro:lancamentos_a_receber"))
    else:
        form = FormIdentificarRecebido(instance=lancamento, initial = {
            'data_recebido' : datetime.date.today(),
            'valor_recebido' : lancamento.total_pendente(),
            'modo_recebido' : lancamento.contrato.forma_pagamento,
            
            })
        
    return render_to_response('frontend/financeiro/financeiro-lancamentos-identificar-recebimento.html', locals(), context_instance=RequestContext(request),)  

class FormIdentificarRecebido(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormIdentificarRecebido, self).__init__(*args, **kwargs)
        self.fields['data_recebido'].widget.attrs['class'] = 'datepicker'
        self.fields['data_recebido'].required = True
        self.fields['valor_recebido'].required = True
        self.fields['modo_recebido'].required = True
        self.fields['conta'].required = True
    
    class Meta:
        model = Lancamento
        fields = ('valor_recebido', 'modo_recebido', 'data_recebido','conta')

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def lancamentos_a_receber(request):
    lancamentos_pendentes = Lancamento.objects.filter(data_cobranca__lt=datetime.date.today(), data_recebido=None)
    lancamentos_pendentes_total =  lancamentos_pendentes.aggregate(Sum('valor_cobrado'))
    total_com_juros_e_multa = 0
    for lancamento in lancamentos_pendentes:
        total_com_juros_e_multa += lancamento.total_pendente()
    # demais lancamentos
    # semana atual
    semana = get_weeks()
    if request.GET.get('semana'):
        semana_exibir = semana[request.GET.get('semana')]
    else:
        semana_exibir = semana[0]
    inicio_semana = semana_exibir[0]
    fim_semana = semana_exibir[-1]
    lancamentos_futuros = Lancamento.objects.filter(data_recebido=None, data_cobranca__range=(inicio_semana, fim_semana))
    soma_lancamentos_futuro = lancamentos_futuros.aggregate(Sum('valor_cobrado'))
    return render_to_response('frontend/financeiro/financeiro-lancamentos-a-receber.html', locals(), context_instance=RequestContext(request),)


class AnteciparLancamentoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AnteciparLancamentoForm, self).__init__(*args, **kwargs)
        self.fields['data_antecipado'].widget.attrs['class'] = 'datepicker'
    
    class Meta:
        model = Lancamento
        fields = 'valor_recebido', 'modo_recebido', 'data_antecipado', 'conta', 

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def lancamentos_a_receber_antecipar(request, lancamento_id):
    lancamento = get_object_or_404(Lancamento, pk=lancamento_id, antecipado=False)
    lancamento.atencipado=True
    if request.POST:
        form = AnteciparLancamentoForm(request.POST, instance=lancamento)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.situacao = "t"
            lancamento.antecipado_por = request.user
            lancamento.antecipado=True
            lancamento.save()
            messages.success(request, "Sucesso! Lançamento Antecipado!" )
            return(redirect("financeiro:lancamentos_a_receber"))
    else:
        form = AnteciparLancamentoForm(instance=lancamento)
    return render_to_response('frontend/financeiro/financeiro-lancamentos-antecipar.html', locals(), context_instance=RequestContext(request),)
    