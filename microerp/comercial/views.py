# -*- coding: utf-8 -*-
import datetime
import operator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q

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
from comercial.models import PropostaComercial, PerfilAcessoComercial, FollowUpDePropostaComercial, RequisicaoDeProposta
from estoque.models import Produto

from django.conf import settings

from rh import utils

from django.http import HttpResponse

#
# FORMULARIOS
#

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
        
    class Meta:
        model = PreCliente
        fields = 'nome', 'contato', 'dados', 'designado'


class AdicionarPropostaForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AdicionarPropostaForm, self).__init__(*args, **kwargs)
        self.fields['data_expiracao'].widget.attrs['class'] = 'datepicker'
    
    class Meta:
        model = PropostaComercial
        fields = 'status', 'probabilidade', 'valor_proposto', 'data_expiracao', 'observacoes'

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
        return cnpj

    
    def __init__(self, *args, **kwargs):
        precliente = kwargs.pop('precliente')
        super(AdicionarCliente, self).__init__(*args, **kwargs)
        self.fields['tipo'].required = True
        if precliente:
            self.fields['nome'].initial = precliente.nome
            self.fields['observacao'].initial = precliente.dados
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        self.fields['designado'].queryset = Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis)
        
    
    class Meta:
        model = Cliente
        fields = 'nome', 'tipo', 'fantasia', 'cnpj', 'inscricao_estadual', \
        'cpf', 'rg', 'nascimento', 'ramo', 'observacao', 'origem',\
        'contato', 'email', 'telefone_fixo', 'telefone_celular', 'fax',\
        'designado'
        

class FormAdicionarFollowUp(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormAdicionarFollowUp, self).__init__(*args, **kwargs)
        self.fields['proposta'].widget = forms.HiddenInput()

    class Meta:
        model = FollowUpDePropostaComercial
        fields = 'proposta', 'texto',


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
    return render_to_response('frontend/comercial/comercial-home.html', locals(), context_instance=RequestContext(request),)



@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def clientes(request):
    cliente_q = request.GET.get('cliente', False)
    if cliente_q:
        clientes = Cliente.objects.filter(
            Q(nome__icontains=cliente_q) | \
            Q(cnpj__icontains=cliente_q) | \
            Q(cpf__icontains=cliente_q)
        )
        #puxa todos os pre clientes, menos os já convertidos)
        preclientes = PreCliente.objects.filter(nome__icontains=cliente_q, cliente_convertido=None) 
    else:
        clientes = Cliente.objects.all()
        preclientes = PreCliente.objects.filter(cliente_convertido=None)

    preclientes_sem_proposta = PreCliente.objects.filter(propostacomercial=None, cliente_convertido=None)
    clientes_sem_proposta = Cliente.objects.filter(propostacomercial=None)
    requisicoes_propostas = RequisicaoDeProposta.objects.filter(atendido=False)
    # se nao for gerente, limita a listagem para os que lhe sao designados
    if not request.user.perfilacessocomercial.gerente:
        clientes = clientes.filter(designado=request.user.funcionario)
        preclientes = preclientes.filter(designado=request.user.funcionario)
        preclientes_sem_proposta = preclientes_sem_proposta.filter(designado=request.user.funcionario)
        clientes_sem_proposta = clientes_sem_proposta.filter(designado=request.user.funcionario)
        requisicoes_propostas = requisicoes_propostas.filter(cliente__designado=request.user.funcionario)
    
    return render_to_response('frontend/comercial/comercial-clientes.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def cliente_ver(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    cliente_q = request.GET.get('cliente', None)
    if request.POST:
        form_adicionar_follow_up = FormAdicionarFollowUp(request.POST)
        if form_adicionar_follow_up.is_valid():
            follow_up = form_adicionar_follow_up.save(commit=False)
            follow_up.criado_por = request.user
            follow_up.save()
            messages.success(request, u"Sucesso! Novo Follow Up Adicionado")
    else:
        form_adicionar_follow_up = FormAdicionarFollowUp()

    return render_to_response('frontend/comercial/comercial-cliente-ver.html', locals(), context_instance=RequestContext(request),)

class FormEditarProposta(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormEditarProposta, self).__init__(*args, **kwargs)
        self.fields['data_expiracao'].widget.attrs['class'] = 'datepicker'
    
    
    class Meta:
        model = PropostaComercial
        fields = 'probabilidade', 'valor_proposto', 'data_expiracao', 'observacoes'


@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def cliente_editar_proposta(request, cliente_id, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    if request.POST:
        form_editar_proposta = FormEditarProposta(request.POST, instance=proposta)
        if form_editar_proposta.is_valid():
            proposta_alterada = form_editar_proposta.save()
            messages.success(request, u"Sucesso! Proposta #%s alterada!" % proposta.id)
            return redirect(reverse("comercial:cliente_ver", args=[proposta.cliente.id])+"#tab_propostas")
    else:
        form_editar_proposta = FormEditarProposta(instance=proposta)
        
    return render_to_response('frontend/comercial/comercial-cliente-editar-proposta.html', locals(), context_instance=RequestContext(request),)


# Pre Cliente
@user_passes_test(possui_perfil_acesso_comercial)
def precliente_adicionar(request):
    if request.POST:
        try:
            form = form_add_precliente = PreClienteAdicionarForm(data=request.POST, sugestao=None, perfil=request.user.perfilacessocomercial)
            if form.is_valid():
                precliente = form.save(commit=False)
                precliente.adicionado_por = request.user
                precliente.save()
                messages.success(request, u'Pré Cliente %s adicionado com sucesso!' % precliente)
                return redirect(reverse('comercial:home'))
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
            cliente_novo = form.save()
            precliente.cliente_convertido = cliente_novo
            precliente.save()
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
        if form.is_valid:
            proposta = form.save(commit=False)
            proposta.cliente = cliente
            proposta.criador_por = request.user
            proposta.save()
            return redirect(reverse('comercial:cliente_ver', args=[cliente.id]) + "#tab_propostas")
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
            proposta.criado_por = request.user
            proposta.save()
            return redirect(reverse('comercial:home'))
    else:
        form = AdicionarPropostaForm()
    return render_to_response('frontend/comercial/comercial-propostas-precliente-adicionar.html', locals(), context_instance=RequestContext(request),)
    


@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_minhas(request):
    minhas_propostas = PropostaComercial.objects.filter(criado_por=request.user, status="aberta")
    propostas_em_meus_clientes = PropostaComercial.objects.filter(cliente__designado=request.user.funcionario, status="aberta").exclude(criado_por=request.user)
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

@user_passes_test(possui_perfil_acesso_comercial)
def requisicao_proposta_cliente_atender(request, requisicao_id):
    requisicao = get_object_or_404(RequisicaoDeProposta, pk=requisicao_id)
    requisicao.atendido = True
    requisicao.atendido_data = datetime.datetime.now()
    requisicao.save()
    # marca como atendida e envia pra tela de adicionar proposta
    return redirect(reverse("comercial:propostas_comerciais_cliente_adicionar", args=[requisicao.cliente.id]))

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def designacoes(request):
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
    clientes = forms.ModelMultipleChoiceField(required=True, queryset=Cliente.objects.all())
    preclientes = forms.ModelMultipleChoiceField(required=True, queryset=PreCliente.objects.filter(cliente_convertido=None))

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
                
        return render_to_response('frontend/comercial/comercial-designacoes-confirmar.html', locals(), context_instance=RequestContext(request),)
    else:
        messages.warning(request, u"Não pode ser acessado diretamente")
        return redirect(reverse("comercial:designacoes"))
