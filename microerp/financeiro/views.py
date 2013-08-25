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

from django.conf import settings

from rh.utils import get_weeks

from comercial.models import ContratoFechado
from financeiro.models import Lancamento
from financeiro.models import ProcessoAntecipacao
from cadastro.models import Cliente

import datetime

def possui_perfil_acesso_financeiro(user, login_url="/"):
    try:
        if user.perfilacessofinanceiro and user.funcionario.ativo():
            return True
    except:
        return False

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def home(request):
    ## widget do contratos
    contratos_tipo_fechado = ContratoFechado.objects.filter(status="emaberto", tipo="fechado", receber_apos_conclusao=False)
    contratos_tipo_aberto = ContratoFechado.objects.filter(status="emaberto", tipo="aberto")
    contratos_tipo_mensal = ContratoFechado.objects.filter(status="emaberto", tipo="mensal")
    contratos_receber_apos_conclusao = ContratoFechado.objects.filter(status="emaberto", tipo="fechado", receber_apos_conclusao=True)
    ## totais de contratos
    contratos_tipo_fechado_total =  contratos_tipo_fechado.aggregate(Sum('valor'))['valor__sum'] or 0
    contratos_tipo_aberto_total =  contratos_tipo_aberto.aggregate(Sum('valor'))['valor__sum'] or 0
    contratos_tipo_mensal_total = contratos_tipo_mensal.aggregate(Sum('valor'))['valor__sum'] or 0
    contratos_receber_apos_conclusao_total = contratos_receber_apos_conclusao.aggregate(Sum('valor'))['valor__sum'] or 0
    # totais
    total_contratos_emaberto_count = ContratoFechado.objects.filter(status="emaberto").count()
    
    ## widget de lancamentos
    # pendentes
    lancamentos_pendentes = Lancamento.objects.filter(data_cobranca__lt=datetime.date.today(), data_recebido=None)
    lancamentos_pendentes_total_valor =  lancamentos_pendentes.aggregate(Sum('valor_cobrado'))['valor_cobrado__sum'] or 0
    # atecipados
    lancamentos_abertos_atencipados = Lancamento.objects.filter(antecipado=True, data_recebido=None)
    lancamentos_abertos_atencipados_total_valor = lancamentos_abertos_atencipados.aggregate(Sum('valor_cobrado'))['valor_cobrado__sum'] or 0
    # a receber
    lancamentos_a_receber = Lancamento.objects.filter(antecipado=False, data_recebido=None, data_cobranca__gte=datetime.date.today())
    lancamentos_a_receber_total_valor = lancamentos_a_receber.aggregate(Sum('valor_cobrado'))['valor_cobrado__sum'] or 0
    # total
    total_lancamentos_a_receber = lancamentos_pendentes.count() + lancamentos_abertos_atencipados.count() + lancamentos_a_receber.count()
    total_valor_lancamentos_a_receber = lancamentos_pendentes_total_valor + lancamentos_a_receber_total_valor
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
        self.fields['valor_mao_de_obra'].required = True
        self.fields['valor_materiais'].required = True
        if contrato:
            self.fields['contrato'].widget = forms.HiddenInput()
            self.fields['peso'].widget = forms.HiddenInput()
            self.fields['contrato'].initial = contrato.id
            self.fields['data_cobranca'].widget.attrs['class'] = 'datepicker'
        if proximo_peso:
            self.fields['peso'].initial = proximo_peso
        
    class Meta:
        model = Lancamento
        fields = 'contrato', 'peso', 'data_cobranca', 'modo_recebido', 'valor_mao_de_obra', 'valor_materiais', 'notas_fiscais'

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

# Lancamentos

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def lancamentos(request):
    return render_to_response('frontend/financeiro/financeiro-lancamentos.html', locals(), context_instance=RequestContext(request),)


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

            return(redirect("financeiro:lancamentos"))
    else:
        
        # se lancamento ja não possuir o campo preenchido, sugerir com
        # o padrao do contrato
        if lancamento.modo_recebido:
            modo_receber_sugerido = lancamento.modo_recebido
        else:
            modo_receber_sugerido = lancamento.contrato.forma_pagamento
        
        form = FormIdentificarRecebido(instance=lancamento, initial = {
            'data_recebido' : datetime.date.today(),
            'valor_recebido' : lancamento.total_pendente(),
            'modo_recebido' : modo_receber_sugerido,
            
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
def ajax_lancamento_informacao_pagamento(request, lancamento_id):
    lancamento = get_object_or_404(Lancamento, pk=lancamento_id)
    if request.POST:
        infos = request.POST.get('informacoes-pagamento', None)
        lancamento.informacoes_pagamento = infos
        lancamento.save()
        messages.success(request, "Sucesso! Informação sobre pagamento aleterado.")
        return redirect(reverse("financeiro:lancamentos"))
    else:
        return render_to_response('frontend/financeiro/financeiro-include-informacoes-pagamento-lancamento.html', locals(), context_instance=RequestContext(request),)
    

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def ajax_lancamento_comentarios(request, lancamento_id):
    lancamento = get_object_or_404(Lancamento, pk=lancamento_id)
    return render_to_response('frontend/financeiro/financeiro-include-comentarios-modal.html', locals(), context_instance=RequestContext(request),)

class SelecionarClienteForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())
    cliente.widget.attrs['class'] = 'select2'
    

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def ajax_lancamento_buscar(request):
    inicio_busca = datetime.date.today()
    fim_busca = datetime.date.today() + datetime.timedelta(days=30)
    if request.POST:
        buscado = True
        if request.POST.get('numero-contrato', None):
            try:
                id_contrato = int(request.POST.get('numero-contrato'))
                lancamentos_exibir = Lancamento.objects.filter(contrato__pk=id_contrato)
            except:
                id_contrato = 0
        if request.POST.get('numero-lancamento', None):
            try:
                id_lancamento = int(request.POST.get('numero-lancamento'))
                lancamentos_exibir = Lancamento.objects.filter(pk=id_lancamento)
            except:
                id_lancamento = 0
        if request.POST.get('data-inicio', None) and request.POST.get('data-fim', None):
            try:
                data_inicio = datetime.datetime.strptime(request.POST.get('data-inicio', None), "%d/%m/%Y")
                data_fim = datetime.datetime.strptime(request.POST.get('data-fim', None), "%d/%m/%Y")
                lancamentos_exibir = Lancamento.objects.filter(data_cobranca__range=(data_inicio, data_fim))
            except:
                raise
                
                
        
    return render_to_response('frontend/financeiro/financeiro-include-lancamentos-buscar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def ajax_lancamentos_receber(request, busca_tipo, offset):
    try:
        offset = int(offset)
    except:
        offset = 0
    
    if busca_tipo == "semana":
        semana = get_weeks()
        semana_exibir = semana[offset]
        inicio_semana = semana_exibir[0]
        fim_semana = semana_exibir[-1]
        lancamentos_exibir = Lancamento.objects.filter(data_recebido=None, data_cobranca__range=(inicio_semana, fim_semana))
    elif busca_tipo == "dia":
        hoje = datetime.date.today()
        dia_buscado =  hoje + datetime.timedelta(days=offset)
        lancamentos_exibir = Lancamento.objects.filter(data_recebido=None, data_cobranca=dia_buscado)
    elif busca_tipo == "pendentes":
        pendentes = True
        lancamentos_exibir = Lancamento.objects.filter(data_cobranca__lt=datetime.date.today(), data_recebido=None)
    soma_lancamentos_futuro = lancamentos_exibir.aggregate(Sum('valor_cobrado'))['valor_cobrado__sum'] or 0
    soma_lancamentos_antecipados = lancamentos_exibir.filter(antecipado=True).aggregate(Sum('valor_recebido'))['valor_recebido__sum'] or 0
    
    return render_to_response('frontend/financeiro/financeiro-include-linha-lancamento-futuro.html', locals(), context_instance=RequestContext(request),)



@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def lancamentos_a_receber(request):
    
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
    soma_lancamentos_antecipados = lancamentos_futuros.filter(antecipado=True).aggregate(Sum('valor_recebido'))
    return render_to_response('frontend/financeiro/financeiro-lancamentos-a-receber.html', locals(), context_instance=RequestContext(request),)


class AnteciparLancamentoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AnteciparLancamentoForm, self).__init__(*args, **kwargs)
        self.fields['data_antecipado'].widget.attrs['class'] = 'datepicker'
    
    class Meta:
        model = Lancamento
        fields = 'valor_recebido', 'modo_recebido', 'data_antecipado', 'conta', 

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def lancamentos_a_receber_antecipar(request):
    antecipaveis = getattr(settings, 'TIPOS_LANCAMENTOS_ANTECIPAVEIS', ('boleto', 'cheque', 'credito'))
    lancamentos_antecipaveis = Lancamento.objects.filter(modo_recebido__in=antecipaveis, data_cobranca__gte=datetime.date.today()).exclude(antecipado=True, situacao="t")
    if request.POST.get('confirmar'):
        # confirmado, criar a antecipacao e vincular aos pagamentos
        confirmado = True
        lancamentos_id = request.POST.getlist('lancamento')
        lancamentos_a_antecipar = lancamentos_antecipaveis.filter(id__in=lancamentos_id)
        # calcula o valor total e registra o processo de antecipacao
        percentual = request.POST.get('percentual', 0)
        valor_total = lancamentos_a_antecipar.aggregate(total=Sum('valor_cobrado'))['total'] or 0
        valor_percentual = float(valor_total) * float(percentual) / 100
        valor_final = float(valor_total) - float(valor_percentual)
        # cria o processo de antecipacao
        processo = ProcessoAntecipacao.objects.create(
            valor_inicial=valor_total,
            percentual_abatido=percentual,
            valor_abatido=valor_final,
            antecipado_por=request.user,
        )
        processo.lancamentos.add(*lancamentos_a_antecipar.all())
        # altera o lancamento
        # marca todos os lancamentos como antecipados, e da as providencias
        for lancamento in lancamentos_a_antecipar.all():
            valor_percentual = float(lancamento.valor_cobrado) * float(percentual) / 100
            lancamento.valor_recebido = float(lancamento.valor_cobrado) - float(valor_percentual)
            lancamento.data_antecipado = datetime.date.today()
            lancamento.antecipado_por = request.user
            lancamento.situacao = "t"
            lancamento.antecipado = True
            lancamento.save()
            messages.info(request, u"Lançamento #%s marcado como antecipado: R$ %s" % (lancamento.id, lancamento.valor_recebido))
        messages.success(request, u"Sucesso! Antecipação Realizada!")
        redirect(reverse("financeiro:lancamentos_a_receber_antecipar"))
        
        

        
    else:
        if request.POST:
            if request.POST.get('calcular-antecipacao'):
                calcular = True
                lancamentos_id = request.POST.getlist('lancamentos-a-antecipar', None)
                try:
                    percentual = request.POST.get('percentual', 0)
                    if lancamentos_id:
                        lancamentos_a_antecipar = lancamentos_antecipaveis.filter(id__in=lancamentos_id)
                        valor_total = lancamentos_a_antecipar.aggregate(total=Sum('valor_cobrado'))
                        valor_percentual = float(valor_total['total']) * float(percentual) / 100
                        resultado_final = float(valor_total['total']) - float(valor_percentual)
                    else:
                        calcular = False
                        messages.error(request, u"Erro! Deve ser marcado pelo menos um Lançamento")
                    
                except:
                    messages.error(request, u"Erro! Percentual deve ser um número inteiro!")
                    return redirect(reverse("financeiro:lancamentos_a_receber_antecipar"))
                    
        else:
            if request.GET.get('lancamento'):
                try:
                    lancamento_sugerido = int(request.GET.get('lancamento'))
                except: 
                    lancamento_sugerido = 0
            # exibe os processos de antecipacao
            processos = ProcessoAntecipacao.objects.all()
                
    return render_to_response('frontend/financeiro/financeiro-lancamentos-antecipar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def lancamentos_a_receber_comentar(request, lancamento_id):
    lancamento = get_object_or_404(Lancamento, pk=lancamento_id)
    if request.POST:
        comentario = request.POST.get('comentario', None)
        if comentario:
            lancamento.observacaolancamento_set.create(texto=comentario, criado_por=request.user)
            messages.success(request, u"Sucesso! Comentário Registrado com Sucesso!")
        else:
            messages.error(request, u"Erro! Campo comentário não pode ser vazio.")
    else:
        messages.error(request, u"Erro! Não dever ser acessado diretamente")
    return(redirect("financeiro:lancamentos"))

