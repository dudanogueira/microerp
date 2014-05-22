# -*- coding: utf-8 -*-
import datetime, locale
import operator
from collections import OrderedDict
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum

from django.core.mail import EmailMessage

from django.contrib.sites.models import Site

from django.core.exceptions import ValidationError
from django_localflavor_br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField

from django import forms

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.db.models import Count

# APPS MODELS
from rh.models import Departamento, Funcionario
from cadastro.models import Cliente, PreCliente
from solicitacao.models import Solicitacao
from comercial.models import PropostaComercial, FollowUpDePropostaComercial, RequisicaoDeProposta, ContratoFechado
from comercial.models import PerfilAcessoComercial, FechamentoDeComissao
from comercial.models import LinhaRecursoMaterial, Orcamento, GrupoIndicadorDeProdutoProposto
from financeiro.models import LancamentoFinanceiroReceber
from estoque.models import Produto

from django.conf import settings

from rh import utils

from django.http import HttpResponse

# FORM DE OUTROS APPS
from cadastro.views import AdicionarEnderecoClienteForm


from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.units import inch, mm 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.auth.models import User
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT

#
# FORMULARIOS
#

class ConfigurarImpressaoContrato(forms.Form):
    
    def __init__(self, *args, **kwargs):
        contrato = kwargs.pop('contrato')
        super(ConfigurarImpressaoContrato, self).__init__(*args, **kwargs)
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        initial1 = contrato.responsavel_comissionado or None
        self.fields['testemunha1'] = forms.ModelChoiceField(queryset=Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis), initial=initial1, label="Testemunha 1")
        self.fields['testemunha2'] = forms.ModelChoiceField(queryset=Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis), required=False, label="Testemunha 2")
        self.fields['imprime_logo'] = forms.BooleanField()
        self.fields['imprime_logo'].initial = True


class PreClienteAdicionarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        sugestao = kwargs.pop('sugestao')
        perfil = kwargs.pop('perfil')
        super(PreClienteAdicionarForm, self).__init__(*args, **kwargs)
        self.fields['designado'].empty_label = "Nenhum"
        if sugestao:
            self.fields['nome'].initial = sugestao
        if not perfil.gerente:
            self.fields['designado'].widget = forms.HiddenInput()
            self.fields['designado'].initial = perfil.user.funcionario
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        self.fields['designado'].queryset = Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis)
        self.fields['designado'].widget.attrs['class'] = 'select2'
        
    class Meta:
        model = PreCliente
        fields = 'nome', 'contato', 'dados', 'designado'

class AdicionarPropostaForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AdicionarPropostaForm, self).__init__(*args, **kwargs)
        self.fields['valor_proposto'].localize = True
        self.fields['valor_proposto'].widget.is_localized = True
    
    
    class Meta:
        model = PropostaComercial
        fields = 'probabilidade', 'valor_proposto', 'tipo'
        localized_fields = 'valor_proposto',

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
        return telefone_fixo
    
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
            # checa se já existe CPF no banco de dados
            cliente = Cliente.objects.filter(cpf=cpf)
            if cliente:
                raise ValidationError(u"Já existe um cliente com este CPF!")
        return cpf
            
        
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
            
            # checa se já existe CPF no banco de dados
            cliente = Cliente.objects.filter(cnpj=cnpj)
            if cliente:
                raise ValidationError(u"Já existe um cliente com este CNPJ!")
            
        return cnpj
    
    def __init__(self, *args, **kwargs):
        precliente = kwargs.pop('precliente')
        gerente = kwargs.pop('gerente', False)
        super(AdicionarCliente, self).__init__(*args, **kwargs)
        self.fields['tipo'].required = True
        self.fields['nascimento'].widget.attrs['class'] = 'datepicker'
        if precliente:
            self.fields['nome'].initial = precliente.nome
            self.fields['observacao'].initial = precliente.dados
    
    class Meta:
        model = Cliente
        fields = 'nome', 'tipo', 'fantasia', 'cnpj', 'inscricao_estadual', \
        'cpf', 'rg', 'nascimento', 'ramo', 'observacao', 'origem',\
        'contato', 'email', 'telefone_fixo', 'telefone_celular', 'fax',

class FormAdicionarFollowUp(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormAdicionarFollowUp, self).__init__(*args, **kwargs)
        self.fields['proposta'].widget = forms.HiddenInput()
        self.fields['texto'].required = True
        self.fields['probabilidade'].required = True
        self.fields['data_expiracao'].required = False
        self.fields['data_expiracao'].widget.attrs['class'] = 'datepicker'

    class Meta:
        model = FollowUpDePropostaComercial
        fields = 'proposta', 'texto', 'probabilidade', 'reagenda_data_expiracao', 'data_expiracao'
    
    def clean_data_expiracao(self):
            data = self.cleaned_data['data_expiracao']
            reagenda_data_expiracao = self.cleaned_data['reagenda_data_expiracao']
            if reagenda_data_expiracao and not data:
                    raise forms.ValidationError("É preciso informar uma data!")
            return data

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
    #ultimos followups
    if not request.user.perfilacessocomercial.gerente:
        ultimos_followups = FollowUpDePropostaComercial.objects.filter(
            Q(proposta__designado=request.user.funcionario) | Q(proposta__cliente__designado=request.user.funcionario) | Q(proposta__precliente__designado=request.user.funcionario) | \
            Q(proposta__designado=None) | (Q(proposta__cliente__designado=None) & Q(proposta__precliente__designado=None))
        )[0:10]
    else:
        ultimos_followups = FollowUpDePropostaComercial.objects.all()[0:10]
        
    preclientes_sem_proposta = PreCliente.objects.filter(propostacomercial=None, cliente_convertido=None, designado=request.user.funcionario, sem_interesse=False).count()
    requisicoes_propostas = RequisicaoDeProposta.objects.filter(atendido=False, cliente__designado=request.user.funcionario).count()
    return render_to_response('frontend/comercial/comercial-home.html', locals(), context_instance=RequestContext(request),)


class DefinePreClienteSemInteresseForm(forms.ModelForm):
    
    def clean(self):
        cleaned_data=super(DefinePreClienteSemInteresseForm, self).clean()
        opcao = cleaned_data.get('sem_interesse_opcao')
        motivo = cleaned_data.get('sem_interesse_motivo')
        if not opcao and not motivo:
            raise ValidationError('Pelo menos uma opção deve ser preenchida')
        return cleaned_data
    class Meta:
        model = PreCliente
        fields =  'sem_interesse_opcao', 'sem_interesse_motivo'

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def clientes_precliente_sem_interesse(request, precliente_id):
    precliente = get_object_or_404(PreCliente, pk=precliente_id)
    if request.POST:
        form = DefinePreClienteSemInteresseForm(request.POST, instance=precliente)
        if form.is_valid():
            precliente = form.save(commit=False)
            precliente.sem_interesse = True
            precliente.sem_interesse_data = datetime.datetime.now()
            precliente.save()
            messages.success(request, "Sucesso! Pré Cliente marcado como Sem Interesse.")
            return redirect(reverse("comercial:clientes"))
    else:
        form = DefinePreClienteSemInteresseForm(instance=precliente)
    return render_to_response('frontend/comercial/comercial-cliente-precliente-sem-interesse.html', locals(), context_instance=RequestContext(request),)

class FiltrarPreClientesERequisicoesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(FiltrarPreClientesERequisicoesForm, self).__init__(*args, **kwargs)
        self.fields['funcionario'].widget.attrs['class'] = 'select2'
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        self.fields['funcionario'].queryset = Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis)
        

    funcionario = forms.ModelChoiceField(queryset=None, label="Funcionário", required=False, empty_label="Todos do Comercial")


@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def clientes(request):
    form_filtrar_precliente = FiltrarPreClientesERequisicoesForm()  
    cliente_q = request.GET.get('cliente', False)
    if cliente_q:
        cliente_q = cliente_q.strip()
        clientes = Cliente.objects.filter(
            Q(nome__icontains=cliente_q) | \
            Q(fantasia__icontains=cliente_q) | \
            Q(cnpj__icontains=cliente_q) | \
            Q(cpf__icontains=cliente_q)
        )
        #puxa todos os pre clientes, menos os já convertidos)
        preclientes = PreCliente.objects.filter(nome__icontains=cliente_q, cliente_convertido=None) 
    else:
        clientes = Cliente.objects.all()
        preclientes = PreCliente.objects.filter(cliente_convertido=None, sem_interesse=False)

    preclientes_sem_proposta = PreCliente.objects.filter(propostacomercial=None, cliente_convertido=None, sem_interesse=False, designado=request.user.funcionario).order_by('nome')
    requisicoes_propostas = RequisicaoDeProposta.objects.filter(atendido=False).order_by('cliente__nome')
    # se nao for gerente, limita a listagem para os que lhe sao designados
    if not request.user.perfilacessocomercial.gerente:
        preclientes = preclientes.filter(designado=request.user.funcionario)
        preclientes_sem_proposta = preclientes_sem_proposta.filter(designado=request.user.funcionario)
        requisicoes_propostas = requisicoes_propostas.filter(cliente__designado=request.user.funcionario)
        
    if request.POST.get('btn-aplicar-filtro', None):
            form_filtrar_precliente = FiltrarPreClientesERequisicoesForm(request.POST)
            if form_filtrar_precliente.is_valid():
                funcionario_escolhido = form_filtrar_precliente.cleaned_data['funcionario']
                if funcionario_escolhido:
                    clientes = clientes.filter(designado=funcionario_escolhido)
                    preclientes = preclientes.filter(designado=funcionario_escolhido)
                    preclientes_sem_proposta = preclientes_sem_proposta.filter(designado=funcionario_escolhido)
                    requisicoes_propostas = requisicoes_propostas.filter(cliente__designado=funcionario_escolhido)
    
    return render_to_response('frontend/comercial/comercial-clientes.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def cliente_ver(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.POST.get('form-adicionar-endereco', None):
        form_adicionar_endereco = AdicionarEnderecoClienteForm(request.POST, cliente=cliente)
        if form_adicionar_endereco.is_valid():
            endereco = form_adicionar_endereco.save(commit=False)
            if cliente.enderecocliente_set.count():
                endereco.principal = False
            else:
                endereco.principal = True
            endereco.save()
            messages.success(request, 'Endereço Adicionado!')
    else:
        form_adicionar_endereco = AdicionarEnderecoClienteForm(cliente=cliente)
    cliente_q = request.GET.get('cliente', None)
    form_adicionar_follow_up = FormAdicionarFollowUp()

    return render_to_response('frontend/comercial/comercial-cliente-ver.html', locals(), context_instance=RequestContext(request),)

class FormEditarProposta(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormEditarProposta, self).__init__(*args, **kwargs)
        
        if (kwargs['instance'].cliente and kwargs['instance'].cliente.tipo != "pj") or kwargs['instance'].precliente :
            del self.fields['nome_do_proposto']
            del self.fields['documento_do_proposto']
        
        self.fields['valor_proposto'].localize = True
        self.fields['valor_proposto'].widget.is_localized = True
    
    class Meta:
        model = PropostaComercial
        fields = 'valor_proposto', 'nome_do_proposto', 'documento_do_proposto', 'tipo'
        localized_fields = 'valor_proposto',

class FormSelecionaOrcamentoModelo(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FormSelecionaOrcamentoModelo, self).__init__(*args, **kwargs)
        self.fields['modelo'].widget.attrs['class'] = 'select2'
    
    modelo = forms.ModelMultipleChoiceField(queryset=Orcamento.objects.filter(modelo=True, ativo=True), required=True)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_editar_orcamento(request, proposta_id, orcamento_id):
    orcamento = get_object_or_404(Orcamento, proposta__id=proposta_id, pk=orcamento_id)
    OrcamentoFormSet = forms.models.inlineformset_factory(Orcamento, LinhaRecursoMaterial, extra=1, can_delete=True, form=LinhaOrcamentoForm)
    if request.POST:
        if 'adicionar_linha_material' in request.POST:
            messages.info(request, u"Nova Linha de Materiais adicionados")
            cp = request.POST.copy()
            cp['orcamento-TOTAL_FORMS'] = int(cp['orcamento-TOTAL_FORMS'])+ 1
            form_editar_linhas = OrcamentoFormSet(cp, instance=orcamento, prefix='orcamento')
            form_orcamento = OrcamentoForm(cp, instance=orcamento)
        else:
            form_editar_linhas = OrcamentoFormSet(request.POST, instance=orcamento, prefix="orcamento")
            form_orcamento = OrcamentoForm(request.POST, instance=orcamento)
            if form_editar_linhas.is_valid() and form_orcamento.is_valid():
                modelo_linhas = form_editar_linhas.save()
                orcamento = form_orcamento.save()
                messages.success(request, u"Sucesso! Orçamento (%s) Alterado da Proposta #%s" % (orcamento.descricao, orcamento.proposta.id))
                # se cliente, mostra ficha
                return redirect(reverse('comercial:editar_proposta', args=[orcamento.proposta.id]))
            else:
                form_orcamento = OrcamentoForm(request.POST, instance=orcamento)
                
    else:
        form_editar_linhas = OrcamentoFormSet(instance=orcamento, prefix="orcamento")
        form_orcamento = OrcamentoForm(instance=orcamento)
    return render_to_response('frontend/comercial/comercial-editar-proposta-editar-orcamento.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_reajustar_orcamento(request, proposta_id, orcamento_id):
    orcamento = get_object_or_404(Orcamento, proposta__id=proposta_id, pk=orcamento_id)
    orcamento.reajusta_custo()
    messages.success(request, u"Sucesso! Orçamento Reajustado.")
    return redirect(reverse("comercial:editar_proposta", args=[orcamento.proposta.id]))

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_imprimir_orcamento(request, proposta_id, orcamento_id):
    orcamento = get_object_or_404(Orcamento, proposta__id=proposta_id, pk=orcamento_id)
    return render_to_response('frontend/comercial/comercial-editar-proposta-imprimir-orcamento.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_imprimir_orcamentos_da_proposta(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    return render_to_response('frontend/comercial/comercial-editar-proposta-imprimir-orcamentos.html', locals(), context_instance=RequestContext(request),)




@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_inativar_orcamento(request, proposta_id, orcamento_id):
    orcamento = get_object_or_404(Orcamento, proposta__id=proposta_id, pk=orcamento_id)
    orcamento.ativo = False
    orcamento.save()
    messages.success(request, u"Sucesso! Orçamento Inativado.")
    return redirect(reverse("comercial:editar_proposta", args=[orcamento.proposta.id]))


@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_ativar_orcamento(request, proposta_id, orcamento_id):
    orcamento = get_object_or_404(Orcamento, proposta__id=proposta_id, pk=orcamento_id)
    orcamento.ativo = True
    orcamento.save()
    messages.success(request, u"Sucesso! Orçamento Ativado.")
    return redirect(reverse("comercial:editar_proposta", args=[orcamento.proposta.id]))


@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    seleciona_modelos_proposta = FormSelecionaOrcamentoModelo()
    form_editar_proposta = FormEditarProposta(instance=proposta)
    adicionar_orcamento_form = OrcamentoForm(initial={'proposta': proposta.id })
    if request.POST:
        if 'adicionar-modelos' in request.POST:
            seleciona_modelos_proposta = FormSelecionaOrcamentoModelo(request.POST)
            if seleciona_modelos_proposta.is_valid():
                modelos = seleciona_modelos_proposta.cleaned_data['modelo']
                # clona o modelo de orcamento pra dentro da proposta
                for modelo in modelos:
                    linhas_materiais = modelo.linharecursomaterial_set.all()
                    # cria novo orcamento à partir de modelo
                    modelo.pk = None
                    novo_orcamento = modelo
                    novo_orcamento.modelo = False
                    novo_orcamento.proposta = proposta
                    novo_orcamento.save()
                    # copia todos as linhas de materiais pro modelo
                    for linha in linhas_materiais:
                        linha.pk = None
                        linha.orcamento = novo_orcamento
                        linha.save()
        if request.POST.get('adicionar-orcamento-btn'):
            adicionar_orcamento_form = OrcamentoForm(request.POST)
            if adicionar_orcamento_form.is_valid():
                novo_orcamento = adicionar_orcamento_form.save(commit=False)
                novo_orcamento.criado_por = request.user.funcionario
                novo_orcamento.save()
                messages.success(request, u"Sucesso! Novo Orçamento Adicionado.")
                return redirect(reverse("comercial:editar_proposta_editar_orcamento", args=[proposta.id, novo_orcamento.id]))
        if request.POST.get('alterar-proposta'):
            form_editar_proposta = FormEditarProposta(request.POST, instance=proposta)
            if form_editar_proposta.is_valid():
                proposta_alterada = form_editar_proposta.save()
                messages.success(request, u"Sucesso! Proposta #%s alterada!" % proposta.id)
                # se cliente, mostra ficha
                return redirect(reverse('comercial:editar_proposta', args=[proposta_alterada.id]))

        if request.POST.get('adicionar-modelos'):
            seleciona_modelos_proposta = FormSelecionaOrcamentoModelo(request.POST)
            if seleciona_modelos_proposta.is_valid():
                pass

    return render_to_response('frontend/comercial/comercial-editar-proposta.html', locals(), context_instance=RequestContext(request),)

class FormFecharProposta(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormFecharProposta, self).__init__(*args, **kwargs)
        self.fields['definido_perdido_motivo'].required = True

    class Meta:
        model = PropostaComercial
        fields = 'definido_perdido_motivo',

@user_passes_test(possui_perfil_acesso_comercial)
def editar_proposta_fechar(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    if request.POST:
        form_fechar = FormFecharProposta(request.POST, instance=proposta)
        if form_fechar.is_valid():
            proposta = form_fechar.save(commit=False)
            if request.user.perfilacessocomercial.gerente:
                proposta.status = 'perdida'
                messages.info(request, "Sucesso! Proposta fechada como Gerente")
            else:
                proposta.status = 'perdida_aguardando'
                messages.info(request, "Sucesso! Proposta Fechada e Aguardando para Aprovação de Fechamento")
                    
            proposta.definido_perdido_por = request.user.funcionario
            proposta.definido_perdido_em = datetime.datetime.now()
            proposta.save()
            if proposta.cliente:
                return redirect(reverse("comercial:cliente_ver", args=[proposta.cliente.id]))
            else:
                return redirect(reverse("comercial:propostas_comerciais_minhas"))

    else:
        form_fechar = FormFecharProposta()
    return render_to_response('frontend/comercial/comercial-proposta-fechar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def gerencia_aprovar_fechamentos(request):
    if request.POST:
        propostas_a_fechar = request.POST.getlist('seleciona_propostas_fechar')
        propostas = PropostaComercial.objects.filter(pk__in=propostas_a_fechar)
        for proposta in propostas:
            if request.POST.get('aprovar-fechamento'):
                proposta.status = 'perdida'
                messages.error(request, "Proposta #%s Fechada!" % proposta.id)
            elif request.POST.get('reabrir-proposta'):
                proposta.status = 'aberta'
                messages.success(request, "Proposta #%s Reaberta!" % proposta.id)
            proposta.save()
                
    propostas_fechadas = PropostaComercial.objects.filter(status="perdida_aguardando")
    return render_to_response('frontend/comercial/comercial-gerenciar-aprovar-perdidas.html', locals(), context_instance=RequestContext(request),)


class LancamentoFinanceiroReceberComercialForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        total_proposto = kwargs.pop('total_proposto', 0)
        super(LancamentoFinanceiroReceberComercialForm, self).__init__(*args, **kwargs)
        self.fields['data_cobranca'].widget.attrs['class'] = 'datepicker'
        self.fields['valor_cobrado'].localize = True
        self.fields['valor_cobrado'].widget.is_localized = True
        self.fields['valor_cobrado'].widget.attrs['class'] = 'valor_parcela'
    
    def clean_data_cobranca(self):
        data = self.cleaned_data['data_cobranca']
        if data < datetime.date.today():
            raise forms.ValidationError("Erro! Data de Cobrança deve ser maior que data atual")
        return data
    
    class Meta:
        model = LancamentoFinanceiroReceber
        fields = ("data_cobranca", 'valor_cobrado', 'modo_recebido')
        localized_fields = 'valor_cobrado',

class ConfigurarContratoBaseadoEmProposta(forms.Form):
    '''Formulario usado pra alterar as informacoes que serao importadas
    pro contrato com base na proposta'''
    
    def __init__(self, *args, **kwargs):
        super(ConfigurarContratoBaseadoEmProposta, self).__init__(*args, **kwargs)
        self.fields['apoio_tecnico'].widget.attrs['class'] = 'select2'
    
    objeto = forms.CharField(widget = forms.Textarea, label="Objeto do Contrato", required=True)
    garantia = forms.CharField(widget = forms.Textarea, label="Garantia", required=True)
    items_incluso = forms.CharField(widget = forms.Textarea, label="Itens Inclusos", required=True)
    items_nao_incluso = forms.CharField(widget = forms.Textarea, label=u"Itens Não Inclusos", required=True)
    observacoes = forms.CharField(widget = forms.Textarea, label=u"Observações", required=False)
    nome_do_proposto_legal = forms.CharField()
    documento_do_proposto_legal = forms.CharField()
    apoio_tecnico = forms.ModelChoiceField(queryset=Funcionario.objects.exclude(periodo_trabalhado_corrente=None), label=u"Apoio Técnico", required=False)



class UsarCartaoCredito(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(UsarCartaoCredito, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs['class'] = 'datepicker'
    
    data = forms.DateField(initial=datetime.date.today())
    parcelas = forms.IntegerField()

@user_passes_test(possui_perfil_acesso_comercial)
def editar_proposta_converter(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id, status="aberta")
    ConfigurarConversaoPropostaFormset = forms.models.inlineformset_factory(ContratoFechado, LancamentoFinanceiroReceber, extra=1, can_delete=True, form=LancamentoFinanceiroReceberComercialForm)
    usar_cartao_credito = UsarCartaoCredito()
    configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(
        initial={
            'objeto': proposta.objeto_proposto,
            'garantia': proposta.garantia_proposto,
            'items_incluso': proposta.descricao_items_proposto,
            'items_nao_incluso': proposta.items_nao_incluso,
            'observacoes': proposta.forma_pagamento_proposto,
            'nome_do_proposto_legal': proposta.nome_do_proposto,
            'documento_do_proposto_legal': proposta.documento_do_proposto,
        }
    )
    form_configurar_contrato = ConfigurarConversaoPropostaFormset(prefix="configurar_contrato")
    if proposta.cliente:
        # tratar a proposta do cliente e converter
        if request.POST:
            if 'usar-cartao' in request.POST:
                form_cartao = UsarCartaoCredito(request.POST)
                if form_cartao.is_valid():
                    data = form_cartao.cleaned_data['data']
                    parcelas = form_cartao.cleaned_data['parcelas']
                    form_configurar_contrato = ConfigurarConversaoPropostaFormset(request.POST, prefix="configurar_contrato")
                    total_lancamentos = 0
                    for form in form_configurar_contrato.forms:
                        if form not in form_configurar_contrato.deleted_forms:
                            if form.cleaned_data and form.cleaned_data.get('valor_cobrado'):
                                total_lancamentos += form.cleaned_data.get('valor_cobrado', 0)
                    total_restante = proposta.valor_proposto - total_lancamentos
                    if total_restante > 0:
                        # nenhum lancamento inicial, será tudo no cartão
                        cp = request.POST.copy()
                        form_index_offset = len(form_configurar_contrato.forms)
                        if total_lancamentos == 0:
                            cp['configurar_contrato-TOTAL_FORMS'] = parcelas
                            range_parcelas = range(parcelas)
                        else:                        
                            cp['configurar_contrato-TOTAL_FORMS'] = int(cp['configurar_contrato-TOTAL_FORMS'])+ parcelas
                            range_parcelas = range(parcelas+form_index_offset)[form_index_offset:]
                        cada_parcela = total_restante / parcelas
                        for p in range_parcelas:
                            data = data+datetime.timedelta(days=30)
                            cp['configurar_contrato-%s-data_cobranca' % p] = data
                            cp['configurar_contrato-%s-modo_recebido' % p] = 'credito'
                            cp['configurar_contrato-%s-valor_cobrado' % p] = cada_parcela
                        form_configurar_contrato = ConfigurarConversaoPropostaFormset(cp, prefix="configurar_contrato")
                        configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST)
                        messages.info(request, 'Adicionando %s parcelas de %s para o dia %s' % (parcelas, cada_parcela, data))
                    else:
                        messages.error(request, u"Erro! Não existe mais Valor restante para parcelar no cartão")
            if 'adicionar-parcela' in request.POST:
                messages.info(request, u"Nova Parcela de Lançamento Financeiro a Receber Adicionada!")
                cp = request.POST.copy()
                cp['configurar_contrato-TOTAL_FORMS'] = int(cp['configurar_contrato-TOTAL_FORMS'])+ 1
                form_configurar_contrato = ConfigurarConversaoPropostaFormset(cp, prefix="configurar_contrato")
                configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST)
            elif 'converter-contrato' in request.POST:
                configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST)
                form_configurar_contrato = ConfigurarConversaoPropostaFormset(request.POST, prefix="configurar_contrato")
                if form_configurar_contrato.is_valid() and configurar_contrato_form.is_valid():
                    # checa se total preenchido no formulario bate com valor proposto
                    total_lancamentos = 0
                    for form in form_configurar_contrato.forms:
                        if form not in form_configurar_contrato.deleted_forms:
                            if form.cleaned_data and form.cleaned_data.get('valor_cobrado'):
                                total_lancamentos += form.cleaned_data.get('valor_cobrado', 0)
                    if float(total_lancamentos) == float(proposta.valor_proposto):
                        # converte proposta e marca data e quem converteu
                        proposta.status = "convertida"
                        proposta.definido_convertido_em = datetime.datetime.now()
                        proposta.definido_convertido_por = request.user.funcionario
                        # cria o Contrato Convertido
                        novo_contrato = ContratoFechado.objects.create(
                            cliente=proposta.cliente,
                            objeto=proposta.objeto_proposto,
                            valor=proposta.valor_proposto,
                            status="emanalise",
                            responsavel=request.user.funcionario,
                            responsavel_comissionado=proposta.designado,
                        )
                        # relaciona novo contrato com essa proposta
                        proposta.contrato_vinculado = novo_contrato
                        #salva a proposta
                        proposta.save()
                        # registra lancamentos vinculando ao novo contrato
                        i = 0
                        for form in form_configurar_contrato.forms:
                            if form.is_valid():
                                i += 1
                                novo_lancamento = form.save(commit=False)
                                novo_lancamento.contrato = novo_contrato
                                novo_lancamento.peso = i
                                novo_lancamento.save()
                        # registra os dados configurados para o contrato (alterados ou importados da proposta)
                        novo_contrato.objeto = configurar_contrato_form.cleaned_data['objeto']
                        novo_contrato.garantia = configurar_contrato_form.cleaned_data['garantia']
                        novo_contrato.items_incluso = configurar_contrato_form.cleaned_data['items_incluso']
                        novo_contrato.items_nao_incluso = configurar_contrato_form.cleaned_data['items_nao_incluso']
                        novo_contrato.observacoes = configurar_contrato_form.cleaned_data['observacoes']
                        novo_contrato.nome_proposto_legal = configurar_contrato_form.cleaned_data['nome_do_proposto_legal']
                        novo_contrato.documento_proposto_legal = configurar_contrato_form.cleaned_data['documento_do_proposto_legal']
                        novo_contrato.apoio_tecnico = configurar_contrato_form.cleaned_data['apoio_tecnico']
                        novo_contrato.save()  
                        # retorna para a view contratos em analise
                        if request.user.perfilacessocomercial.gerente:
                            # se gerente, retorna para contratos em analise
                            return redirect(reverse("comercial:analise_de_contratos"))
                        else:
                            # caso contrario, retorna para a ficha do cliente
                            return redirect(reverse("comercial:cliente_ver", args=[novo_contrato.cliente.id]))
                    else:
                        messages.error(request, u"Erro! Valor das parcelas (R$ %s) NÃO CONFERE com valor proposto: R$ %s" % (total_lancamentos, proposta.valor_proposto))

        return render_to_response('frontend/comercial/comercial-proposta-converter.html', locals(), context_instance=RequestContext(request),)
    else:
        # converter pre cliente em cliente
        # manter referencia da proposta
        # continuar processo de conversão
        messages.error(request, u'É obrigatório converter um Pré Cliente para Cliente ANTES de converter uma proposta.')
        return redirect(reverse("comercial:precliente_converter", args=[proposta.precliente.id])+"?proposta_referencia=%s" % proposta.id)


class VincularPreClienteParaClienteForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(VincularPreClienteParaClienteForm, self).__init__(*args, **kwargs)
        self.fields['cliente'].widget.attrs['class'] = 'select2'
    
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())


class VincularPreClienteParaPreClienteForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.precliente = kwargs.pop('precliente')
        super(VincularPreClienteParaPreClienteForm, self).__init__(*args, **kwargs)
        self.fields['precliente'].widget.attrs['class'] = 'select2'
        self.fields['precliente'].queryset = PreCliente.objects.all().exclude(id=self.precliente.id)
    
    precliente = forms.ModelChoiceField(queryset=None)


@user_passes_test(possui_perfil_acesso_comercial)
def precliente_ver(request, pre_cliente_id):
    precliente = get_object_or_404(PreCliente, pk=pre_cliente_id)
    form_adicionar_follow_up = FormAdicionarFollowUp()

    if request.POST:
        form_vincular_a_cliente = VincularPreClienteParaClienteForm(request.POST)
        form_vincular_a_precliente = VincularPreClienteParaPreClienteForm(request.POST, precliente=precliente)
        if form_vincular_a_cliente.is_valid():
            # passa todas as propostas deste precliente para o cliente selecionado
            cliente_selecionado = form_vincular_a_cliente.cleaned_data.get('cliente')
            for proposta in precliente.propostacomercial_set.all():
                proposta.precliente = None
                proposta.cliente = cliente_selecionado
                proposta.save()
                cliente_selecionado.designado = precliente.designado
                texto = """DADOS VINCULADOS DO PRE CLIENTE
                DADOS: %s
                CONTATO: %s
                """ % (precliente.dados, precliente.contato)
                cliente_selecionado.observacao = texto
                cliente_selecionado.save()
                messages.info(request, "Proposta %s vinculada ao Cliente %s" % (proposta.id, cliente_selecionado))
            messages.success(request, "Pré Cliente %s Removido" % precliente)
            precliente.delete()
            return redirect(reverse("comercial:cliente_ver", args=[cliente_selecionado.id] ))

        elif form_vincular_a_precliente.is_valid():
            precliente_selecionado = form_vincular_a_precliente.cleaned_data.get('precliente')
            for proposta in precliente_selecionado.propostacomercial_set.all():
                proposta.precliente = precliente
                proposta.save()
            precliente_selecionado.delete()
            messages.success(request, "Pré Cliente %s Removido. Todas as propostas agora estão em %s" % (precliente_selecionado, precliente))
            return redirect(reverse("comercial:precliente_ver", args=[precliente.id] ))
    else:
        form_vincular_a_cliente = VincularPreClienteParaClienteForm()
        form_vincular_a_precliente = VincularPreClienteParaPreClienteForm(precliente=precliente)
    return render_to_response('frontend/comercial/comercial-precliente-ver.html', locals(), context_instance=RequestContext(request),)

# Pre Cliente
@user_passes_test(possui_perfil_acesso_comercial)
def precliente_adicionar(request):
    if request.POST:
        try:
            form = form_add_precliente = PreClienteAdicionarForm(data=request.POST, sugestao=None, perfil=request.user.perfilacessocomercial)
            if form.is_valid():
                precliente = form.save(commit=False)
                precliente.adicionado_por = request.user.funcionario
                precliente.save()
                messages.success(request, u'Pré Cliente %s adicionado com sucesso!' % precliente)
                return redirect(reverse('comercial:propostas_comerciais_precliente_adicionar', args=[precliente.id]))
        except:
            raise
    else:
        sugestao = request.GET.get('sugestao', None)
        form_add_precliente = PreClienteAdicionarForm(sugestao=sugestao, perfil=request.user.perfilacessocomercial)
    return render_to_response('frontend/comercial/comercial-preclientes-adicionar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def precliente_converter(request, pre_cliente_id):
    precliente = get_object_or_404(PreCliente, id=pre_cliente_id)
    if request.POST:
        form = AdicionarCliente(request.POST, precliente=precliente)
        if form.is_valid():
            # cria novo cliente
            cliente_novo = form.save(commit=False)
            cliente_novo.designado = precliente.designado
            cliente_novo.save()
            # vincula pre cliente com cliente novo
            precliente.cliente_convertido = cliente_novo
            precliente.data_convertido = datetime.date.today()
            precleitne_convertido_por = request.user.funcionario
            precliente.save()
            # altera todas as propostas do precliente para o cliente_novo
            propostas_precliente = PropostaComercial.objects.filter(precliente=precliente)
            propostas_precliente.update(precliente=None, cliente=cliente_novo)
            # retorna para a proposta de referencia
            if request.GET.get('proposta_referencia'):
                return redirect(reverse('comercial:editar_proposta_converter', args=[request.GET.get('proposta_referencia')]))
            # retorna para a nova ficha do cliente
            else:
                return redirect(reverse('comercial:cliente_ver', args=[cliente_novo.id]))
    else:
        form = AdicionarCliente(precliente=precliente)
    return render_to_response('frontend/comercial/comercial-precliente-converter.html', locals(), context_instance=RequestContext(request),)

# propostas comerciais
@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_cliente(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    propostas_abertas = PropostaComercial.objects.filter(cliente=cliente, status='aberta')
    return render_to_response('frontend/comercial/comercial-propostas-cliente.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_cliente_adicionar(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    if request.POST:
        form = AdicionarPropostaForm(request.POST)
        if form.is_valid():
            proposta = form.save(commit=False)
            proposta.cliente = cliente
            proposta.criador_por = request.user.funcionario
            proposta.designado = cliente.designado
            proposta.save()
            # vincula proposta com a requisicao de origem
            if request.GET.get('requisicao_origem', None):
                requisicao_proposta = RequisicaoDeProposta.objects.get(pk=request.GET.get('requisicao_origem', None))
                requisicao_proposta.atendido = True
                requisicao_proposta.atendido_data = datetime.datetime.now()
                requisicao_proposta.atendido_por = request.user.funcionario
                requisicao_proposta.proposta_vinculada = proposta
                requisicao_proposta.save()
            return redirect(reverse('comercial:editar_proposta', args=[proposta.id]))
    else:
        form = AdicionarPropostaForm()
    return render_to_response('frontend/comercial/comercial-propostas-cliente-adicionar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_precliente(request, precliente_id):
    precliente = PreCliente.objects.get(pk=precliente_id)
    propostas_abertas = PropostaComercial.objects.filter(precliente=precliente, status='aberta')
    return render_to_response('frontend/comercial/comercial-propostas-precliente.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_precliente_adicionar(request, precliente_id):
    precliente = PreCliente.objects.get(pk=precliente_id)
    if request.POST:
        form = AdicionarPropostaForm(request.POST)
        if form.is_valid():
            proposta = form.save(commit=False)
            proposta.precliente = precliente
            proposta.criado_por = request.user.funcionario
            proposta.designado = precliente.designado
            proposta.save()
            messages.success(request, "Sucesso! Proposta Adicionada para Pré Cliente.")
            return redirect(reverse('comercial:editar_proposta', args=[proposta.id]))
    else:
        form = AdicionarPropostaForm()
    return render_to_response('frontend/comercial/comercial-propostas-precliente-adicionar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_minhas(request):
    propostas_abertas_validas = PropostaComercial.objects.filter(status='aberta', data_expiracao__gte=datetime.date.today()).order_by('cliente', 'precliente')
    propostas_abertas_expiradas = PropostaComercial.objects.filter(status='aberta', data_expiracao__lt=datetime.date.today())    
    form_adicionar_follow_up = FormAdicionarFollowUp()

    if not request.user.perfilacessocomercial.gerente:
        propostas_abertas_validas = propostas_abertas_validas.filter(
            Q(cliente__designado=request.user.funcionario) | Q(precliente__designado=request.user.funcionario) | Q(designado=request.user.funcionario) | Q(designado=None) & \
            (Q(precliente__designado=None) & Q(cliente__designado=None))
            )
        propostas_abertas_expiradas = propostas_abertas_expiradas.filter(
            Q(cliente__designado=request.user.funcionario) | Q(precliente__designado=request.user.funcionario) | Q(designado=request.user.funcionario) | Q(designado=None) & \
            (Q(precliente__designado=None) & Q(cliente__designado=None))
            )
    
    
    designados_propostas_validas = propostas_abertas_validas.values('designado__nome', 'designado__id').annotate(Count('designado__nome'))
    designados_propostas_expiradas = propostas_abertas_expiradas.values('designado__nome', 'designado__id').annotate(Count('designado__nome'))
    
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

class FiltraTabelaDePrecos(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FiltraTabelaDePrecos, self).__init__(*args, **kwargs)
        self.fields['buscar'].widget.attrs['class'] = 'input-xxlarge'
    
    buscar = forms.CharField(required=True, label='')
    
@user_passes_test(possui_perfil_acesso_comercial)
def tabela_de_precos(request):
    if request.POST:
        form_filtra_tabela = FiltraTabelaDePrecos(request.POST)
        if form_filtra_tabela.is_valid():
            queries = form_filtra_tabela.cleaned_data['buscar'].split()
            qset1 =  reduce(operator.__and__, [Q(codigo=query) | Q(descricao__icontains=query) | Q(nome__icontains=query)  for query in queries])
            produtos = Produto.objects.filter(qset1).order_by('-preco_consumo').distinct()
    else:
        form_filtra_tabela = FiltraTabelaDePrecos()
    return render_to_response('frontend/comercial/comercial-consultar-tabela-precos.html', locals(), context_instance=RequestContext(request),)

class FormEscolherClientesEPreClientes(forms.Form):
    
    
    def __init__(self, *args, **kwargs):
        super(FormEscolherClientesEPreClientes, self).__init__(*args, **kwargs)
        self.fields['clientes'].widget.attrs['class'] = 'select2'
        self.fields['preclientes'].widget.attrs['class'] = 'select2'
    
    
    clientes = forms.ModelMultipleChoiceField(required=False, queryset=Cliente.objects.all())
    preclientes = forms.ModelMultipleChoiceField(required=False, queryset=PreCliente.objects.filter(cliente_convertido=None))

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def designacoes(request):
    escolher_clientes_form = FormEscolherClientesEPreClientes()
    cliente_sem_designacao = Cliente.objects.filter(designado=None)
    precliente_sem_designacao = PreCliente.objects.filter(designado=None, cliente_convertido=None)
    cliente_designacao_invalida = Cliente.objects.exclude(designado=None).filter(designado__periodo_trabalhado_corrente=None)
    precliente_designacao_invalida = PreCliente.objects.exclude(designado=None).filter(designado__periodo_trabalhado_corrente=None, cliente_convertido=None)
    return render_to_response('frontend/comercial/comercial-designacoes.html', locals(), context_instance=RequestContext(request),)

class ConfirmarDesignacao(forms.Form):
    
    def __init__(self, *args, **kwargs):
        clientes = kwargs.pop('clientes', None)
        preclientes = kwargs.pop('preclientes', None)
        super(ConfirmarDesignacao, self).__init__(*args, **kwargs)
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        self.fields['designado'].queryset = Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis)
        self.fields['designado'].widget.attrs['class'] = 'select2'
        self.fields['preclientes'].widget = forms.MultipleHiddenInput()
        self.fields['clientes'].widget = forms.MultipleHiddenInput()
        if clientes:
            self.fields['clientes'].queryset = Cliente.objects.all()
            self.fields['clientes'].initial = clientes
        # pre
        if preclientes:
            self.fields['preclientes'].queryset = PreCliente.objects.filter(cliente_convertido=None)
            self.fields['preclientes'].initial = preclientes
            
        
    designado = forms.ModelChoiceField(required=True, queryset=None, label="Novo Designado", empty_label=None)
    clientes = forms.ModelMultipleChoiceField(required=False, queryset=Cliente.objects.all())
    preclientes = forms.ModelMultipleChoiceField(required=False, queryset=PreCliente.objects.filter(cliente_convertido=None))

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def designacoes_confirmar(request):
    if request.POST:
        if request.POST.get('analisar-desginacoes-btn'):
            clientes_id = request.POST.getlist('clientes')
            clientes = Cliente.objects.filter(id__in=clientes_id).all()
            # preclients
            preclientes_id = request.POST.getlist('preclientes')
            preclientes = PreCliente.objects.filter(id__in=preclientes_id).all()
            form = ConfirmarDesignacao(clientes=clientes, preclientes=preclientes)

        if request.POST.get('confirmar-designacoes-btn'):
            form = ConfirmarDesignacao(request.POST)
            if form.is_valid():
                # designa os preclientes
                designado = form.cleaned_data['designado']
                # preclientes
                form.cleaned_data['preclientes'].update(designado=designado)
                messages.success(request, u"Nova Designação para Pré Clientes Selecionados -> %s" % designado)
                # clientes
                form.cleaned_data['clientes'].update(designado=designado)
                messages.success(request, u"Nova Designação para Clientes Selecionados -> %s" % designado)
                return redirect(reverse('comercial:home'))
        return render_to_response('frontend/comercial/comercial-designacoes-confirmar.html', locals(), context_instance=RequestContext(request),)
    else:
        messages.warning(request, u"Não pode ser acessado diretamente")
        return redirect(reverse("comercial:designacoes"))

class ConfigurarPropostaComercialParaImpressao(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        modelos = kwargs.pop('modelos')
        super(ConfigurarPropostaComercialParaImpressao, self).__init__(*args, **kwargs)
        self.fields['modelo'] = forms.ChoiceField(choices=modelos, label="Tipo de Proposta")
    
    def clean(self):
        cleaned_data = super(ConfigurarPropostaComercialParaImpressao, self).clean()
        representante_legal = cleaned_data.get("representante_legal_proposto")
        if self.instance and self.instance.cliente:
            if self.instance.cliente.tipo == "pj" and not representante_legal:
                raise ValidationError(u"Erro! Para clientes do tipo Pessoa Jurídica é obrigatório um Representante Legal!")
        return cleaned_data

    class Meta:
        model = PropostaComercial
        fields = 'nome_do_proposto', 'documento_do_proposto', 'rua_do_proposto', 'bairro_do_proposto', \
        'cep_do_proposto', 'cidade_do_proposto', 'endereco_obra_proposto', 'representante_legal_proposto', \
        'telefone_contato_proposto', 'email_proposto', 'objeto_proposto', 'descricao_items_proposto', 'items_nao_incluso', 'forma_pagamento_proposto', 'garantia_proposto',

class OrcamentoPrint:
    """ 
    Gera o orcamento impresso.
    """

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
    
    def _header_footer(self, canvas, doc):
            # Save the state of our canvas so we can draw on it
            canvas.saveState()
            styles = getSampleStyleSheet()
 
            # Footer
            footer = Paragraph('<Br /><br/>POP CO 001-F01<br />REV-001', styles['Normal'])
            footer.wrap(doc.width, doc.bottomMargin)
            footer.drawOn(canvas, 10, 10)
            # Release the canvas
            canvas.restoreState()
    
    def print_proposta(self, proposta, tipo, perfil=None):
        
            buffer = self.buffer
            doc = SimpleDocTemplate(buffer,
                                    rightMargin=40,
                                    leftMargin=40,
                                    topMargin=10,
                                    bottomMargin=70,
                                    pagesize=self.pagesize)
            
            # A large collection of style sheets pre-made for us
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='centered_h1', alignment=TA_CENTER, fontSize=15, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))
            styles.add(ParagraphStyle(name='left_h1', alignment=TA_LEFT, fontSize=15, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left_h2', alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='right', alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name='right_h2', alignment=TA_RIGHT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='justify', alignment=TA_JUSTIFY))

            # Our container for 'Flowable' objects
            elements = []
            # logo empresa
            
            im = Image(getattr(settings, 'IMG_PATH_LOGO_EMPRESA'),)
            im.hAlign = 'LEFT'
            
            # id da proposta
            id_proposta = Paragraph("Nº PROPOSTA: %s" % str(proposta.id), styles['right'])
            
            imprime_logo = getattr(settings, 'IMPRIME_LOGO_PROPOSTA', True)
            if imprime_logo:
                data=[(im,id_proposta)]
            else:
                data=[('',id_proposta)]

            table_logo = Table(data, colWidths=270, rowHeights=79)
            table_logo.setStyle(TableStyle([('VALIGN',(-1,-1),(-1,-1),'MIDDLE')]))
            elements.append(table_logo)
            
            if tipo == 'servico':
                # descricao
                id_desc_p = Paragraph("PROPOSTA COMERCIAL", styles['centered_h1'])
                elements.append(id_desc_p)
                
                # space
                elements.append(Spacer(1, 24))
                
                # AC
                texto_endereco = u"<strong>Rua</strong> %s, <strong>Bairro</strong>: %s, <strong>CEP</strong>: %s, <strong>Cidade</strong>: %s" % \
                    (proposta.rua_do_proposto, proposta.bairro_do_proposto, proposta.cep_do_proposto, proposta.cidade_do_proposto)
                texto = u"<b>A/C</b>: %s<br />\
            	<b>Telefone</b>: %s<br />\
            	<b>Endereço do Cliente</b>: %s <br />"% (
                        proposta.nome_do_proposto, proposta.telefone_contato_proposto, 
                        texto_endereco
                    )
                    
                contratante_p = Paragraph(texto, styles['justify'])
                elements.append(contratante_p)
                
                if proposta.email_proposto:
                    texto = u"<b>E-mail</b>: %s<br />" % proposta.email_proposto
                    contratante_p = Paragraph(texto, styles['justify'])
                    elements.append(contratante_p)
                
                if proposta.endereco_obra_proposto:
                    # space
                    elements.append(Spacer(1, 12))
                    texto = u"<b>Endereço da Obra</b>: %s<br />" % proposta.endereco_obra_proposto
                    endereco_obra_texto = Paragraph(texto, styles['justify'])
                    elements.append(endereco_obra_texto)                
                
                # space
                elements.append(Spacer(1, 24))
                
                texto_introducao_proposta = getattr(settings, 'TEXTO_INTRODUCAO_PROPOSTA_COMERCIAL', 'TEXTO INTRODUÇÃO PROPOSTA COMERCIAL')
                texto_introducao_proposta_p = Paragraph(texto_introducao_proposta, styles['justify'])
                elements.append(texto_introducao_proposta_p)

                # space
                elements.append(Spacer(1, 24))
                
                # 1 - DO OBJETO
                do_objeto_titulo = Paragraph("1 - DO OBJETO", styles['left_h2'])
                elements.append(do_objeto_titulo)
                elements.append(Spacer(1, 12))
                # objeto texto
                texto_objeto_p = Paragraph(proposta.objeto_proposto.replace('\n', '<br />'), styles['justify'])
                elements.append(texto_objeto_p)
                
                # space
                elements.append(Spacer(1, 24))
                
                # 1.1 - Descrição dos Itens
                desc_itens_titulo = Paragraph("1.1 - DESCRIÇÃO DOS ITEMS", styles['left_h2'])
                elements.append(desc_itens_titulo)
                # space
                elements.append(Spacer(1, 12))
                
                # objeto texto
                # 1.1 - Descrição dos Itens
                desc_itens_titulo = Paragraph("1.1.1 - MATERIAL INCLUSO", styles['left_h2'])
                elements.append(desc_itens_titulo)
                
                texto_desc_itens_p = Paragraph(proposta.descricao_items_proposto.replace('\n', '<br />'), styles['justify'])
                elements.append(texto_desc_itens_p)
                
                # space
                elements.append(Spacer(1, 24))
                
                
                # 1.2 - Descrição dos Itens Não Inclusos
                desc_itens_titulo = Paragraph("1.1.2 - MATERIAL NÃO INCLUSO", styles['left_h2'])
                elements.append(desc_itens_titulo)
                # space
                elements.append(Spacer(1, 12))
                
                # objeto texto
                texto_desc_itens_p = Paragraph(proposta.items_nao_incluso.replace('\n', '<br />'), styles['justify'])
                elements.append(texto_desc_itens_p)
                
                elements.append(PageBreak())
                
                elements.append(table_logo)
                
                elements.append(Spacer(1, 24))
                
                # 2 - Do valor e formas de pagamento
                titulo = Paragraph("2 - DOS VALORES", styles['left_h2'])
                elements.append(titulo)
                # space
                elements.append(Spacer(1, 12))
                
                
                locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")
                valor_formatado = locale.currency(proposta.valor_proposto, grouping=True)
                texto = "O valor global da proposta é de <strong>%s</strong>" % valor_formatado
                texto_p = Paragraph(texto, styles['justify'])
                elements.append(texto_p)
                

                # space
                elements.append(Spacer(1, 24))

                # 2.1 - Descrição dos Itens
                desc_itens_titulo = Paragraph("2.1 - FORMAS DE PAGAMENTO", styles['left_h2'])
                elements.append(desc_itens_titulo)
                
                # space
                elements.append(Spacer(1, 12))
                
                # objeto texto
                texto = Paragraph(proposta.forma_pagamento_proposto.replace('\n', '<br />'), styles['justify'])
                elements.append(texto)
                
                # space
                elements.append(Spacer(1, 24))
                
                # 3 - VALIDADE
                titulo = Paragraph("3 - VALIDADE", styles['left_h2'])
                elements.append(titulo)
                
                # space
                elements.append(Spacer(1, 12))
                
                # texto validade
                validade = "Essa proposta é válida até %s" % proposta.data_expiracao.strftime("%d/%m/%Y")
                texto = Paragraph(validade, styles['justify'])
                elements.append(texto)
                
                # space
                elements.append(Spacer(1, 24))
                
            elif tipo == "projetoeletrico":
                
                id_desc_p = Paragraph("Proposta de Elaboração de Projeto Elétrico", styles['centered_h1'])
                elements.append(id_desc_p)
                
                # space
                elements.append(Spacer(1, 12))
                
                contratante_texto = u"<strong>Cliente</strong>: %s, <strong>Documento:</strong> %s, <strong>Localizado à rua</strong> %s, <strong>Bairro</strong>: %s, <strong>CEP</strong>: %s, <strong>Cidade</strong>: %s" %\
                    (proposta.nome_do_proposto, proposta.documento_do_proposto, proposta.rua_do_proposto, proposta.bairro_do_proposto, proposta.cep_do_proposto, proposta.cidade_do_proposto)
                contratante_texto_p = Paragraph(contratante_texto, styles['justify'])
                elements.append(contratante_texto_p)

                # space
                elements.append(Spacer(1, 12))
                                
                endereco_texto = u"<strong>Endereço da Obra</strong>: %s, <strong>Representante Legal</strong>: %s, <strong>Telefone(s)</strong>: %s" % \
                    (proposta.endereco_obra_proposto, proposta.representante_legal_proposto, proposta.telefone_contato_proposto)
                endereco_texto_p = Paragraph(endereco_texto, styles['justify'])
                elements.append(endereco_texto_p)
                
                # space
                elements.append(Spacer(1, 12))
                
                # Proponente
                texto_proponente = getattr(settings, 'TEXTO_PROPONENTE_PROJETO_ELETRICO', 'SETTINGS: TEXTO_PROPONENTE_PROJETO_ELETRICO')
                texto_proponente_p = Paragraph(texto_proponente, styles['justify'])
                elements.append(texto_proponente_p)

                # space
                elements.append(Spacer(1, 12))
                                
                # 1 - DO OBJETO
                do_objeto_titulo = Paragraph("1 - DO OBJETO", styles['left_h2'])
                elements.append(do_objeto_titulo)
                # objeto texto
                texto_objeto_p = Paragraph(proposta.objeto_proposto, styles['justify'])
                elements.append(texto_objeto_p)

                # space
                elements.append(Spacer(1, 12))


                # 1.1 - Descrição dos Itens
                desc_itens_titulo = Paragraph("1.1 - DESCRIÇÃO DOS ITEMS", styles['left_h2'])
                elements.append(desc_itens_titulo)
                # objeto texto
                texto_desc_itens_p = Paragraph(proposta.descricao_items_proposto.replace('\n', '<br />'), styles['justify'])
                elements.append(texto_desc_itens_p)
                
                # space
                elements.append(Spacer(1, 12))
                
                # 2.1 - Descrição dos Itens
                desc_itens_titulo = Paragraph("2.1 - FORMAS DE PAGAMENTO", styles['left_h2'])
                elements.append(desc_itens_titulo)
                # objeto texto
                texto = Paragraph(proposta.forma_pagamento_proposto, styles['justify'])
                elements.append(texto)
                
                # space
                elements.append(Spacer(1, 12))
                
                # 3 - VALIDADE
                titulo = Paragraph("3 - VALIDADE", styles['left_h2'])
                elements.append(titulo)
                
                # texto validade
                validade = "Essa proposta é válida até %s" % proposta.data_expiracao.strftime("%d/%m/%Y")
                texto = Paragraph(validade, styles['justify'])
                elements.append(texto)
                
            # TEXTO ESQUERDA FINAL
            if perfil.user.funcionario:
                responsavel_proposta = perfil.user.funcionario
            else:
                responsavel_proposta = proposta.designado
            
            
            
            if perfil and perfil.imagem_assinatura:
                # space
                elements.append(Spacer(1, 12))
                
                im = Image(perfil.imagem_assinatura.path, width=2*inch,height=1*inch,kind='proportional')
                im.hAlign = 'LEFT'
                elements.append(im)
            
            texto_esquerda_final = "Atenciosamente,<br /><b>%s</b>" % responsavel_proposta
            
            if perfil.user.funcionario.sexo == "m":
                texto_esquerda_final += "<br />Consultor de Vendas<br />"
            else:
                texto_esquerda_final += "<br />Consultora de Vendas<br />"
            
            if perfil.telefone_celular and perfil.telefone_fixo:
                texto_esquerda_final += "%s / %s" % (perfil.telefone_celular, perfil.telefone_fixo)


            elif perfil.telefone_fixo and not perfil.telefone_celular:
                texto_esquerda_final += "%s" % perfil.telefone_fixo
            else:
                texto_esquerda_final += "%s" % perfil.telefone_celular
            
            # space
            elements.append(Spacer(1, 12))
			
            texto_esquerda_final_p = Paragraph(texto_esquerda_final, styles['left'])
            
            telefone_empresa = getattr(settings, 'TELEFONE_EMPRESA', None)
            
            
            # TEXTO DIREITA FINAL
            
            texto_direita_final = """__________________________________________________<br />
            <br />
			Proposta aceita por %s<br /><br />
			Em ___________ de _____________________ de %s.""" % (proposta.representante_legal_proposto, datetime.date.today().strftime("%Y"))
            
            texto_direita_final_p = Paragraph(texto_direita_final, styles['left'])
            
            data=[(texto_esquerda_final_p,texto_direita_final_p)]
            table = Table(data, colWidths=270, rowHeights=79)
            
            elements.append(texto_esquerda_final_p)
            # space
            elements.append(Spacer(1, 20))
            if telefone_empresa:
                texto_telefone_empresa = Paragraph(telefone_empresa, styles['left'])
                elements.append(texto_telefone_empresa)
                # space
                elements.append(Spacer(1, 20))
                
            
            
            elements.append(texto_direita_final_p)
                
            # build pdf
            doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer, canvasmaker=NumberedCanvas)
 
            # Get the value of the BytesIO buffer and write it to the response.
            pdf = buffer.getvalue()
            buffer.close()
            return pdf


class FormEnviarPropostaEmail(forms.Form):
    
    email = forms.CharField(help_text="Para mais emails: email1, email2, email3")


@user_passes_test(possui_perfil_acesso_comercial)
def proposta_comercial_imprimir(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    if proposta.cliente:
        email_inicial = proposta.cliente.email
    if proposta.email_proposto:
        email_inicial = proposta.email_proposto
    else:
        email_inicial = None
    enviar_proposta_email = FormEnviarPropostaEmail(initial={'email': email_inicial})
    
    # tenta ao máximo auto completar os dados
    # nome
    if not proposta.nome_do_proposto:
        if proposta.cliente:
            proposta.nome_do_proposto = proposta.cliente.nome
        if proposta.precliente:
            proposta.nome_do_proposto = proposta.precliente.nome
    # documento referencia
    if not proposta.documento_do_proposto:
        if proposta.cliente and proposta.cliente.tipo == 'pj':
            proposta.documento_do_proposto = "CNPJ: %s" % proposta.cliente.cnpj
        if proposta.cliente and proposta.cliente.tipo == 'pf':
            proposta.documento_do_proposto = "CPF: %s" % proposta.cliente.cpf
    # rua
    if not proposta.rua_do_proposto and proposta.cliente:
        if proposta.cliente.enderecocliente_set.filter(principal=True):
            proposta.rua_do_proposto = "%s - %s" % (proposta.cliente.enderecocliente_set.filter(principal=True)[0].rua, proposta.cliente.enderecocliente_set.filter(principal=True)[0].numero)
    # bairro
    if not proposta.bairro_do_proposto and proposta.cliente:
        if proposta.cliente.enderecocliente_set.filter(principal=True):
            proposta.bairro_do_proposto = proposta.cliente.enderecocliente_set.filter(principal=True)[0].bairro.nome
    # bairro
    if not proposta.cep_do_proposto  and proposta.cliente:
        if proposta.cliente.enderecocliente_set.filter(principal=True):
            proposta.cep_do_proposto = proposta.cliente.enderecocliente_set.filter(principal=True)[0].cep
    # cidade
    if not proposta.cidade_do_proposto  and proposta.cliente:
        if proposta.cliente.enderecocliente_set.filter(principal=True):
            end = proposta.cliente.enderecocliente_set.filter(principal=True)[0]
            proposta.cidade_do_proposto = "%s - %s" % (end.bairro.cidade.nome, end.bairro.cidade.estado) 
    # endereco da obra proposta
    if not proposta.endereco_obra_proposto and proposta.cliente:
        if proposta.cliente.enderecocliente_set.filter(principal=True):
            end = proposta.cliente.enderecocliente_set.filter(principal=True)[0]
            proposta.endereco_obra_proposto = "Rua %s - %s, Bairro %s, CEP %s, Cidade: %s" % \
            (end.rua, end.numero, end.bairro.nome, end.cep, end.bairro.cidade)
    # telefone
    if not proposta.telefone_contato_proposto:
        if proposta.cliente:
            if proposta.cliente.telefone_fixo and proposta.cliente.telefone_celular:
                proposta.telefone_contato_proposto = "Fixo: %s, Celular: %s" % (proposta.cliente.telefone_fixo, proposta.cliente.telefone_celular) 
            elif proposta.cliente.telefone_fixo and not proposta.cliente.telefone_celular:
                proposta.telefone_contato_proposto = "Fixo: %s" % proposta.cliente.telefone_fixo
            elif not proposta.cliente.telefone_fixo and proposta.cliente.telefone_celular:
                proposta.telefone_contato_proposto = "Celular: %s" % proposta.cliente.telefone_celular
    # email
    if not proposta.email_proposto and proposta.cliente:
        proposta.email_proposto = proposta.cliente.email

    # descricao de itens
    if not proposta.descricao_items_proposto and proposta.orcamentos_ativos():
        proposta.descricao_items_proposto = proposta.texto_descricao_items()
    
    proposta.save()
    modelos_proposta = getattr(settings, 'MODELOS_DE_PROPOSTAS')
    dicionario_template_propostas = getattr(settings, 'DICIONARIO_DE_LOCAL_DE_PROPOSTA')
    form_configura = ConfigurarPropostaComercialParaImpressao(instance=proposta, modelos=modelos_proposta)
    if request.POST:
        form_configura = ConfigurarPropostaComercialParaImpressao(request.POST, instance=proposta, modelos=modelos_proposta)
        if form_configura.is_valid():
            proposta = form_configura.save()
            template_escolhido_chave = form_configura.cleaned_data['modelo']
            template_escolhido = dicionario_template_propostas[template_escolhido_chave]
            # com tudo configurado, gera a proposta
            from io import BytesIO
            
            # nome do arquivo
            nome_arquivo_gerado = "proposta-%s-%s.pdf" % (proposta.id, template_escolhido_chave)
            
            # Create the HttpResponse object with the appropriate PDF headers.
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="%s"' % nome_arquivo_gerado
            buffer = BytesIO()
            report = OrcamentoPrint(buffer, 'Letter')
            pdf = report.print_proposta(proposta, tipo=template_escolhido_chave, perfil=request.user.perfilacessocomercial)
            response.write(pdf)
            if request.POST.get('enviar-por-email'):
                f = forms.EmailField()
                emails = request.POST.get('email').replace(' ', '')
                dest = []
                for email in emails.split(','):
                    try:
                        email_valido = f.clean(email)
                        dest.append(email_valido)
                    except:
                        pass
                messages.info(request, "%s" % dest)
                assunto = "[%s] - Proposta Comercial" % getattr(settings, "NOME_EMPRESA", "NOME DA EMPRESA")
                conteudo = "Segue anexo a Proposta Comercial"
                email = EmailMessage(
                        assunto,
                        conteudo,
                        settings.DEFAULT_FROM_EMAIL,
                        dest,
                    )
                email.attach(nome_arquivo_gerado, pdf, 'application/pdf')
                try:
                    email.send(fail_silently=False)
                    messages.success(request, u'Sucesso! Proposta enviada com sucesso.')
                except:
                    messages.error(request, u'Atenção! Não foi enviado uma mensagem por email para os Gerentes!')
                
                return redirect(reverse("comercial:propostas_comerciais_minhas"))
            else:
                return response
            # descobre o template
            return render_to_response(template_escolhido, locals(), context_instance=RequestContext(request),)
    return render_to_response('frontend/comercial/comercial-configurar-proposta-para-imprimir.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial)
def adicionar_follow_up(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, status="aberta", pk=proposta_id)
    if request.POST:
        form_adicionar_follow_up = FormAdicionarFollowUp(request.POST)
        if form_adicionar_follow_up.is_valid():
            follow_up = form_adicionar_follow_up.save(commit=False)
            follow_up.criado_por = request.user.funcionario
            follow_up.save()
            messages.success(request, u"Sucesso! Novo Follow Up Adicionado na proposta")
        else:
            if request.POST.get('somente-texto'):
                proposta.followupdepropostacomercial_set.create(texto=request.POST.get('texto'), criado_por=request.user.funcionario)
                messages.info(request, u"Follow UP SOMENTE TEXTO adicionado à proposta #%s" % proposta.id)
                
            else:
                messages.error(request, u"Erro! Formulário inválido! Follow Up Não Adicionado.")
    # retorna para referrer ou view do cliente
    try:
        url = request.META['HTTP_REFERER']
    except:
        if proposta.cliente:
            url = reverse("comercial:cliente_ver", args=[proposta.cliente.id])
        else:
            url = reverse("comercial:propostas_comerciais_minhas")
    
    return(redirect(url))

@user_passes_test(possui_perfil_acesso_comercial)
def contratos_meus(request):
    if request.user.perfilacessocomercial.gerente:
        meus_contratos = ContratoFechado.objects.all().order_by('responsavel')
    else:
        meus_contratos = ContratoFechado.objects.filter(responsavel=request.user.funcionario).order_by('status')
    return render_to_response('frontend/comercial/comercial-contratos-meus.html', locals(), context_instance=RequestContext(request),)

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.pdfgen import canvas
 
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
 
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
 
    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
 
    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(211 * mm, 15 * mm + (0.2 * inch),
                             u"Página %d de %d" % (self._pageNumber, page_count))
 
 
 
class ContratoPrint:
    """ 
    Imprime o contrato impresso.
    """

    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
    
    def _header_footer(self, canvas, doc):
            # Save the state of our canvas so we can draw on it
            canvas.saveState()
            styles = getSampleStyleSheet()
 
            # Footer
            footer = Paragraph('<Br /><br/>POP CO 001-F01<br />REV-001', styles['Normal'])
            footer.wrap(doc.width, doc.bottomMargin)
            footer.drawOn(canvas, 10, 10)
            # Release the canvas
            canvas.restoreState()
    
    def print_contrato(self, contrato, testemunha1=None, testemunha2=None, imprime_logo=False):
            
        
            buffer = self.buffer
            
            if imprime_logo:
                margem_topo = 10
            else:
                margem_topo = 70
                
            
            doc = SimpleDocTemplate(buffer,
                                    rightMargin=40,
                                    leftMargin=40,
                                    topMargin=margem_topo,
                                    bottomMargin=70,
                                    pagesize=self.pagesize)
            
            # A large collection of style sheets pre-made for us
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='centered_h1', alignment=TA_CENTER, fontSize=15, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))
            styles.add(ParagraphStyle(name='left_h1', alignment=TA_LEFT, fontSize=15, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left_h2', alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='right', alignment=TA_RIGHT, fontSize=10))
            styles.add(ParagraphStyle(name='right_h2', alignment=TA_RIGHT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='justify', alignment=TA_JUSTIFY))
            
            # Our container for 'Flowable' objects
            elements = []
            
            # logo empresa
            im = Image(getattr(settings, 'IMG_PATH_LOGO_EMPRESA'),)
            im.hAlign = 'LEFT'
            
            # id do contrato
            id_contrato = Paragraph("Nº CONTRATO: %s" % str(contrato.id), styles['right'])
            
            if imprime_logo:
                data=[(im,id_contrato)]
                table = Table(data, colWidths=270, rowHeights=79)
            else:
                data=[('',id_contrato)]
                table = Table(data, colWidths=270, rowHeights=20)

            table.setStyle(TableStyle([('VALIGN',(-1,-1),(-1,-1),'BOTTOM')]))
            elements.append(table)
            

            
            # descricao
            id_contrato_p = Paragraph("CONTRATO DE PRESTAÇÃO DE SERVIÇOS.", styles['centered_h1'])
            elements.append(id_contrato_p)
            
            # space
            elements.append(Spacer(1, 20))
            
            # CONTRATANTE DESC
            contratante_text = contrato.sugerir_texto_contratante()
            contratante_p = Paragraph("<b>CONTRATANTE</b>: %s" % contratante_text, styles['justify'])
            elements.append(contratante_p)
            
            # space
            elements.append(Spacer(1, 12))
            
            # CONTRATADA DESC
            contratada_texto = getattr(settings, "TEXTO_CONTRATO_CONTRATADA", "Settings: TEXTO_CONTRATO_CONTRATADA - Texto descrevendo a empresa")
            contratada_p = Paragraph("<b>CONTRATADA</b>: %s" % contratada_texto, styles['justify'])
            elements.append(contratada_p)
            
            # space
            elements.append(Spacer(1, 12))
            #
            # CLAUSULA 1 - DO OBJETO
            #
            clausula_1_p = Paragraph("CLÁSULA 1ª – DO OBJETO", styles['left_h1'])
            elements.append(clausula_1_p)
            # space
            elements.append(Spacer(1, 12))
            
            objeto_p = Paragraph(unicode(contrato.objeto).replace("\n", "<br />"), styles['justify'])
            elements.append(objeto_p)
            # space
            elements.append(Spacer(1, 5))
            # itens incluso titulo
            itens_incluso_titulo_p = Paragraph(u". Itens inclusos:", styles['left_h2'])
            elements.append(itens_incluso_titulo_p)
            # itens incluso texto
            itens_inclusos_p = Paragraph(unicode(contrato.items_incluso).replace("\n", "<br />"), styles['justify'])
            elements.append(itens_inclusos_p)
            # space
            elements.append(Spacer(1, 5))
            # itens N incluso titulo
            itens_n_incluso_titulo_p = Paragraph(". Itens não inclusos:", styles['left_h2'])
            elements.append(itens_n_incluso_titulo_p)
            # itens N incluso texto
            itens_n_inclusos_p = Paragraph(unicode(contrato.items_nao_incluso).replace("\n", "<br />"), styles['justify'])
            elements.append(itens_n_inclusos_p)
            
            # space
            elements.append(Spacer(1, 5))
            
            #
            # CLAUSULA 2 - NORMAS DE EXECUÇÃO
            #
            clausula_2_p = Paragraph("CLÁUSULA 2ª - NORMAS DE EXECUÇÃO", styles['left_h1'])
            elements.append(clausula_2_p)
            # space
            elements.append(Spacer(1, 12))
            
            normas_execucao_texto = getattr(settings, "TEXTO_NORMAS_EXECUCAO", "Settings: TEXTO_NORMAS_EXECUCAO - Texto descrevendo as normas de execução do contrato")    
            normas_execucao_p = Paragraph(str(normas_execucao_texto).replace("\n", "<br />"), styles['justify'])
            elements.append(normas_execucao_p)
            
            #
            # CLAUSULA 3 - FORMAS DE PAGAMENTO
            #
            clausula_3_p = Paragraph("CLÁUSULA 3ª – DO VALOR E FORMA DE PAGAMENTO", styles['left_h1'])
            elements.append(clausula_3_p)
            # space
            elements.append(Spacer(1, 12))
            forma_pagamento_p = Paragraph(unicode(contrato.propostacomercial.forma_pagamento_proposto).replace("\n", "<br />"), styles['justify'])
            elements.append(forma_pagamento_p)
            elements.append(Spacer(1, 12))

            for lancamento in contrato.lancamentofinanceiroreceber_set.all():
                lancamento_text = "<b>Parcela %s</b> de R$ %s no dia %s na forma de %s" % (lancamento.peso, lancamento.valor_cobrado, lancamento.data_cobranca.strftime("%d/%m/%y"), lancamento.get_modo_recebido_display())
                lancamento_p = Paragraph(unicode(lancamento_text).replace("\n", "<br />"), styles['justify'])
                elements.append(lancamento_p)
                elements.append(Spacer(1, 12))
            
            import locale
            locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")
            valor_formatado = locale.currency(contrato.valor, grouping=True)
            
            total_texto = "Total: %s" % valor_formatado
            total_p = Paragraph(unicode(total_texto).replace("\n", "<br />"), styles['left_h2'])
            elements.append(total_p)
            elements.append(Spacer(1, 12))
            
                
            #
            # CLÁUSULA 4ª – DOS PRAZOS
            #
            clausula_4_p = Paragraph("CLÁUSULA 4ª – DOS PRAZOS", styles['left_h1'])
            elements.append(clausula_4_p)
            # space
            elements.append(Spacer(1, 12))
            
            prazos_texto = getattr(settings, "TEXTO_HTML_PRAZOS", "Settings: TEXTO_HTML_PRAZOS - Texto descrevendo as normas de execução do contrato")    
            prazos_p = Paragraph(str(prazos_texto).replace("\n", "<br />"), styles['justify'])
            elements.append(prazos_p)
            elements.append(Spacer(1, 12))

            #
            #
            #  CLÁUSULA 5ª – DA RESCISÃO
            #
            clausula_5_p = Paragraph("CLÁUSULA 5ª – DA RESCISÃO", styles['left_h1'])
            elements.append(clausula_5_p)
            # space
            elements.append(Spacer(1, 12))
            # 
            rescisao_texto = getattr(settings, "TEXTO_HTML_RESCISAO", "Settings: TEXTO_HTML_RESCISAO - Texto descrevendo as normas de Execucao")    
            rescisao_p = Paragraph(str(rescisao_texto).replace("\n", "<br />"), styles['justify'])
            elements.append(rescisao_p)
            
            
            elements.append(Spacer(1, 12))
            #
            #
            #  CLÁUSULA 6ª – DA GARANTIA
            #
            clausula_6_p = Paragraph(u"CLÁUSULA 6ª – DA GARANTIA", styles['left_h1'])
            elements.append(clausula_6_p)
            elements.append(Spacer(1, 12))
            # space
            # 
            garantia_p = Paragraph(unicode(contrato.garantia).replace("\n", "<br />"), styles['justify'])
            elements.append(garantia_p)
            elements.append(Spacer(1, 12))
            
            #
            #
            #  CLÁUSULA 7ª – DO FORO
            #
            clausula_6_p = Paragraph(u"CLÁUSULA 7ª – DO FORO", styles['left_h1'])
            elements.append(clausula_6_p)
            # space
            # 
            foro_texto = getattr(settings, "TEXTO_HTML_FORO", "Settings: TEXTO_HTML_FORO - Texto descrevendo O FORO do contrato")    
            foro_p = Paragraph(str(foro_texto).replace("\n", "<br />"), styles['justify'])
            elements.append(foro_p)
            elements.append(Spacer(1, 12))
            
            ## cidade do contrato
            elements.append(Spacer(1, 12))
            cidade = getattr(settings, "CIDADE_CONTRATO", "Settings: CIDADE_CONTRATO - Texto descrevendo A Cidade do Contrato")
            cidade_texto = "%s, %s" % (cidade, datetime.date.today().strftime("%d de %B de %Y"))
            cidade_p = Paragraph(str(cidade_texto).replace("\n", "<br />"), styles['right'])
            elements.append(cidade_p)
            
            
            espaco_assinaturas = 30
            
            # REPRESENTANTE LEGAL EMPRESA
            #
            elements.append(Spacer(1, espaco_assinaturas))
            representante_linha = Paragraph(str("_"*500), styles['justify'])
            elements.append(representante_linha)
            representante_empresa = getattr(settings, "REPRESENTATE_LEGAL_EMPRESA", "Settings: REPRESENTATE_LEGAL_EMPRESA - Texto descrevendo Representante Legal da Empresa")    
            representante_p = Paragraph(str(representante_empresa), styles['left'])
            elements.append(representante_p)
            
            # CLIENTE / PROPOSTO LEGAL
            #
            elements.append(Spacer(1, espaco_assinaturas))
            cliente_linha = Paragraph(str("_"*500), styles['justify'])
            elements.append(cliente_linha)
            representante_p = Paragraph(unicode(contrato.sugerir_texto_contratante()), styles['left'])
            elements.append(representante_p)
            
            # TESTEMUNHA 1
            #
            elements.append(Spacer(1, espaco_assinaturas))
            testemunha_linha = Paragraph(str("_"*500), styles['justify'])
            elements.append(testemunha_linha)
            if testemunha1:
                texto = "TESTEMUNHA 1, Nome: %s, CPF: %s" % (testemunha1, testemunha1.cpf)
            else:                
                if contrato.responsavel_comissionado:
                    texto = "TESTEMUNHA 1, Nome: %s, CPF: %s" % (contrato.responsavel_comissionado, contrato.responsavel_comissionado.cpf)
                else:
                    texto = "TESTEMUNHA 1"
            testemunha_texto = Paragraph(unicode(texto), styles['left'])
            elements.append(testemunha_texto)
            
            # TESTEMUNHA 2
            #
            elements.append(Spacer(1, espaco_assinaturas))
            testemunha_linha = Paragraph(str("_"*500), styles['justify'])
            elements.append(testemunha_linha)
            if testemunha2:
                texto = "TESTEMUNHA 2, Nome: %s, CPF: %s" % (testemunha2, testemunha2.cpf)
            else:                
                texto = "TESTEMUNHA 2"
            testemunha_texto = Paragraph(unicode(texto), styles['left'])
            elements.append(testemunha_texto)
            # build pdf
            doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer, canvasmaker=NumberedCanvas)
 
            # Get the value of the BytesIO buffer and write it to the response.
            pdf = buffer.getvalue()
            buffer.close()
            return pdf


@user_passes_test(possui_perfil_acesso_comercial)
def contratos_gerar_impressao(request, contrato_id):
    if request.user.perfilacessocomercial.gerente:
        contrato = get_object_or_404(ContratoFechado, pk=contrato_id)
    else:
        contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status__in=["assinatura", "emaberto"])
    from io import BytesIO
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="CONTRATO-%s.pdf"' % contrato.id

    buffer = BytesIO()

    report = ContratoPrint(buffer, 'Letter')
    if request.GET.get('testemunha1'):
        testemunha1 = Funcionario.objects.get(pk=int(request.GET.get('testemunha1')))
    else:
        testemunha1 = None
    if request.GET.get('testemunha2'):
        testemunha2 = Funcionario.objects.get(pk=int(request.GET.get('testemunha2')))
    else:
        testemunha2 = None
    imprime_logo = request.GET.get('imprime_logo')
    pdf = report.print_contrato(contrato, testemunha1=testemunha1, testemunha2=testemunha2, imprime_logo=imprime_logo)
    response.write(pdf)
    return response
    
    
    texto_contratada = getattr(settings, "TEXTO_CONTRATO_CONTRATADA", "Texto descrevendo a empresa")
    texto_normas_execucao = getattr(settings, "TEXTO_NORMAS_EXECUCAO", "Texto descrevendo as normas de execução do contrato")    
    texto_juros_valor_contrato = getattr(settings, "TEXTO_CONTRATO_JUROS_VALORES", "Texto descrevendo a forma de juros e multas regidos por este contrato")    
    texto_contrato_dos_prazos = getattr(settings, "TEXTO_HTML_PRAZOS", "Texto descrevendo as informações sobre Prazos")
    texto_contrato_rescisao = getattr(settings, "TEXTO_HTML_RESCISAO", "Texto descrevendo as informações sobre Rescisão")
    texto_contrato_foro = getattr(settings, "TEXTO_HTML_FORO", "Texto descrevendo as informações sobre o Foro")
    nome_empresa = getattr(settings, 'NOME_EMPRESA', 'Mestria')
    
    return render_to_response('frontend/comercial/comercial-contratos-gerar-impressao.html', locals(), context_instance=RequestContext(request),)

class FormRevalidarContrato(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormRevalidarContrato, self).__init__(*args, **kwargs)
        self.fields['valor'].localize = True
        self.fields['valor'].widget.is_localized = True
    
    class Meta:
        model = ContratoFechado
        fields = 'categoria', 'objeto', 'garantia', 'items_incluso', 'items_nao_incluso', 'valor', 'tipo',
        localized_fields = 'valor',


@user_passes_test(possui_perfil_acesso_comercial)
def contratos_meus_definir_assinado(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status="assinatura")
    contrato.status = "emaberto"
    contrato.save()
    return redirect(reverse("comercial:contratos_meus"))
    
@user_passes_test(possui_perfil_acesso_comercial)
def contratos_meus_revalidar(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status="invalido")
    ConfigurarConversaoPropostaFormset = forms.models.inlineformset_factory(ContratoFechado, LancamentoFinanceiroReceber, extra=0, can_delete=True, form=LancamentoFinanceiroReceberComercialForm)
    if request.POST:
        form_contrato = FormRevalidarContrato(request.POST, instance=contrato)
        form_configurar_contrato = ConfigurarConversaoPropostaFormset(request.POST, prefix="revalidar_contrato", instance=contrato)
        if form_contrato.is_valid() and form_configurar_contrato.is_valid():
            total_lancamentos = 0
            for form in form_configurar_contrato.forms:
                if form.cleaned_data:
                    total_lancamentos += float(form.cleaned_data['valor_cobrado'])
            if float(total_lancamentos) == float(contrato.valor):
                contrato = form_contrato.save(commit=False)
                contrato.status = "emanalise"
                contrato.save()
                form_configurar_contrato.save()
                messages.success(request, u"Sucesso! Contrato Revalidado")
                # envia email para gerentes do comercial
                dest = []
                for perfil in PerfilAcessoComercial.objects.filter(gerente=True):
                    dest.append(perfil.user.funcionario.email or perfil.user.email)

                assunto = u'Contrato para Análise: #%s' % contrato.id
                
                current_site_domain = Site.objects.get_current().domain
                template = loader.get_template('template_de_email/comercial/novo-contrato-em-analise.html')
                c = Context(
                        {
                            "contrato": contrato,
                            "current_site_domain": current_site_domain
                        }
                    )
                conteudo = template.render(c)
                email = EmailMessage(
                        assunto, 
                        conteudo,
                        'SISTEMA',
                        dest,
                    )
                try:
                    email.send(fail_silently=False)
                    messages.success(request, u'Sucesso! Uma mensagem de email foi enviado para os Gerentes!')
                except:
                    messages.error(request, u'Atenção! Não foi enviado uma mensagem por email para os Gerentes!')
                
                return redirect(reverse("comercial:contratos_meus"))
            else:
                messages.error(request, u"Erro. Valor de Lançamentos não confere com o valor do contrato.")
            
    else:
        form_contrato = FormRevalidarContrato(instance=contrato)
        form_configurar_contrato = ConfigurarConversaoPropostaFormset(prefix="revalidar_contrato", instance=contrato)

    return render_to_response('frontend/comercial/comercial-contratos-meus-revalidar.html', locals(), context_instance=RequestContext(request),)


class FormAdicionaModelo(forms.ModelForm):
    
    class Meta:
        model = Orcamento
        fields = 'descricao',

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo_novo(request):
    if request.POST:
        form_adicionar_modelo = FormAdicionaModelo(request.POST)
        if form_adicionar_modelo.is_valid():
            novo_modelo = form_adicionar_modelo.save(commit=False)
            novo_modelo.modelo = True
            novo_modelo.criado_por = request.user.funcionario
            novo_modelo.save()
            return redirect(reverse("comercial:orcamentos_modelo_editar", args=[novo_modelo.id]))
    else:
        form_adicionar_modelo = FormAdicionaModelo()
    return render_to_response('frontend/comercial/comercial-orcamentos-modelo-novo.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo(request):
    modelos = Orcamento.objects.filter(ativo=True, modelo=True)
    return render_to_response('frontend/comercial/comercial-orcamentos-modelo.html', locals(), context_instance=RequestContext(request),)

class OrcamentoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(OrcamentoForm, self).__init__(*args, **kwargs)
        self.fields['proposta'].widget = forms.HiddenInput()
        self.fields['descricao'].widget.attrs['class'] = "input-xxlarge"
        self.fields['descricao'].required = True

    class Meta:
        model = Orcamento
        fields = 'descricao', 'proposta'

class LinhaOrcamentoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LinhaOrcamentoForm, self).__init__(*args, **kwargs)
        self.fields['produto'].widget = forms.HiddenInput()
        self.fields['produto'].widget.attrs['class'] = 'select2-ajax'
        self.fields['quantidade'].widget.attrs['class'] = 'recalcula_quantidade_quando_muda'

    class Meta:
        model = LinhaRecursoMaterial
        fields = 'quantidade', 'produto'

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo_editar(request, modelo_id):
    modelo = get_object_or_404(Orcamento, modelo=True, pk=modelo_id)
    OrcamentoFormSet = forms.models.inlineformset_factory(Orcamento, LinhaRecursoMaterial, extra=0, can_delete=True, form=LinhaOrcamentoForm)
    if request.POST:
        if 'adicionar_linha_material' in request.POST:
            messages.info(request, u"Nova Linha de Materiais adicionados")
            cp = request.POST.copy()
            cp['modelo-TOTAL_FORMS'] = int(cp['modelo-TOTAL_FORMS'])+ 1
            form_editar_linhas = OrcamentoFormSet(cp, instance=modelo, prefix='modelo')
            form_modelo = OrcamentoForm(cp, instance=modelo)
        else:
            form_editar_linhas = OrcamentoFormSet(request.POST, instance=modelo, prefix="modelo")
            form_modelo = OrcamentoForm(request.POST, instance=modelo)
            if form_editar_linhas.is_valid() and form_modelo.is_valid():
                modelo_linhas = form_editar_linhas.save()
                modelo = form_modelo.save()
                messages.success(request, u"Sucesso! Modelo Alterado")
                # volta pra lista de modelos
                return redirect(reverse('comercial:orcamentos_modelo'))
    else:
        form_editar_linhas = OrcamentoFormSet(instance=modelo, prefix="modelo")
        form_modelo = OrcamentoForm(instance=modelo)
    return render_to_response('frontend/comercial/comercial-orcamentos-modelo-editar.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo_reajustar(request, modelo_id):
    modelo = get_object_or_404(Orcamento, modelo=True, pk=modelo_id)
    modelo.reajusta_custo()
    messages.success(request, u"Sucesso! Preço de Modelo %s Reajustado." % modelo)
    return redirect(reverse("comercial:orcamentos_modelo"))

class SelecionaAnoIndicadorComercial(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(SelecionaAnoIndicadorComercial, self).__init__(*args, **kwargs)
        anos = PropostaComercial.objects.dates('criado', 'year', order='DESC')
        anos_choice = [(str(a.year), str(a.year)) for a in anos]
        if (str(datetime.date.today().year), str(datetime.date.today().year)) not in anos_choice:
            anos_choice.append((datetime.date.today().year, datetime.date.today().year))
        self.fields['ano'].choices = anos_choice
        self.fields['ano'].widget.attrs['class'] = 'input-small'

    ano = forms.ChoiceField()

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def indicadores_do_comercial(request):
    try:
        ano = request.GET.get('ano', datetime.date.today().year)
        ano = int(ano)
    except:
        raise
        ano = datetime.date.today().year
    
    # pre clientes criados
    total_preclientes_criados = []
    # pre clientes convertidos
    total_preclientes_convertidos = []
    # propostas criadas
    total_propostas_criadas = []
    # propostas convertidas
    total_propostas_convertidas = []
    # propostas fechadas
    total_propostas_perdidas = []
    
    for month in range(1,13):
        # preclientes criados
        preclientes_no_mes = PreCliente.objects.filter(criado__year=ano, criado__month=month).count()
        total_preclientes_criados.append(preclientes_no_mes)
        # preclientes convertidos
        preclientes_covnertidos_no_mes = PreCliente.objects.filter(data_convertido__year=ano, data_convertido__month=month).count()
        total_preclientes_convertidos.append(preclientes_covnertidos_no_mes)
        # propostas criadas
        propostas_criadas_mes = PropostaComercial.objects.filter(criado__year=ano, criado__month=month)
        contagem_propostas_criadas_mes = propostas_criadas_mes.count()
        valores_propostas_criadas_mes = propostas_criadas_mes.aggregate(Sum('valor_proposto'))['valor_proposto__sum'] or 0
        total_propostas_criadas.append((contagem_propostas_criadas_mes, valores_propostas_criadas_mes))
        # propostas convertidas
        propostas_convertidas_mes = PropostaComercial.objects.filter(definido_convertido_em__year=ano, definido_convertido_em__month=month)
        contagem_propostas_convertidas_mes = propostas_convertidas_mes.count()
        valores_propostas_convertidas_mes = propostas_convertidas_mes.aggregate(Sum('valor_proposto'))['valor_proposto__sum'] or 0
        total_propostas_convertidas.append((contagem_propostas_convertidas_mes, valores_propostas_convertidas_mes))
        # propostas perdidas
        propostas_perdidas_mes = PropostaComercial.objects.filter(definido_perdido_em__year=ano, definido_perdido_em__month=month)
        contagem_propostas_criadas_mes = propostas_perdidas_mes.count()
        valores_propostas_criadas_mes = propostas_perdidas_mes.aggregate(Sum('valor_proposto'))['valor_proposto__sum'] or 0
        total_propostas_perdidas.append((contagem_propostas_criadas_mes, valores_propostas_criadas_mes))
        
    # propostas abertas não expiradas
    propostas_abertas_nao_expiradas = PropostaComercial.objects.filter(status="aberta", data_expiracao__gte=datetime.date.today())
    propostas_abertas_nao_expiradas_contagem = propostas_abertas_nao_expiradas.count()
    propostas_abertas_nao_expiradas_por_criador = propostas_abertas_nao_expiradas.values('criado_por__nome').annotate(Count('id'), Sum('valor_proposto'))
    propostas_abertas_nao_expiradas_por_responsavel = propostas_abertas_nao_expiradas.values('designado__nome').annotate(Count('id'), Sum('valor_proposto'))
    propostas_abertas_nao_expiradas_total = propostas_abertas_nao_expiradas.aggregate(Sum('valor_proposto'))['valor_proposto__sum']    

    # propostas abertas expiradas
    propostas_abertas_expiradas = PropostaComercial.objects.filter(status="aberta", data_expiracao__lt=datetime.date.today())
    propostas_abertas_expiradas_contagem = propostas_abertas_expiradas.count()
    propostas_abertas_expiradas_por_criador = propostas_abertas_expiradas.values('criado_por__nome').annotate(Count('id'), Sum('valor_proposto'))
    propostas_abertas_expiradas_por_responsavel = propostas_abertas_expiradas.values('designado__nome').annotate(Count('id'), Sum('valor_proposto'))
    propostas_abertas_expiradas_total = propostas_abertas_expiradas.aggregate(Sum('valor_proposto'))['valor_proposto__sum']
    
    # Grupo Indicador de Produtos em Propostas Convertidas
    total_grupo_indicadores_propostas_convertidas = {}
    for grupo in GrupoIndicadorDeProdutoProposto.objects.all():
        grupo_month_set = []
        for month in range(1,13):
            quantidades = LinhaRecursoMaterial.objects.filter(
                orcamento__ativo=True,
                orcamento__proposta__status="convertida",
                orcamento__proposta__definido_convertido_em__year=ano,
                orcamento__proposta__definido_convertido_em__month=month,
                produto__grupo_indicador=grupo
            ).aggregate(Sum('quantidade'))
            grupo_month_set.append(quantidades['quantidade__sum'] or 0)
        total_grupo_indicadores_propostas_convertidas[grupo.nome] = grupo_month_set
    
    total_grupo_indicadores_propostas_convertidas = OrderedDict(sorted(total_grupo_indicadores_propostas_convertidas.items(), key=lambda t: t[0]))

    # Grupo Indicador de Produtos em Propostas Perdidas
    total_grupo_indicadores_propostas_perdidas = {}
    for grupo in GrupoIndicadorDeProdutoProposto.objects.all():
        grupo_month_set = []
        for month in range(1,13):
            quantidades = LinhaRecursoMaterial.objects.filter(
                orcamento__ativo=True,
                orcamento__proposta__status="perdida",
                orcamento__proposta__definido_perdido_em__year=ano,
                orcamento__proposta__definido_perdido_em__month=month,
                produto__grupo_indicador=grupo
            ).aggregate(Sum('quantidade'))
            grupo_month_set.append(quantidades['quantidade__sum'] or 0)
        total_grupo_indicadores_propostas_perdidas[grupo.nome] = grupo_month_set
    total_grupo_indicadores_propostas_perdidas = OrderedDict(sorted(total_grupo_indicadores_propostas_perdidas.items(), key=lambda t: t[0]))


    form_seleciona_ano = SelecionaAnoIndicadorComercial(initial={'ano': ano})
    resultados = True
    ano = str(ano)
        
    # Grupo de Indicador com Propostas Abertas Não Expiradas
    grupos_indicadores_produtos_orcamento_aberto_nao_expirado = LinhaRecursoMaterial.objects.filter(orcamento__proposta__status="aberta", orcamento__proposta__data_expiracao__gte=datetime.date.today()).exclude(produto__grupo_indicador=None).values('produto__grupo_indicador__nome').annotate(Sum('quantidade'))

    # Grupo de Indicador com Propostas Abertas Expiradas
    grupos_indicadores_produtos_orcamento_aberto_expirado = LinhaRecursoMaterial.objects.filter(orcamento__proposta__status="aberta", orcamento__proposta__data_expiracao__lt=datetime.date.today()).exclude(produto__grupo_indicador=None).values('produto__grupo_indicador__nome').annotate(Sum('quantidade'))
    
    # SubGrupo de Indicador com Propostas ABertas Não expiradas
    sub_grupos_indicadores_produtos_orcamento_aberto_nao_expirado = LinhaRecursoMaterial.objects.filter(orcamento__proposta__status="aberta", orcamento__proposta__data_expiracao__gte=datetime.date.today()).exclude(produto__sub_grupo_indicador=None).values('produto__sub_grupo_indicador__nome', 'produto__sub_grupo_indicador__grupo__nome').annotate(Sum('quantidade'))
    
    # SubGrupo de Indicador com Propostas ABertas Expiradas
    sub_grupos_indicadores_produtos_orcamento_aberto_expirado = LinhaRecursoMaterial.objects.filter(orcamento__proposta__status="aberta", orcamento__proposta__data_expiracao__lt=datetime.date.today()).exclude(produto__sub_grupo_indicador=None).values('produto__sub_grupo_indicador__nome', 'produto__sub_grupo_indicador__grupo__nome').annotate(Sum('quantidade'))
    
    
    return render_to_response('frontend/comercial/comercial-indicadores.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial(request):
    return render_to_response('frontend/comercial/comercial-relatorios.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial_probabilidade(request):
    try:
        probabilidade = int(request.GET.get('probabilidade'))
    except:
        probabilidade = 70
    agrupador = request.GET.get('agrupador', 'tipo')
    propostas = PropostaComercial.objects.filter(probabilidade__gte=probabilidade, status="aberta")

    if agrupador == "tipo":
        propostas = propostas.order_by('tipo')
    elif agrupador == "funcionario":
        propostas = propostas.order_by('designado')
    
    return render_to_response('frontend/comercial/comercial-relatorios-probabilidade.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial_propostas_e_followups(request):
    try:
        followup_n = int(request.GET.get('followup_n'))
    except:
        followup_n = 0

    agrupador = request.GET.get('agrupador', 'tipo')
    propostas = PropostaComercial.objects.annotate(num_fup=Count('followupdepropostacomercial')).filter(num_fup=followup_n)
    
    if agrupador == "tipo":
        propostas = propostas.order_by('tipo')
    elif agrupador == "funcionario":
        propostas = propostas.order_by('designado')
        
    return render_to_response('frontend/comercial/comercial-relatorios-propostas-followups.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial_propostas_declinadas(request):
    agrupador = request.GET.get('agrupador', 'tipo')
    erro = False
    try:
        de = request.GET.get('de', None)
        if de:
            de = datetime.datetime.strptime(de, '%d/%m/%Y')
        ate = request.GET.get('ate', None)
        if ate:
            ate = datetime.datetime.strptime(ate, '%d/%m/%Y')
        if de and ate and ate < de:
            raise
    except:
        messages.error(request, "Intervalo de datas errado")
        erro = True
    if not erro:
        if de and ate:
            propostas = PropostaComercial.objects.filter(definido_perdido_em__range=(de,ate), status__in=['perdida', 'perdida_aguardando'])
        elif de and not ate:
            de = datetime.datetime.combine(de, datetime.time(00, 00))
            propostas = PropostaComercial.objects.filter(definido_perdido_em__gte=de, status__in=['perdida', 'perdida_aguardando'])
        elif not de and ate:
            ate = datetime.datetime.combine(ate, datetime.time(23, 59))
            propostas = PropostaComercial.objects.filter(definido_perdido_em__lte=ate, status__in=['perdida', 'perdida_aguardando'])
        else:
            propostas = PropostaComercial.objects.filter(status__in=['perdida', 'perdida_aguardando'])
        
        if agrupador == "tipo":
            propostas = propostas.order_by('tipo')
        elif agrupador == "funcionario":
            propostas = propostas.order_by('designado')
        
    
            
    return render_to_response('frontend/comercial/comercial-relatorios-propostas-declinadas.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def analise_de_contratos(request):
    contratos_em_analise = ContratoFechado.objects.filter(status="emanalise")
    return render_to_response('frontend/comercial/comercial-analise-de-contratos.html', locals(), context_instance=RequestContext(request),)

class FormAnalisarContrato(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormAnalisarContrato, self).__init__(*args, **kwargs)
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        self.fields['responsavel_comissionado'].queryset = Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis)
        self.fields['responsavel_comissionado'].widget.attrs['class'] = 'select2'
        self.fields['responsavel'].widget.attrs['class'] = 'select2'
        self.fields['responsavel'].queryset = Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis)

    class Meta:
        model = ContratoFechado
        fields = ('objeto', 'categoria', 'responsavel_comissionado', 'responsavel', 'nome_proposto_legal', 'documento_proposto_legal', 'apoio_tecnico')

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def analise_de_contratos_analisar(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status="emanalise")
    if request.POST:
        form_analisar_contrato = FormAnalisarContrato(request.POST, instance=contrato)
        if form_analisar_contrato.is_valid():
            contrato = form_analisar_contrato.save()
            if request.POST.get('aterar-contrato'):
                messages.success(request, u"Sucesso! Contrato em Análise Alterado.")
            elif request.POST.get('contrato-invalido'):
                contrato.status ="invalido"
                contrato.motivo_invalido = request.POST.get('motivo-invalido')
                contrato.save()
                messages.success(request, u"Sucesso! Contrato Analisado. Definido como Inválido")
                
            elif request.POST.get('contrato-valido'):
                contrato.status = "assinatura"
                contrato.data_validacao = datetime.datetime.now()
                contrato.funcionario_validador = request.user.funcionario
                contrato.save()
                messages.success(request, u"Sucesso! Contrato Analisado. Definido como Aguardando Assinatura")
            return redirect(reverse("comercial:analise_de_contratos"))
    else:
        form_analisar_contrato = FormAnalisarContrato(instance=contrato)
    return render_to_response('frontend/comercial/comercial-analise-de-contratos-analisar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def gerencia_comissoes(request):
    fechamentos_com_lancamentos_abertos = FechamentoDeComissao.objects.filter(lancamentodefechamentocomissao__pago=False)
    fechamentos_sem_lancamentos = FechamentoDeComissao.objects.filter(lancamentodefechamentocomissao=None)
    return render_to_response('frontend/comercial/comercial-gerencia-comissoes.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def gerencia_comissoes_novo_fechamento(request):
    if request.POST:
        # cria fechamento com os contratos selecionados
        ids_contratos = request.POST.getlist('contrato-id')
        contratos_selecionados = ContratoFechado.objects.filter(id__in=ids_contratos)
        id_comissionado = request.POST.get('funcionario-comissionado')
        funcionario_comissionado = Funcionario.objects.get(pk=id_comissionado)
        novo_fechamento = FechamentoDeComissao.objects.create(
            comissionado = funcionario_comissionado,
        )
        novo_fechamento.contratos.add(*contratos_selecionados)
        novo_fechamento.save()
    contratos_abertos = ContratoFechado.objects.filter(fechamentodecomissao=None).exclude(responsavel_comissionado=None)
    return render_to_response('frontend/comercial/comercial-gerencia-comissoes-novo-fechamento.html', locals(), context_instance=RequestContext(request),)
