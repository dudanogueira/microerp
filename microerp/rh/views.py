# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test

from django.db.models import Q

from rh.models import Departamento, Funcionario, Demissao
from rh.models import FolhaDePonto, RotinaExameMedico, SolicitacaoDeLicenca
from rh.models import EntradaFolhaDePonto, Competencia
from rh.utils import get_weeks

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
        fields = ('data_referencia',)

class AdicionarEntradaFolhaDePontoForm(forms.ModelForm):
    class Meta:
        model = EntradaFolhaDePonto
        fields = ('inicio', 'fim', 'total')



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
# DECORATORS
#

def possui_perfil_acesso_rh(user, login_url="/"):
    try:
        if user.perfilacessorh and user.funcionario.ativo():
            return True
    except:
        return False

#
# VIEWS
#

@user_passes_test(possui_perfil_acesso_rh)
def home(request):
    # demissoes
    demissoes_andamento = Demissao.objects.filter(status="andamento")
    # exames por vir
    exames_futuros = RotinaExameMedico.objects.filter(data__gt=datetime.date.today()) | RotinaExameMedico.objects.filter(realizado=False)
    # aniversarios
    this_week = get_weeks()[0]
    days = [day.day for day in this_week]
    today = datetime.date.today()
    aniversarios_mes = Funcionario.objects.filter(nascimento__month=today.month).exclude(periodo_trabalhado_corrente=None).extra(
        select={'birthmonth': 'MONTH(nascimento)'}, order_by=['birthmonth']
        )
    aniversarios_hoje = Funcionario.objects.filter(nascimento__month=today.month, nascimento__day=today.day)
    return render_to_response('frontend/rh/rh-home.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_rh)
def funcionarios(request):
    departamentos = Departamento.objects.all()
    funcionarios_inativos = Funcionario.objects.filter(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/rh/rh-funcionarios.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_rh)
def funcionarios_relatorios_listar_ativos(request):
    relatorio = True
    funcionarios_ativos = Funcionario.objects.exclude(periodo_trabalhado_corrente=None).order_by('periodo_trabalhado_corrente__inicio')
    return render_to_response('frontend/rh/rh-funcionarios-listar-ativos.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_rh)
def funcionarios_relatorios_listar_ativos_aniversarios(request):
    relatorio = True
    meses = range(1,13)
    lista = []
    for mes in meses:
        funcionarios_ativos = Funcionario.objects.filter(nascimento__month=mes).extra(
        #select = {'custom_dt': 'date(nascimento)'}).order_by('-custom_dt'
        select={'birthmonth': 'MONTH(nascimento)'}, order_by=['birthmonth']
        )
        lista.append((datetime.date(datetime.date.today().year, mes, 1), funcionarios_ativos,))
    return render_to_response('frontend/rh/rh-funcionarios-listar-aniversarios.html', locals(), context_instance=RequestContext(request),)
        
@user_passes_test(possui_perfil_acesso_rh)
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

@user_passes_test(possui_perfil_acesso_rh)
def solicitacao_licencas(request,):
    solicitacoes_abertas = SolicitacaoDeLicenca.objects.filter(status="aberta")
    solicitacoes_autorizada = SolicitacaoDeLicenca.objects.filter(status="autorizada")
    return render_to_response('frontend/rh/rh-solicitacao-licencas.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_rh)
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

@user_passes_test(possui_perfil_acesso_rh)
def solicitacao_licencas_autorizar(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoDeLicenca, pk=solicitacao_id)
    solicitacao.status = "autorizada"
    solicitacao.data_autorizado = datetime.date.today()
    solicitacao.processado_por = request.user.funcionario
    solicitacao.save()
    return redirect(reverse('rh:solicitacao_licencas'))

@user_passes_test(possui_perfil_acesso_rh)
def exames_medicos(request):
    exames_data_pendente = RotinaExameMedico.objects.filter(data=None)
    exames_remarcacao = RotinaExameMedico.objects.filter(data__lt=datetime.date.today(), realizado=False)
    exames_agendados = RotinaExameMedico.objects.filter(data__gt=datetime.date.today(), realizado=False)
    exames_realizados = RotinaExameMedico.objects.filter(realizado=True)
    return render_to_response('frontend/rh/rh-exames-medicos.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_rh)
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


@user_passes_test(possui_perfil_acesso_rh)
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
                messages.success(request, u"Exame marcado como Realizado!")
                # Se é exame admissional, ou atualização
                # marcar para daqui a X dias o exame de atualização
                if exame_alterado.tipo == "a" or exame_alterado.tipo == "u":
                    dias_proximo_exame = exame_alterado.funcionario.cargo_atual.dias_renovacao_exames
                    data_novo_exame = datetime.date.today() + relativedelta( days = dias_proximo_exame )
                    novo_exame = exame.funcionario.rotinaexamemedico_set.create(
                        tipo="u",
                        data=data_novo_exame,
                        periodo_trabalhado=exame.periodo_trabalhado,
                    )
                    messages.info(request, u"Um Novo Exame do Tipo Atualização foi Criado: #ID%s" % novo_exame.id)
                    # adiciona os exames padrao para o cargo do funcionario
                    for exame_padrao in exame.funcionario.cargo_atual.exame_medico_padrao.all():
                        novo_exame.exames.add(exame_padrao)
                    novo_exame.save()

            except ValidationError, e:
                messages.error(request, "%" '; '.join(e.messages))        
            except:
                raise
        else:
            errors = ["%s: %s" % (item[0], str(item[1])) for item in form.errors.items()]
            messages.error(request, "%" '; '.join(errors))

    return redirect(reverse('rh:exames_medicos_ver', args=[exame.id,]))

@user_passes_test(possui_perfil_acesso_rh)
def processos_demissao(request):
    processos_abertos = Demissao.objects.filter(status="andamento")
    processos_fechados = Demissao.objects.filter(status="finalizado")
    return render_to_response('frontend/rh/rh-processos-demissao.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_rh)
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
                demissor=request.user,
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
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_ferias(request):
    funcionarios = Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/rh/rh-controle-de-ferias.html', locals(), context_instance=RequestContext(request),)

# controle_de_banco_de_horas
@user_passes_test(possui_perfil_acesso_rh)
def controle_de_banco_de_horas(request):
    funcionarios = Funcionario.objects.all().exclude(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/rh/rh-controle-de-banco-de-horas.html', locals(), context_instance=RequestContext(request),)

# controle_banco_de_horas_do_funcionario
@user_passes_test(possui_perfil_acesso_rh)
def controle_banco_de_horas_do_funcionario(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, id=funcionario_id)
    folhas_abertas = funcionario.folhadeponto_set.filter(encerrado=False)
    folhas_fechadas = funcionario.folhadeponto_set.filter(encerrado=True)
    # processo adicionar entrada folha
    if request.POST:
        form_add_entrada_folha_ponto = AdicionarEntradaFolhaDePontoForm(request.POST)
        if form_add_entrada_folha_ponto.is_valid():
            entrada = form_add_entrada_folha_ponto.save(commit=False)
            folha_id = int(form_add_entrada_folha_ponto.data['folha'])
            folha = get_object_or_404(FolhaDePonto, id=folha_id)
            entrada.folha = folha
            entrada.adicionado_por = request.user
            entrada.save()
            messages.success(request, u'Sucesso: Lançamento de %s horas realizado!' % entrada.total )
        else:
            messages.error(request, u'Formulário Não Validado')
            
    else:
        form_add_entrada_folha_ponto = AdicionarEntradaFolhaDePontoForm()
    return render_to_response('frontend/rh/rh-banco-de-horas-funcionario.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_rh)
def controle_banco_de_horas_do_funcionario_gerenciar(request, funcionario_id, folha_id):
    folha = get_object_or_404(FolhaDePonto, funcionario__id=funcionario_id, id=folha_id)
    folha.encerrado = True
    folha.save()
    return redirect(reverse('rh:controle_banco_de_horas_do_funcionario', args=[folha.funcionario.id,]))

@user_passes_test(possui_perfil_acesso_rh)
def matriz_de_competencias(request):
    competencias = Competencia.objects.all()
    return render_to_response('frontend/rh/rh-matriz-de-competencias.html', locals(), context_instance=RequestContext(request),)