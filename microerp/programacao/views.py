# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from models import FollowUpDeOrdemDeServico, TarefaDeProgramacao
from rh.models import Funcionario

from comercial.models import ContratoFechado

from programacao.models import OrdemDeServico

from django import forms

def possui_perfil_acesso_programacao(user, login_url="/"):
    try:
        if user.perfilacessoprogramacao and user.funcionario.periodo_trabalhado_corrente:
            return True
    except:
        return False

def possui_perfil_acesso_programacao_gerente(user, login_url="/"):
    try:
        if user.perfilacessoprogramacao and user.funcionario.periodo_trabalhado_corrente and user.perfilacessoprogramacao.gerente and user.funcionario:
            return True
    except:
        return False

#
# FORMS
#

class FormAdicionaFollowUpContrato(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormAdicionaFollowUpContrato, self).__init__(*args, **kwargs)
        self.fields['ordem_de_servico'].widget = forms.HiddenInput()
        self.fields['criado_por'].widget = forms.HiddenInput()
    
    class Meta:
        model = FollowUpDeOrdemDeServico

class FormEditarProgramacaoDeContrato(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormEditarProgramacaoDeContrato, self).__init__(*args, **kwargs)
        self.fields['previsao_inicio_execucao'].widget.attrs['class'] = 'datepicker'
        self.fields['previsao_termino_execucao'].widget.attrs['class'] = 'datepicker'
        self.fields['efetivo_inicio_execucao'].widget.attrs['class'] = 'datepicker'
        self.fields['efetivo_inicio_execucao'].widget.attrs['class'] = 'datepicker'
        self.fields['efetivo_termino_execucao'].widget.attrs['class'] = 'datepicker'

    class Meta:
        model = ContratoFechado
        fields = 'previsao_inicio_execucao', 'previsao_termino_execucao', 'efetivo_inicio_execucao', \
        'efetivo_termino_execucao', 'funcionarios_participantes', 'apoio_tecnico'


class FormAdicionarTarefa(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormAdicionarTarefa, self).__init__(*args, **kwargs)
        #self.fields['contrato'].widget = forms.HiddenInput()
        self.fields['funcionarios_participantes'].widget.attrs['class'] = 'select2'
        self.fields['data_inicio'].widget.attrs['class'] = 'datetimepicker'
        self.fields['data_fim'].widget.attrs['class'] = 'datetimepicker'
        self.fields['funcionarios_participantes'].queryset = Funcionario.objects.exclude(periodo_trabalhado_corrente=None)

    class Meta:
        model = TarefaDeProgramacao
        fields = 'titulo', 'descricao', 'funcionarios_participantes', 'data_inicio', 'data_fim', 

#
# VIEWS
#

@user_passes_test(possui_perfil_acesso_programacao, login_url='/')
def home(request):
    if request.POST:
        form_add_followup_contrato = FormAdicionaFollowUpContrato(request.POST)
        if form_add_followup_contrato.is_valid():
            fup = form_add_followup_contrato.save(commit=False)
            fup.criado_por = request.user.funcionario
            fup.save()
            fup.contrato.porcentagem_execucao = form_add_followup_contrato.cleaned_data['porcentagem_execucao']
            fup.contrato.save()
            messages.success(request, 'FollowUp de Contrato Adicionado!')
    else:
        form_add_followup_contrato = FormAdicionaFollowUpContrato(initial={'criado_por': request.user.funcionario})
    ordens_de_servico = OrdemDeServico.objects.order_by('status')
    return render_to_response('frontend/programacao/programacao-home.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_programacao, login_url='/')
def marcar_contrato_iniciado(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    contrato.status_execucao = "emandamento"
    contrato.porcentagem_execucao = 5
    contrato.data_marcado_emandamento = datetime.datetime.now()
    contrato.save()
    # cria um follow up
    contrato.followupdecontrato_set.create(criado_por=request.user.funcionario, texto="Execução Iniciada", porcentagem_execucao=contrato.porcentagem_execucao)
    return redirect(reverse("programacao:home"))

@user_passes_test(possui_perfil_acesso_programacao, login_url='/')
def marcar_contrato_aguardando_cliente(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    contrato.status_execucao = "pendente"
    contrato.aguardando_cliente = True
    contrato.data_marcado_pendente = datetime.datetime.now()
    contrato.save()
    messages.success(request, "Contrato Marcado Como Pendente")
    # cria um follow up
    contrato.followupdecontrato_set.create(criado_por=request.user.funcionario, texto="Execução Pendente: Aguardando o Cliente", porcentagem_execucao=contrato.porcentagem_execucao)
    return redirect(reverse("programacao:home"))

@user_passes_test(possui_perfil_acesso_programacao, login_url='/')
def marcar_contrato_retorno_cliente(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    contrato.status_execucao = "emandamento"
    contrato.aguardando_cliente = False
    contrato.data_marcado_retorno_cliente = datetime.datetime.now()
    contrato.save()
    messages.success(request, "Contrato Marcado Como Retornado pelo Cliente.")
    # cria um follow up
    contrato.followupdecontrato_set.create(criado_por=request.user.funcionario, texto="Execução Retornada: Retorno do Cliente", porcentagem_execucao=contrato.porcentagem_execucao)
    return redirect(reverse("programacao:home"))

@user_passes_test(possui_perfil_acesso_programacao, login_url='/')
def editar_programacao_contrato(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    if request.POST:
        form_editar_contrato = FormEditarProgramacaoDeContrato(request.POST, instance=contrato)
        if form_editar_contrato.is_valid():
            contrato = form_editar_contrato.save()
            messages.success(request, 'Programação de Contrato Alterada')
            return redirect(reverse("programacao:home"))
    else:
        form_editar_contrato = FormEditarProgramacaoDeContrato(instance=contrato)
    return render_to_response('frontend/programacao/programacao-editar-programacao-contrato.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_programacao, login_url='/')
def editar_programacao_contrato_adicionar_tarefa(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    if request.POST:
        form = FormAdicionarTarefa(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.criado_por = request.user.funcionario
            tarefa.save()
            if request.POST.get('acao-post-save') == 'outro':
                return redirect(reverse("programacao:editar_programacao_contrato_adicionar_tarefa", args=[contrato.id]))
            else:
                return redirect(reverse("programacao:editar_programacao_contrato", args=[contrato.id]))
            
    else:
        form = FormAdicionarTarefa(initial={'contrato': contrato.id})
    
    
    return render_to_response('frontend/programacao/programacao-editar-programacao-contrato-adicionar-tarefa.html', locals(), context_instance=RequestContext(request),)


    
