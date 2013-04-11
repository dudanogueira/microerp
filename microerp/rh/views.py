# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError

from django.db.models import Q

from rh.models import Departamento, Funcionario, Demissao
from rh.models import FolhaDePonto, RotinaExameMedico, SolicitacaoDeLicenca
from django import forms

#
# FORMULARIOS
#

class DemitirFuncionarioForm(forms.Form):
    exame_demissional = forms.DateTimeField(
        initial=datetime.datetime.now(),
        help_text="Formato: dd/mm/yyyy HH:MM"
    )

class AgendarExameMedicoForm(forms.ModelForm):
    class Meta:
        model = RotinaExameMedico
        fields = ('data',)

class AdicionarFolhaDePontoForm(forms.ModelForm):
    class Meta:
        model = FolhaDePonto
        fields = ('arquivo', 'data_referencia', 'horas_trabalhadas')


class AdicionarArquivoRotinaExameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdicionarArquivoRotinaExameForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    class Meta:
        model = RotinaExameMedico
        fields = ('arquivo',)


class AdicionarSolicitacaoLicencaForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoDeLicenca
        fields = ('tipo', 'motivo', 'inicio', 'fim')


#
# VIEWS
#

def home(request):
    demissoes_andamento = Demissao.objects.filter(status="andamento")
    exames_futuros = RotinaExameMedico.objects.filter(data__gt=datetime.date.today()) | RotinaExameMedico.objects.filter(realizado=False)
    return render_to_response('frontend/rh/rh-home.html', locals(), context_instance=RequestContext(request),)

def funcionarios(request):
    departamentos = Departamento.objects.exclude(cargo__funcionario_cargo_atual_set__periodo_trabalhado_corrente=None)
    funcionarios_inativos = Funcionario.objects.filter(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/rh/rh-funcionarios.html', locals(), context_instance=RequestContext(request),)

def funcionarios_relatorios_listar_ativos(request):
    funcionarios_ativos = funcionarios_inativos = Funcionario.objects.exclude(periodo_trabalhado_corrente=None).order_by('-periodo_trabalhado_corrente__inicio')
    return render_to_response('frontend/rh/rh-funcionarios-listar-ativos.html', locals(), context_instance=RequestContext(request),)

def ver_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    if request.POST:
        # folha de ponto
        adicionar_folhaponto_form = AdicionarFolhaDePontoForm(request.POST, request.FILES)
        if adicionar_folhaponto_form.is_valid():
            folha = adicionar_folhaponto_form.save(commit=False)
            folha.funcionario = funcionario
            folha.periodo_trabalhado = funcionario.periodo_trabalhado_corrente
            # gerente, já vai autorizado
            if request.user.perfilacessorh.gerente:
                folha.autorizado = True
                folha.funcionario_autorizador = request.user.funcionario
            folha.save()            
            folha.funcionario_autorizador = request.user.funcionario
            folha.save()
            messages.success(request, u'Folha de Ponto Adicionada')
        else:
            messages.error(request, u'Formulário para Adicionar Ponto Inválido')

    else:    
        adicionar_folhaponto_form = AdicionarFolhaDePontoForm()
        adicionar_solicitacaolicenca_form = AdicionarSolicitacaoLicencaForm()
        
    return render_to_response('frontend/rh/rh-funcionarios-ver.html', locals(), context_instance=RequestContext(request),)

def solicitacao_licencas(request,):
    solicitacoes_abertas = SolicitacaoDeLicenca.objects.filter(status="aberta")
    solicitacoes_autorizada = SolicitacaoDeLicenca.objects.filter(status="autorizada")
    return render_to_response('frontend/rh/rh-solicitacao-licencas.html', locals(), context_instance=RequestContext(request),)

def solicitacao_licenca_add(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    if request.POST:
        form = AdicionarSolicitacaoLicencaForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.funcionario = funcionario
            solicitacao.save()
            messages.success(request, u'Solicitação Adicionada')
        else:
            errors = ["%s: %s" % (item[0], str(item[1])) for item in form.errors.items()]
            messages.error(request, "%s" % ' '.join(errors))
    return redirect(reverse('rh:ver_funcionario', args=[funcionario.id,]))

def solicitacao_licencas_autorizar(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoDeLicenca, pk=solicitacao_id)
    solicitacao.status = "autorizada"
    solicitacao.data_autorizado = datetime.date.today()
    solicitacao.processado_por = request.user.funcionario
    solicitacao.save()
    return redirect(reverse('rh:solicitacao_licencas'))

def exames_medicos(request):
    exames_data_pendente = RotinaExameMedico.objects.filter(data=None)
    exames_remarcacao = RotinaExameMedico.objects.filter(data__lt=datetime.date.today(), realizado=False)
    exames_agendados = RotinaExameMedico.objects.filter(data__gt=datetime.date.today(), realizado=False)
    exames_realizados = RotinaExameMedico.objects.filter(realizado=True)
    return render_to_response('frontend/rh/rh-exames-medicos.html', locals(), context_instance=RequestContext(request),)

def exames_medicos_ver(request, exame_id):
    exame = get_object_or_404(RotinaExameMedico, id=exame_id)
    if 'agendar' in request.POST:
        form_agendar = AgendarExameMedicoForm(request.POST, instance=exame)
        if form_agendar.is_valid():
            exame = form_agendar.save()
            messages.info(request, u"Agendado para %s" % exame.data.strftime("%d/%m/%Y %H:%M"))
    else:
        form_agendar = AgendarExameMedicoForm(instance=exame)
    exame_arquivo_form = AdicionarArquivoRotinaExameForm(instance=exame)
    
    return render_to_response('frontend/rh/rh-exames-medicos-ver.html', locals(), context_instance=RequestContext(request),)


def exames_medicos_exame_realizado_hoje(request, exame_id):
    '''marca exame como Realizado Hoje'''
    exame = get_object_or_404(RotinaExameMedico, pk=exame_id)
    if request.POST:
        form = AdicionarArquivoRotinaExameForm(request.POST, request.FILES, instance=exame)
        if form.is_valid():            
            try:
                exame_alterado = form.save(commit=False)
                exame_alterado.realizado = True
                exame_alterado.save()
                messages.info(request, "Salvo")
            except ValidationError, e:
                messages.error(request, "%" '; '.join(e.messages))        
            except:
                raise
        else:
            errors = ["%s: %s" % (item[0], str(item[1])) for item in form.errors.items()]
            messages.error(request, "%" '; '.join(errors))

    return redirect(reverse('rh:exames_medicos_ver', args=[exame.id,]))


def exames_medicos_exame_realizado_hoje_old(request, exame_id):
    '''marca exame como Realizado Hoje'''
    if request.POST:
        form = AdicionarArquivoRotinaExameForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                exame = form.save()
                if not exame.data:
                    exame.data = datetime.datetime.now()
                exame.realizado = True
                exame.clean()
                exame.save()
                messages.success(request, u"Exame marcado como Realizado!")
                # Se é exame admissional, ou atualização
                # marcar para daqui a 1 ano, do tipo atualização
                if exame.tipo == "a" or exame.tipo == "u":
                    data_novo_exame = datetime.date.today() + relativedelta( months = +12 )
                    novo_exame = exame.funcionario.rotinaexamemedico_set.create(
                        tipo="u",
                        data=data_novo_exame,
                        periodo_trabalhado=exame.periodo_trabalhado,
                    )
                    messages.info(request, u"Um Novo Exame do Tipo Atualização foi Criado: #ID%s" % novo_exame.id)
                    for exame_padrao in exame.funcionario.cargo_atual.exame_medico_padrao.all():
                        novo_exame.exames.add(exame_padrao)
                    novo_exame.save()
            else:
                messages.error(request, "ERROR")        
        except ValidationError, e:
            messages.error(request, "%" '; '.join(e.messages))        

        return redirect(reverse('rh:exames_medicos_ver', args=[exame.id,]))

def processos_demissao(request):
    return render_to_response('frontend/rh/rh-processos-demissao.html', locals(), context_instance=RequestContext(request),)

def demitir_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    # Se não possuir periodo corrente, não pode ser demitido
    if not funcionario.periodo_trabalhado_corrente:
        messages.warning(request, u"Impossível demitir este Funcionário. Ele não possui Período Trabalhado Corrente")
        return redirect(reverse('rh:ver_funcionario', args=[funcionario.id,]))
    if request.POST:
        form = DemitirFuncionarioForm(request.POST)
        if form.is_valid():
            data_exame_demissional = form.cleaned_data['exame_demissional']
            periodo_trabalhado_finalizado = funcionario.periodo_trabalhado_corrente
            # encerra Periodo Trabalhado Corrente e desvincula ao funcionario
            funcionario.periodo_trabalhado_corrente.fim = datetime.date.today()
            funcionario.periodo_trabalhado_corrente.save()
            funcionario.periodo_trabalhado_corrente = None
            funcionario.save()
            messages.info(request, u'Período Trabalhado Desvinculado')
            # agenda rotina de médico demissional com padrões do cargo
            exame = funcionario.rotinaexamemedico_set.create(
                data=data_exame_demissional,
                tipo='d',
                periodo_trabalhado=periodo_trabalhado_finalizado,
            )
            for exame_padrao in funcionario.cargo_atual.exame_medico_padrao.all():
                exame.exames.add(exame_padrao)
            exame.save()
            messages.info(request, u'Exame Médico Demissional criado em: %s, #ID%s' % (exame.data, exame.id))
            # Cria Registro de Demissão
            demissao = funcionario.demissao_set.create(
                data=datetime.date.today(),
                periodo_trabalhado_finalizado=periodo_trabalhado_finalizado,
                demissor=request.user.funcionario,
            )
            messages.info(request, u'Entrada de Demissão Criada: ID#%s' % demissao.id)
            # sucesso no processo
            messages.success(request, u'Processo de Demissão Iniciado com Sucesso!')
            # redireciona pra tela do usuário
            return redirect(reverse('rh:ver_funcionario', args=[funcionario.id,]))
        else:
            messages.error(request, u'Erro de Validação do Formulário % s' % form.errors)
            
    else:
        form = DemitirFuncionarioForm()
    return render_to_response('frontend/rh/rh-funcionarios-demitir.html', locals(), context_instance=RequestContext(request),)

# controle_de_ferias
def controle_de_ferias(request):
    funcionarios = Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/rh/rh-controle-de-ferias.html', locals(), context_instance=RequestContext(request),)

# controle_de_banco_de_horas
def controle_de_banco_de_horas(request):
    funcionarios = Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/rh/rh-controle-de-banco-de-horas.html', locals(), context_instance=RequestContext(request),)