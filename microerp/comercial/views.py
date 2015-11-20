# -*- coding: utf-8 -*-
import datetime, locale, operator
from collections import OrderedDict
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from localflavor.br.br_states import STATE_CHOICES

from django.core.mail import EmailMessage

from django.contrib.sites.models import Site

from django.core.exceptions import ValidationError
from localflavor.br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField

from django import forms

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.db.models import Count

# APPS MODELS
from rh.models import Departamento, Funcionario
from cadastro.models import Cliente, PreCliente, Bairro
from solicitacao.models import Solicitacao
from comercial.models import PropostaComercial, FollowUpDePropostaComercial, RequisicaoDeProposta, ContratoFechado
from comercial.models import DocumentoGerado, ItemGrupoDocumento
from comercial.models import PerfilAcessoComercial, FechamentoDeComissao, CONTRATO_FORMA_DE_PAGAMENTO_CHOICES
from comercial.models import LinhaRecursoMaterial, LinhaRecursoHumano, LinhaRecursoLogistico, Orcamento, GrupoIndicadorDeProdutoProposto
from financeiro.models import LancamentoFinanceiroReceber
from financeiro.models import ContaBancaria
from estoque.models import Produto

from django.conf import settings

from rh import utils

from django.http import HttpResponse

# FORM DE OUTROS APPS
from cadastro.views import AdicionarEnderecoClienteForm


from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.contrib.auth.models import User
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib import colors
from reportlab.lib import utils

from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from io import BytesIO

#
# FORMULARIOS
#


class ConfigurarImpressaoContrato(forms.Form):
    
    def __init__(self, *args, **kwargs):
        contrato = kwargs.pop('contrato')
        super(ConfigurarImpressaoContrato, self).__init__(*args, **kwargs)
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        funcionarios_disponiveis = Funcionario.objects.filter(user__perfilacessocomercial__empresa=contrato.cliente.designado.user.perfilacessocomercial.empresa)
        initial1 = contrato.responsavel_comissionado or None
        a = contrato.cliente.designado
        self.fields['testemunha1'] = forms.ModelChoiceField(queryset=funcionarios_disponiveis, initial=initial1, label="Testemunha 1")
        self.fields['testemunha2'] = forms.ModelChoiceField(queryset=funcionarios_disponiveis, required=False, label="Testemunha 2")
        self.fields['imprime_logo'] = forms.BooleanField()
        self.fields['imprime_logo'].initial = True


class PreClienteAdicionarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        sugestao = kwargs.pop('sugestao')
        perfil = kwargs.pop('perfil')
        super(PreClienteAdicionarForm, self).__init__(*args, **kwargs)
        self.fields['designado'].empty_label = "Nenhum"
        self.fields['designado'].required = True
        self.fields['tipo'].required = True
        self.fields['telefone_fixo'] = BRPhoneNumberField(required=False)
        self.fields['telefone_celular'] = BRPhoneNumberField(required=False)
        if sugestao:
            self.fields['nome'].initial = sugestao
        if not perfil.gerente:
            self.fields['designado'].widget = forms.HiddenInput()
            self.fields['designado'].initial = perfil.user.funcionario
        self.fields['designado'].queryset = perfil.funcionarios_disponiveis()
        self.fields['designado'].widget.attrs['class'] = 'select2'

    def clean_cpf(self):
        tipo = self.cleaned_data.get('tipo', None)
        cpf = self.cleaned_data.get('cpf', None)
        if tipo == 'pf' and not cpf:
            raise ValidationError(u"Para Pré Clientes do tipo PF (Pessoa Física) é necessário informar o CPF")
        elif tipo =='pf' and cpf:
            try:
                cpf = BRCPFField().clean(cpf)
            except:
                raise ValidationError(u"Número do CPF Inválido!")

            # checa se já existe CPF no banco de dados
            if cpf:
                # primeiro os preclientes não convertidos
                precliente = PreCliente.objects.filter(cpf=cpf, cliente_convertido=None)
                if precliente:
                    raise ValidationError(u"Já existe um cliente com este CPF: %s" % precliente[0].nome)
                # agora os preclientes convertidos, no caso, clientes
                cliente = Cliente.objects.filter(cpf=cpf)
                if cliente:
                    raise ValidationError(u"Já existe um cliente com este CPF: %s" % cliente[0].nome)
        return cpf

    #def clean_inscricao_estadual(self):
    #    tipo = self.cleaned_data.get('tipo', None)
    #    inscricao_estadual = self.cleaned_data.get('inscricao_estadual', None)
    #    if tipo == 'pj' and not inscricao_estadual:
    #        raise ValidationError(u'Embora Válido, não é aceito um CNPJ com %s' % '000000000000000')

    def clean_cnpj(self):
        tipo = self.cleaned_data.get('tipo', None)
        cnpj = self.cleaned_data.get('cnpj', None)
        if tipo == 'pj' and not cnpj:
            raise ValidationError(u"Para Clientes do tipo PJ (Pessoa Jurídica) é necessário informar o CNPJ")
        elif tipo == 'pj' and cnpj:
            try:
                cnpj = BRCNPJField().clean(cnpj)
                if cnpj == '00000000000000':
                    raise ValidationError(u"Número do CNPJ Inválido!")
            except:
                raise ValidationError(u"Número do CNPJ Inválido!")

            # checa se já existe CPF no banco de dados
            if cnpj:
                precliente = PreCliente.objects.filter(cnpj=cnpj)
                if precliente:
                    raise ValidationError(u"Já existe um cliente com este CNPJ!: %s" % precliente[0].nome)

        return cnpj

    class Meta:
        model = PreCliente
        fields = 'nome', 'tipo', 'cpf', 'cnpj', 'numero_instalacao', 'telefone_fixo', 'telefone_celular', 'cep', 'rua', 'numero', 'bairro_texto', 'cidade_texto', 'uf_texto', 'complemento', 'dados', 'origem', 'designado'

class AdicionarPropostaForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AdicionarPropostaForm, self).__init__(*args, **kwargs)
        self.fields['valor_proposto'].localize = True
        self.fields['valor_proposto'].widget.is_localized = True
        self.fields['tipo'].required = True
    
    
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
    
    #def clean_inscricao_estadual(self):
    #    tipo = self.cleaned_data.get('tipo', None)
    #    inscricao_estadual = self.cleaned_data.get('inscricao_estadual', None)
    #    if tipo == 'pj' and not inscricao_estadual:
    #        raise ValidationError(u'Embora Válido, não é aceito um CNPJ com %s' % '000000000000000')
        
    def clean_cnpj(self):
        tipo = self.cleaned_data.get('tipo', None)
        cnpj = self.cleaned_data.get('cnpj', None)
        if tipo == 'pj' and not cnpj:
            raise ValidationError(u"Para Clientes do tipo PJ (Pessoa Jurídica) é necessário informar o CNPJ")
        elif tipo == 'pj' and cnpj:
            try:
                cnpj = BRCNPJField().clean(cnpj)
                if cnpj == '00000000000000':
                    raise ValidationError(u"Número do CNPJ Inválido!")
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
        com_endereco = kwargs.pop('com_endereco', False)
        super(AdicionarCliente, self).__init__(*args, **kwargs)
        self.fields['tipo'].required = True
        self.fields['nascimento'].widget.attrs['class'] = 'datepicker'
        if precliente:
            self.fields['nome'].initial = precliente.nome
            self.fields['observacao'].initial = precliente.dados
        if com_endereco:
            #self.fields['bairro'] = forms.ModelChoiceField(queryset=Bairro.objects.all())
            #self.fields['bairro'].widget.attrs['class'] = 'select2'
            self.fields['cep'] = forms.CharField()
            self.fields['rua'] = forms.CharField()
            self.fields['numero'] = forms.CharField()
            self.fields['bairro_texto'] = forms.CharField()
            self.fields['cidade_texto'] = forms.CharField()
            self.fields['uf_texto'] = forms.ChoiceField(choices=STATE_CHOICES)
            #self.fields['cpf'] = forms.IntegerField()
            self.fields['complemento'] = forms.CharField(required=False)
            
            
    
    class Meta:
        model = Cliente
        fields = 'nome', 'tipo', 'fantasia', 'cnpj', 'inscricao_estadual', \
        'cpf', 'rg', 'nascimento', 'ramo', 'observacao', 'origem',\
        'contato', 'email', 'telefone_fixo', 'telefone_celular', 'fax',

class FormAdicionarFollowUp(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        perfil = kwargs.pop('perfil')
        super(FormAdicionarFollowUp, self).__init__(*args, **kwargs)
        self.fields['proposta'].widget = forms.HiddenInput()
        self.fields['texto'].required = True
        self.fields['proposta'].localized = False
        self.fields['probabilidade'].required = True
        self.fields['data_expiracao'].required = False
        self.fields['data_expiracao'].widget.attrs['class'] = 'datepicker'
        self.fields['visita_por'].queryset = perfil.funcionarios_disponiveis()
        self.fields['visita_por'].widget.attrs['class'] = 'select2'

    class Meta:
        model = FollowUpDePropostaComercial
        fields = 'proposta', 'texto', 'probabilidade', 'reagenda_data_expiracao', 'data_expiracao', 'visita', 'visita_por'
    
    def clean_data_expiracao(self):
        data = self.cleaned_data['data_expiracao']
        reagenda_data_expiracao = self.cleaned_data['reagenda_data_expiracao']
        if reagenda_data_expiracao and not data:
            raise forms.ValidationError(u"É preciso informar uma data!")
        return data

    def clean_visita_por(self):
        visita_por = self.cleaned_data['visita_por']
        visita = self.cleaned_data['visita']
        if visita and not visita_por:
            raise forms.ValidationError(u"É preciso indicar o Funcionário que realizou a visita")
        return visita_por
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
def home_angular(request):
    return render_to_response('frontend/comercial/comercial-angular_home.html', locals(),
                              context_instance=RequestContext(request), )

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def home(request):
    # widget cliente
    #ultimos followups
    ultimos_followups = request.user.perfilacessocomercial.ultimos_followups()
        
    preclientes_sem_proposta = request.user.perfilacessocomercial.preclientes_sem_proposta().count()

    requisicoes_propostas = request.user.perfilacessocomercial.requisicao_de_proposta().count()
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
        perfil = kwargs.pop('perfil')
        super(FiltrarPreClientesERequisicoesForm, self).__init__(*args, **kwargs)
        self.fields['funcionario'].widget.attrs['class'] = 'select2'
        self.fields['funcionario'].queryset = perfil.funcionarios_disponiveis()

    funcionario = forms.ModelChoiceField(queryset=None, label="Funcionário", required=False, empty_label="Todos do Comercial")


@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def clientes(request):
    form_filtrar_precliente = FiltrarPreClientesERequisicoesForm(perfil=request.user.perfilacessocomercial)
    cliente_q = request.GET.get('cliente', False)
    # busca realizada
    if cliente_q:
        busca_feita = True
        cliente_q = cliente_q.strip()
        # se super gerente, puxa todos
        if request.user.perfilacessocomercial.super_gerente:
            clientes = Cliente.objects.filter(
                Q(ativo=True) & \
                Q(nome__icontains=cliente_q) | \
                Q(fantasia__icontains=cliente_q) | \
                Q(cnpj__icontains=cliente_q) | \
                Q(cpf__icontains=cliente_q)
            )
            # todos os preclientes
            preclientes = PreCliente.objects.filter(
                cliente_convertido=None
            ).filter(
                Q(nome__icontains=cliente_q) | \
                Q(cnpj__icontains=cliente_q) | \
                Q(cpf__icontains=cliente_q)
            )
        # puxa somente os da mesma empresa
        else:
            clientes = Cliente.objects.filter(
                designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
            ).filter(
                Q(ativo=True) & \
                Q(nome__icontains=cliente_q) | \
                Q(fantasia__icontains=cliente_q) | \
                Q(cnpj__icontains=cliente_q) | \
                Q(cpf__icontains=cliente_q)
            )
            preclientes = PreCliente.objects.filter(
                designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa,
                cliente_convertido=None
            ).filter(
                Q(nome__icontains=cliente_q) | \
                Q(cnpj__icontains=cliente_q) | \
                Q(cpf__icontains=cliente_q)
            )
        #puxa todos os pre clientes, menos os já convertidos)

    else:
        if request.GET.get('cliente') == '' or request.POST.get('btn-aplicar-filtro', None):
            busca_feita = True
            clientes = Cliente.objects.filter(
                designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
            )
            preclientes = PreCliente.objects.filter(
                designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa,
                cliente_convertido=None
            )
    if request.user.perfilacessocomercial.super_gerente:
        # mostra todos preclientes sem proposta
        preclientes_sem_proposta = PreCliente.objects.filter(
                propostacomercial=None, cliente_convertido=None,
                sem_interesse=False,
        ).order_by('nome')
        # mostra todas as requsicoes
        requisicoes_propostas = RequisicaoDeProposta.objects.filter(atendido=False).order_by('cliente__nome')
    elif not request.user.perfilacessocomercial.super_gerente and request.user.perfilacessocomercial.gerente:
        # mostra todos preclientes sem proposta da mesma empresa
        preclientes_sem_proposta = PreCliente.objects.filter(
            propostacomercial=None, cliente_convertido=None,
            sem_interesse=False,
            designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
        ).order_by('nome')
        # mostra requisicoes da empresa empresa
        requisicoes_propostas = RequisicaoDeProposta.objects.filter(
                atendido=False,
                cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
        ).order_by('cliente__nome')
    else:
        # mostra somente meus preclientes sem proposta da minha empresa
        preclientes_sem_proposta = PreCliente.objects.filter(
            propostacomercial=None, cliente_convertido=None,
            sem_interesse=False,
            designado=request.user.funcionario,
            designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
        ).order_by('nome')
        # mostra somente meus clientes com requisicao de proposta

    if request.POST.get('btn-aplicar-filtro', None):
        form_filtrar_precliente = FiltrarPreClientesERequisicoesForm(request.POST, perfil=request.user.perfilacessocomercial)
        if form_filtrar_precliente.is_valid():
            funcionario_escolhido = form_filtrar_precliente.cleaned_data['funcionario']
            if funcionario_escolhido:
                clientes = clientes.filter(designado=funcionario_escolhido)
                preclientes = preclientes.filter(designado=funcionario_escolhido)
                preclientes_sem_proposta = preclientes_sem_proposta.filter(designado=funcionario_escolhido)
    return render_to_response('frontend/comercial/comercial-clientes.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def cliente_ver(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id, ativo=True)
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
    form_adicionar_follow_up = FormAdicionarFollowUp(perfil=request.user.perfilacessocomercial)

    return render_to_response('frontend/comercial/comercial-cliente-ver.html', locals(), context_instance=RequestContext(request),)

class FormEditarProposta(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormEditarProposta, self).__init__(*args, **kwargs)
        
        if (kwargs['instance'].cliente and kwargs['instance'].cliente.tipo != "pj") or kwargs['instance'].precliente :
            del self.fields['nome_do_proposto']
            del self.fields['documento_do_proposto']
        
        self.fields['valor_proposto'].localize = True
        self.fields['valor_proposto'].widget.is_localized = True
        self.fields['parcelamentos_possiveis'].widget.attrs['class'] = 'select2'
        self.fields['parcelamentos_possiveis'].help_text = ""
        self.fields['tipo'].label = "Tipo Principal"
        self.fields['tipos'].label = 'Tipos dessa Proposta'
        self.fields['tipos'].widget.attrs['class'] = 'select2'
    
    def clean_valor_proposto(self):
        data = self.cleaned_data['valor_proposto']
        minimo = self.instance.consolidado()
        if data < minimo:
            raise ValidationError(u"Erro! Valor abaixo do mínimo %s" % minimo)
        return data
    
    class Meta:
        model = PropostaComercial
        fields = 'valor_proposto', 'nome_do_proposto', 'documento_do_proposto', 'tipo', 'tipos', 'parcelamentos_possiveis'
        localized_fields = 'valor_proposto',

class FormSelecionaOrcamentoModelo(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FormSelecionaOrcamentoModelo, self).__init__(*args, **kwargs)
        self.fields['modelo'].widget.attrs['class'] = 'select2'
        self.fields['modelo'].queryset = Orcamento.objects.filter(Q(modelo=True, ativo=True, promocao=False) | Q(modelo=True, ativo=True, promocao=True, inicio_promocao__lte=datetime.date.today(), fim_promocao__gte=datetime.date.today()))
    
    modelo = forms.ModelMultipleChoiceField(queryset=None, required=True)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_editar_orcamento(request, proposta_id, orcamento_id):
    orcamento = get_object_or_404(Orcamento, proposta__id=proposta_id, pk=orcamento_id)
    OrcamentoMaterialFormSet = forms.models.inlineformset_factory(Orcamento, LinhaRecursoMaterial, extra=1, can_delete=True, form=LinhaOrcamentoMaterialForm)
    OrcamentoRecursoHumanoFormSet = forms.models.inlineformset_factory(Orcamento, LinhaRecursoHumano, extra=1, can_delete=True, form=LinhaOrcamentoHumanoForm)
    if request.POST:
        if 'adicionar_linha_material' in request.POST:
            messages.info(request, u"Nova Linha de Materiais adicionada")
            cp = request.POST.copy()
            form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(cp, instance=orcamento, prefix='orcamento-humano')
            cp['orcamento-material-TOTAL_FORMS'] = int(cp['orcamento-material-TOTAL_FORMS'])+ 1
            form_editar_linhas_material = OrcamentoMaterialFormSet(cp, instance=orcamento, prefix='orcamento-material')
            form_orcamento = OrcamentoForm(cp, instance=orcamento)
        if 'adicionar_linha_humano' in request.POST:
            messages.info(request, u"Nova Linha de Mão de Obra adicionada")
            cp = request.POST.copy()
            form_editar_linhas_material = OrcamentoMaterialFormSet(cp, instance=orcamento, prefix='orcamento-material')
            cp['orcamento-humano-TOTAL_FORMS'] = int(cp['orcamento-humano-TOTAL_FORMS'])+ 1            
            form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(cp, instance=orcamento, prefix='orcamento-humano')
            form_orcamento = OrcamentoForm(cp, instance=orcamento)
        elif 'alterar-orcamento' in request.POST:
            form_editar_linhas_material = OrcamentoMaterialFormSet(request.POST, instance=orcamento, prefix="orcamento-material")
            form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(request.POST, instance=orcamento, prefix="orcamento-humano")
            form_orcamento = OrcamentoForm(request.POST, instance=orcamento)
            if form_editar_linhas_material.is_valid() and form_editar_linhas_humano.is_valid() and form_orcamento.is_valid():
                linhas_material = form_editar_linhas_material.save()
                linhas_humano = form_editar_linhas_humano.save()
                orcamento = form_orcamento.save()
                messages.success(request, u"Sucesso! Orçamento (%s) Alterado da Proposta #%s" % (orcamento.descricao, orcamento.proposta.id))
                # se cliente, mostra ficha
                return redirect(reverse('comercial:editar_proposta', args=[orcamento.proposta.id]))
            else:
                form_orcamento = OrcamentoForm(request.POST, instance=orcamento)
        
                
    else:
        form_editar_linhas_material = OrcamentoMaterialFormSet(instance=orcamento, prefix="orcamento-material")
        form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(instance=orcamento, prefix="orcamento-humano")
        form_orcamento = OrcamentoForm(instance=orcamento)
    return render_to_response('frontend/comercial/comercial-editar-proposta-editar-orcamento.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta_reajustar_orcamento(request, proposta_id, orcamento_id):
    orcamento = get_object_or_404(Orcamento, proposta__id=proposta_id, pk=orcamento_id)
    reajustou = orcamento.reajusta_custo()
    if reajustou:
        messages.warning(request, u"Atenção! Houve Reajuste de uma das linhas do Orçamento %s!" % orcamento)
    else:
        messages.success(request, u"Não houveram reajustes de preço para o Orçamento %s" % orcamento)
    
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


class LinhaRecursoLogisticoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LinhaRecursoLogisticoForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].required = True
        self.fields['custo_total'].localize = True
        self.fields['custo_total'].widget.is_localized = True
    
    class Meta:
        model = LinhaRecursoLogistico
        fields = 'tipo', 'custo_total', 'descricao'
        localized_fields = 'custo_total',

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def editar_proposta(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    seleciona_modelos_proposta = FormSelecionaOrcamentoModelo()
    form_editar_proposta = FormEditarProposta(instance=proposta)
    LinhaRecursoLogisticoFormSet = forms.models.inlineformset_factory(PropostaComercial, LinhaRecursoLogistico, extra=1, can_delete=True, form=LinhaRecursoLogisticoForm)
    adicionar_orcamento_form = OrcamentoForm(initial={'proposta': proposta.id })
    form_editar_linhas_logistica = LinhaRecursoLogisticoFormSet(instance=proposta, prefix="proposta-logistica")
    if request.POST:
        if 'adicionar-modelos' in request.POST:
            seleciona_modelos_proposta = FormSelecionaOrcamentoModelo(request.POST)
            if seleciona_modelos_proposta.is_valid():
                modelos = seleciona_modelos_proposta.cleaned_data['modelo']
                # clona o modelo de orcamento pra dentro da proposta
                for modelo in modelos:
                    linhas_materiais = modelo.linharecursomaterial_set.all()
                    linhas_humano = modelo.linharecursohumano_set.all()
                    # cria novo orcamento à partir de modelo
                    novo_orcamento = modelo
                    orcamento_id_originario = modelo.id
                    novo_orcamento.pk = None
                    novo_orcamento.save()
                    if modelo.promocao:
                        novo_orcamento.promocao = modelo.promocao # se for promocao, passa pra frente
                        # registra promocao originaria
                        novo_orcamento.promocao_originaria_id = orcamento_id_originario
                        # registra inicio e fim da promocao
                        novo_orcamento.inicio_promocao = modelo.inicio_promocao
                        novo_orcamento.fim_promocao = modelo.fim_promocao
                    if modelo.tabelado:
                        novo_orcamento.tabelado_originario_id = orcamento_id_originario

                    if modelo.promocao or modelo.tabelado:
                        novo_orcamento.custo_total = modelo.custo_total
                        
                    novo_orcamento.modelo = False
                    novo_orcamento.proposta = proposta
                    novo_orcamento.save()
                    if novo_orcamento.promocao:
                        novo_orcamento.promocao_originaria = modelo
                        novo_orcamento.save()
                    # copia todos as linhas de materiais pro modelo
                    for linha in linhas_materiais:
                        linha.pk = None
                        linha.orcamento = novo_orcamento
                        linha.save()
                    # copia todas as linhas de recursos humanos
                    # copia todos as linhas de materiais pro modelo
                    for linha in linhas_humano:
                        linha.pk = None
                        linha.orcamento = novo_orcamento
                        linha.save()
                # retorna
                return redirect(reverse("comercial:editar_proposta", args=[proposta.id,]))
                    
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
        if 'salva-recursos-logisticos' in request.POST:
            form_editar_linhas_logistica = LinhaRecursoLogisticoFormSet(request.POST, instance=proposta, prefix="proposta-logistica")
            if form_editar_linhas_logistica.is_valid():
                form_editar_linhas_logistica = form_editar_linhas_logistica.save()
                return redirect(reverse('comercial:editar_proposta', args=[proposta.id]))

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
        if request.user.perfilacessocomercial.super_gerente:
            propostas = PropostaComercial.objects.filter(
                pk__in=propostas_a_fechar
            )

        else:
            propostas = PropostaComercial.objects.filter(
                pk__in=propostas_a_fechar,
                cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
            )
        for proposta in propostas:
            if request.POST.get('aprovar-fechamento'):
                proposta.status = 'perdida'
                messages.error(request, "Proposta #%s Fechada!" % proposta.id)
            elif request.POST.get('reabrir-proposta'):
                proposta.status = 'aberta'
                messages.success(request, "Proposta #%s Reaberta!" % proposta.id)
            proposta.save()
    if request.user.perfilacessocomercial.super_gerente:
        propostas_fechadas = PropostaComercial.objects.filter(status="perdida_aguardando")
    else:
        propostas_fechadas = PropostaComercial.objects.filter(
            cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa,
            status="perdida_aguardando"
        )
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
        fields = ("data_cobranca", 'valor_cobrado', 'modo_recebido', 'observacao_recebido')
        localized_fields = 'valor_cobrado',

class ConfigurarContratoBaseadoEmProposta(forms.Form):
    '''Formulario usado pra alterar as informacoes que serao importadas
    pro contrato com base na proposta'''
    
    def __init__(self, *args, **kwargs):
        perfil = kwargs.pop('perfil', None)
        super(ConfigurarContratoBaseadoEmProposta, self).__init__(*args, **kwargs)
        self.fields['apoio_tecnico'].widget.attrs['class'] = 'select2'
        self.fields['apoio_tecnico'].queryset = perfil.funcionarios_disponiveis()
        self.fields['conta_transferencia'].queryset = perfil.empresa.contas_disponiveis.all()
    
    objeto = forms.CharField(widget = forms.Textarea, label="Objeto do Contrato", required=True)
    items_incluso = forms.CharField(widget = forms.Textarea, label="Itens Inclusos", required=True)
    items_nao_incluso = forms.CharField(widget = forms.Textarea, label=u"Itens Não Inclusos", required=True)
    normas_execucao = forms.CharField(widget = forms.Textarea, label=u"Direitos e Obrigações", required=True)
    prazos_execucao = forms.CharField(widget = forms.Textarea, label=u"Prazos de Execução", required=True)
    rescisao = forms.CharField(widget = forms.Textarea, label=u"Rescisão", required=True)
    garantia = forms.CharField(widget = forms.Textarea, label="Garantia", required=True)
    foro = forms.CharField(widget = forms.Textarea, label=u"Foro", required=True)
    endereco_obra = forms.CharField(widget = forms.Textarea, label=u"Endereço da Obra", required=True)
    
    #observacoes = forms.CharField(widget = forms.Textarea, label=u"Observações", required=False)
    nome_do_proposto_legal = forms.CharField()
    documento_do_proposto_legal = BRCPFField(label="Documento Legal do Proposto (CPF)")
    apoio_tecnico = forms.ModelChoiceField(
        queryset=Funcionario.objects.exclude(periodo_trabalhado_corrente=None),
        label=u"Apoio Técnico", required=False
    )
    conta_transferencia = forms.ModelChoiceField(
            queryset=ContaBancaria.objects.all(),
            label=u"Conta para Transferência",
        help_text="Obrigatório Somente se houver Transferência Eletrônica nas Parcelas", required=False
    )


class UsarCartaoCredito(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(UsarCartaoCredito, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs['class'] = 'datepicker'
    
    data = forms.DateField(initial=datetime.date.today())
    tipo = forms.ChoiceField(choices=CONTRATO_FORMA_DE_PAGAMENTO_CHOICES)
    parcelas = forms.IntegerField()


class BasearContratoNoModelo(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        proposta = kwargs.pop('proposta', None)
        modelo = kwargs.pop('modelo', None)
        perfil = kwargs.pop('perfil', None)
        super(BasearContratoNoModelo, self).__init__(*args, **kwargs)
        self.fields['valor'].initial = proposta.valor_proposto
        if proposta.tipo.tipo_contrato_mapeado:
            self.fields['categoria'].initial = proposta.tipo.tipo_contrato_mapeado.id
        self.fields['categoria'].required = True
        self.fields['responsavel'].initial = perfil.user.funcionario
        # adiciona os campos editaveis do modelo
        itens_editaveis = ItemGrupoDocumento.objects.filter(
            (Q(texto_editavel=True)| Q(imagem_editavel=True)) & \
            Q(grupo__documento=modelo)
            ).order_by('grupo__peso', 'peso').distinct()
        # remove os lancamentos e parcelamentos da exibição
        itens_editaveis = itens_editaveis.exclude(chave_identificadora__in=('parcelamentos', 'lancamentos'))
        if perfil:
            self.fields['responsavel'].queryset = perfil.funcionarios_disponiveis()
            self.fields['apoio_tecnico'].queryset = perfil.funcionarios_disponiveis()
            self.fields['responsavel_comissionado'].queryset = perfil.funcionarios_disponiveis()
        for textos_editaveis in itens_editaveis:
            self.fields[textos_editaveis.chave_identificadora] = forms.CharField(widget=forms.Textarea)
            self.fields[textos_editaveis.chave_identificadora].widget.attrs['class'] = 'tinymce'
            self.fields[textos_editaveis.chave_identificadora].label=textos_editaveis.titulo
            self.fields[textos_editaveis.chave_identificadora].required = True
            try:
                # se existe item da proposta com mesma chave, busca conteudo
                item = ItemGrupoDocumento.objects.get(
                    chave_identificadora=textos_editaveis.chave_identificadora,
                    grupo__documento=proposta.documento_gerado
                )
                texto = item.texto
            except ItemGrupoDocumento.DoesNotExist:
                # caso nao exista, usar o conteudo do modelo
                texto = textos_editaveis.texto
            self.fields[textos_editaveis.chave_identificadora].initial = texto
            # se existe item da proposta com chave contratante, sugerir conteudo
            if textos_editaveis.chave_identificadora == 'contratante':
                self.fields[textos_editaveis.chave_identificadora].initial = proposta.cliente.sugerir_texto_contratante()
            if textos_editaveis.chave_identificadora == 'contratado':
                self.fields[textos_editaveis.chave_identificadora].initial = proposta.cliente.sugerir_texto_contratado()


    class Meta:
        model = ContratoFechado
        fields = 'valor', 'categoria', 'forma_pagamento', 'responsavel', 'apoio_tecnico', 'responsavel_comissionado'

@user_passes_test(possui_perfil_acesso_comercial)
def editar_proposta_converter_novo(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id, status="aberta")
        # exige cliente na proposta
    if not proposta.cliente:
        messages.error(request, u'É obrigatório converter um Pré Cliente para Cliente ANTES de converter uma proposta.')
        return redirect(reverse("comercial:precliente_converter", args=[proposta.precliente.id])+"?proposta_referencia=%s" % proposta.id)

    if request.GET.get('escolhido', None):
        modelo_escolhido = DocumentoGerado.objects.get(pk=request.GET.get('escolhido', None))
    else:
        # puxa o modelo do tipo contrato pro mesmo tipo de proposta
        modelo_documento_contrato = DocumentoGerado.objects.filter(
            modelo=True,
            tipo_proposta=proposta.tipo,
            tipo='contrato',
            empresa_vinculada=request.user.perfilacessocomercial.empresa
        )
        if not modelo_documento_contrato:
            messages.error(request, u"Erro de Parametrização. Não existe um modelo de Contrato para este tipo de Proposta: %s" % proposta.tipo)
            return redirect(reverse("comercial:propostas_comerciais_minhas"))
        return render_to_response('frontend/comercial/comercial-proposta-converter_novo.html', locals(), context_instance=RequestContext(request),)

    ConfigurarConversaoPropostaFormset = forms.models.inlineformset_factory(ContratoFechado, LancamentoFinanceiroReceber, extra=0, form=LancamentoFinanceiroReceberComercialForm)

    usar_cartao_credito = UsarCartaoCredito()

    if request.POST:
        modelo_escolhido = DocumentoGerado.objects.get(pk=request.POST.get('escolhido'))
        if 'usar-cartao' in request.POST:
            form_cartao = UsarCartaoCredito(request.POST)
            form_contrato = BasearContratoNoModelo(request.POST, modelo=modelo_escolhido, proposta=proposta, perfil=request.user.perfilacessocomercial)
            form_configurar_contrato = ConfigurarConversaoPropostaFormset(request.POST, prefix="configurar_contrato")
            if form_cartao.is_valid():
                data = form_cartao.cleaned_data['data']
                tipo = form_cartao.cleaned_data['tipo']
                parcelas = form_cartao.cleaned_data['parcelas']
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
                        cp['configurar_contrato-%s-modo_recebido' % p] = tipo
                        cp['configurar_contrato-%s-valor_cobrado' % p] = cada_parcela
                    form_configurar_contrato = ConfigurarConversaoPropostaFormset(cp, prefix="configurar_contrato")
                    configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST, perfil=request.user.perfilacessocomercial)
                    messages.info(request, 'Adicionando %s parcelas de %s para o dia %s' % (parcelas, cada_parcela, data))
                else:
                    messages.error(request, u"Erro! Não existe mais Valor restante para parcelar no cartão")
        if 'adicionar-parcela' in request.POST:
            messages.info(request, u"Nova Parcela de Lançamento Financeiro a Receber Adicionada!")
            cp = request.POST.copy()
            cp['configurar_contrato-TOTAL_FORMS'] = int(cp['configurar_contrato-TOTAL_FORMS'])+ 1
            configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST, perfil=request.user.perfilacessocomercial)
        if 'converter' in request.POST:
            form_contrato = BasearContratoNoModelo(request.POST, modelo=modelo_escolhido, perfil=request.user.perfilacessocomercial, proposta=proposta)
            form_configurar_contrato = ConfigurarConversaoPropostaFormset(request.POST, prefix="configurar_contrato")
            if form_contrato.is_valid():
                total_lancamentos = 0
                for form in form_configurar_contrato.forms:
                    if form not in form_configurar_contrato.deleted_forms:
                        if form.cleaned_data and form.cleaned_data.get('valor_cobrado'):
                            total_lancamentos += form.cleaned_data.get('valor_cobrado', 0)
                if float(total_lancamentos) == float(proposta.valor_proposto):
                    # cria contrato
                    novo_contrato = form_contrato.save(commit=False)
                    novo_contrato.objeto = 'objeto presente no documento gerado'
                    novo_contrato.status = 'emanalise'
                    novo_contrato.cliente = proposta.cliente
                    novo_contrato.save()
                    novo_contrato.propostacomercial = proposta
                    novo_contrato.save()
                    # vincular contrato na proposta
                    proposta.contrato_vinculado = novo_contrato
                    proposta.probabilidade = 100
                    proposta.status = "convertida"
                    proposta.definido_convertido_em = datetime.datetime.now()
                    proposta.definido_convertido_por = request.user.funcionario
                    proposta.save()
                    # registra lancamentos vinculando ao novo contrato
                    i = 0
                    for form in form_configurar_contrato.forms:
                        if form.is_valid() and form not in form_configurar_contrato.deleted_forms:
                            i += 1
                            novo_lancamento = form.save(commit=False)
                            novo_lancamento.contrato = novo_contrato
                            novo_lancamento.peso = i
                            novo_lancamento.save()

                    # cria novo documento gerado
                    documento = novo_contrato.cria_documento_gerado(modelo=modelo_escolhido)
                    messages.success(request, u"Contrato %s Criado! Documento de Contrato Gerado" % (novo_contrato.pk))
                    # atualiza dados que possuem no documento da proposta
                    # puxa todos os campos editaveis do documento da proposta
                    editaveis_da_proposta = ItemGrupoDocumento.objects.filter(grupo__documento__propostacomercial=proposta, texto_editavel=True)
                    items_presentes_no_contrato = ItemGrupoDocumento.objects.filter(grupo__documento__contratofechado=novo_contrato)
                    for item in items_presentes_no_contrato:
                        # preenche o campo de parcela, caso exista
                        if item.chave_identificadora in ('parcelamentos', 'lancamentos'):
                            item.texto = novo_contrato.sugere_texto_lancamentos_abertos()
                            item.save()
                        # para cada item  editavel do contrato
                        # busca o item no  formulario enviado
                        try:
                            texto_alterado = form_contrato.cleaned_data[str(item.chave_identificadora)]
                            item.texto = texto_alterado
                            item.save()
                        except:
                            pass
                    # conversao concluida, envia pra view de contratos
                    return redirect(reverse("comercial:contratos_meus"))
                else:
                    diferenca = float(proposta.valor_proposto) - float(total_lancamentos)
                    messages.error(request, u"Erro! Valor de Lançamentos (R$ %s) é diferente do valor do Contrato (R$ %s). Diferença: R$ %s" % (total_lancamentos, proposta.valor_proposto, diferenca))
    else:
        form_contrato = BasearContratoNoModelo(modelo=modelo_escolhido, proposta=proposta, perfil=request.user.perfilacessocomercial)
        messages.info(request, u"Modelo Escolhido: %s" % modelo_escolhido)
        form_configurar_contrato = ConfigurarConversaoPropostaFormset(prefix="configurar_contrato")
        usar_cartao_credito = UsarCartaoCredito()
    return render_to_response('frontend/comercial/comercial-proposta-converter_novo.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial)
def editar_proposta_converter(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id, status="aberta")
    # mantendo compatbilidade com sistema antigo
    if proposta.documento_gerado:
        return redirect(reverse("comercial:editar_proposta_converter_novo", args=[proposta.pk]))
    # modelos de texto
    modelo_objeto = getattr(settings, 'MODELOS_OBJETO_CONTRATO', None)
    modelo_garantia = getattr(settings, 'MODELOS_GARANTIA_CONTRATO', None)
    modelo_normas = getattr(settings, 'TIPO_NORMA_EXECUCAO', None)
    modelo_prazos = getattr(settings, 'MODELOS_PRAZOS_EXECUCAO', None)
    modelo_rescisao = getattr(settings, 'MODELOS_RESCISAO', None)
    modelo_foro = getattr(settings, 'MODELOS_FORO', None)
    modelo_itens_inclusos = getattr(settings, 'MODELOS_ITENS_INCLUSOS', None)
    modelo_items_nao_incluso = getattr(settings, 'MODELOS_ITENS_NAO_INCLUSOS', None)
    modelo_foro = getattr(settings, 'MODELOS_FORO', None)
    ConfigurarConversaoPropostaFormset = forms.models.inlineformset_factory(ContratoFechado, LancamentoFinanceiroReceber, extra=0, form=LancamentoFinanceiroReceberComercialForm)
    usar_cartao_credito = UsarCartaoCredito()
    # preencher rescisao e foro automatico, pois sempre estrá vazio, com o primeiro valor possível
    if modelo_rescisao:
        rescisao_inicial = modelo_rescisao.items()[0][1]
    else:
        rescisao_inicial = None
    if modelo_foro:
        foro_inicial = modelo_foro.items()[0][1]
    else:
        foro_inicial = None

    configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(
        perfil = request.user.perfilacessocomercial,
        initial={
            'objeto': proposta.objeto_proposto,
            'garantia': proposta.garantia_proposto,
            'items_incluso': proposta.descricao_items_proposto,
            'items_nao_incluso': proposta.items_nao_incluso,
            'observacoes': proposta.forma_pagamento_proposto,
            'endereco_obra': proposta.endereco_obra_proposto,
            'nome_do_proposto_legal': proposta.nome_do_proposto,
            'documento_do_proposto_legal': proposta.documento_do_proposto,
            'foro': foro_inicial,
            'rescisao': rescisao_inicial,
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
                    tipo = form_cartao.cleaned_data['tipo']
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
                            cp['configurar_contrato-%s-modo_recebido' % p] = tipo
                            cp['configurar_contrato-%s-valor_cobrado' % p] = cada_parcela
                        form_configurar_contrato = ConfigurarConversaoPropostaFormset(cp, prefix="configurar_contrato")
                        configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST, perfil=request.user.perfilacessocomercial)
                        messages.info(request, 'Adicionando %s parcelas de %s para o dia %s' % (parcelas, cada_parcela, data))
                    else:
                        messages.error(request, u"Erro! Não existe mais Valor restante para parcelar no cartão")
            if 'adicionar-parcela' in request.POST:
                messages.info(request, u"Nova Parcela de Lançamento Financeiro a Receber Adicionada!")
                cp = request.POST.copy()
                cp['configurar_contrato-TOTAL_FORMS'] = int(cp['configurar_contrato-TOTAL_FORMS'])+ 1
                form_configurar_contrato = ConfigurarConversaoPropostaFormset(cp, prefix="configurar_contrato")
                configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST, perfil=request.user.perfilacessocomercial)
            elif 'converter-contrato' in request.POST:
                configurar_contrato_form = ConfigurarContratoBaseadoEmProposta(request.POST, perfil=request.user.perfilacessocomercial)
                form_configurar_contrato = ConfigurarConversaoPropostaFormset(request.POST, prefix="configurar_contrato")
                if form_configurar_contrato.is_valid() and configurar_contrato_form.is_valid():
                    # checa se total preenchido no formulario bate com valor proposto
                    total_lancamentos = 0
                    for form in form_configurar_contrato.forms:
                        if form not in form_configurar_contrato.deleted_forms:
                            if form.cleaned_data and form.cleaned_data.get('valor_cobrado'):
                                total_lancamentos += form.cleaned_data.get('valor_cobrado', 0)
                    # verifica se existe alguma parcela com transferencia, se sim, conta bancaria deve ser preenchido
                    possui_transferencia = False
                    for form in form_configurar_contrato.forms:
                        if form not in form_configurar_contrato.deleted_forms:
                            if form.cleaned_data and form.cleaned_data.get('modo_recebido') == 'transferencia':
                                possui_transferencia = True
                    if possui_transferencia and configurar_contrato_form.cleaned_data.get('conta_transferencia') is None:
                        configurar_contrato_form.add_error('conta_transferencia', u"Contrato Possui Transferência Bancária, este campo é obrigatório.")
                        messages.error(request, u"Erro! Contrato Possui transferência Bancária. É obrigatório Selecionar uma Conta Bancária")
                    else:
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
                            # determina 100% de fechamento da proposta
                            proposta.probabilidade=100
                            #salva a proposta
                            proposta.save()
                            messages.success(request, u"Sucesso! Proposta #%s convertida em Contrato #%s" % (proposta.id, novo_contrato.id))
                            # registra lancamentos vinculando ao novo contrato
                            i = 0
                            for form in form_configurar_contrato.forms:
                                if form.is_valid() and form not in form_configurar_contrato.deleted_forms:
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
                            novo_contrato.normas_execucao = configurar_contrato_form.cleaned_data['normas_execucao']
                            novo_contrato.prazos_execucao = configurar_contrato_form.cleaned_data['prazos_execucao']
                            novo_contrato.endereco_obra = configurar_contrato_form.cleaned_data['endereco_obra']
                            novo_contrato.rescisao = configurar_contrato_form.cleaned_data['rescisao']
                            novo_contrato.prazo_execucao = configurar_contrato_form.cleaned_data['prazos_execucao']
                            novo_contrato.foro = configurar_contrato_form.cleaned_data['foro']
                            #novo_contrato.observacoes = configurar_contrato_form.cleaned_data['observacoes']
                            novo_contrato.nome_proposto_legal = configurar_contrato_form.cleaned_data['nome_do_proposto_legal']
                            novo_contrato.documento_proposto_legal = configurar_contrato_form.cleaned_data['documento_do_proposto_legal']
                            novo_contrato.apoio_tecnico = configurar_contrato_form.cleaned_data['apoio_tecnico']
                            novo_contrato.conta_transferencia = configurar_contrato_form.cleaned_data['conta_transferencia']
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
        perfil = kwargs.pop('perfil', None)
        super(VincularPreClienteParaClienteForm, self).__init__(*args, **kwargs)
        self.fields['cliente'].widget.attrs['class'] = 'select2'
        # se super gerente, mostrar todos os clientes
        if perfil.super_gerente:
            self.fields['cliente'].queryset = Cliente.objects.filter(ativo=True)
        else:
            self.fields['cliente'].queryset = Cliente.objects.filter(
                designado__user__perfilacessocomercial__empresa=perfil.empresa
            )
    
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.filter(ativo=True))


class VincularPreClienteParaPreClienteForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        perfil = kwargs.pop('perfil', None)
        self.precliente = kwargs.pop('precliente')
        super(VincularPreClienteParaPreClienteForm, self).__init__(*args, **kwargs)
        self.fields['precliente'].widget.attrs['class'] = 'select2'
        if perfil.super_gerente:
            self.fields['precliente'].queryset = PreCliente.objects.filter(
                cliente_convertido=None
                ).exclude(id=self.precliente.id)
        else:
            self.fields['precliente'].queryset = PreCliente.objects.filter(
                designado__user__perfilacessocomercial__empresa=perfil.empresa,
                cliente_convertido=None
            ).exclude(id=self.precliente.id)
    
    precliente = forms.ModelChoiceField(queryset=None)

@user_passes_test(possui_perfil_acesso_comercial)
def precliente_ver(request, pre_cliente_id):
    precliente = get_object_or_404(PreCliente, pk=pre_cliente_id)
    form_adicionar_follow_up = FormAdicionarFollowUp(perfil=request.user.perfilacessocomercial)

    if request.POST:
        form_vincular_a_cliente = VincularPreClienteParaClienteForm(request.POST, perfil=request.user.perfilacessocomercial)
        form_vincular_a_precliente = VincularPreClienteParaPreClienteForm(request.POST, precliente=precliente, perfil=request.user.perfilacessocomercial)
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
        form_vincular_a_cliente = VincularPreClienteParaClienteForm(perfil=request.user.perfilacessocomercial)
        form_vincular_a_precliente = VincularPreClienteParaPreClienteForm(precliente=precliente, perfil=request.user.perfilacessocomercial)
    return render_to_response('frontend/comercial/comercial-precliente-ver.html', locals(), context_instance=RequestContext(request),)

# Pre Cliente
@user_passes_test(possui_perfil_acesso_comercial)
def precliente_adicionar(request):
    if request.POST:
        try:
            form = form_add_precliente = PreClienteAdicionarForm(data=request.POST, sugestao=None, perfil=request.user.perfilacessocomercial)
            if form.is_valid():
                precliente = form.save(commit=False)
                if precliente.tipo == 'pf':
                    precliente.cnpj = None
                else:
                    precliente.cpf = None
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
    if request.GET.get('proposta_referencia', None):
        proposta_referencia = PropostaComercial.objects.get(pk=request.GET.get('proposta_referencia', None))
    else:
        proposta_referencia = None
    if request.POST:
        form = AdicionarCliente(request.POST, precliente=precliente, com_endereco=True)
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
            # salva o endereco
            cliente_novo.enderecocliente_set.create(
                #bairro=form.cleaned_data['bairro'],
                bairro_texto = form.cleaned_data['bairro_texto'],
                cidade_texto = form.cleaned_data['cidade_texto'],
                uf_texto = form.cleaned_data['uf_texto'],
                cep=form.cleaned_data['cep'],
                rua=form.cleaned_data['rua'],
                numero=form.cleaned_data['numero'],
                complemento=form.cleaned_data['complemento'],
            )
            # retorna para a proposta de referencia
            if request.GET.get('proposta_referencia'):
                return redirect(reverse('comercial:editar_proposta_converter', args=[request.GET.get('proposta_referencia')]))
            # retorna para a nova ficha do cliente
            else:
                return redirect(reverse('comercial:cliente_ver', args=[cliente_novo.id]))
    else:
        initial = {}
        # se proposta tiver documento gerado, puxar do precliente
        # pois o precliente ja possui mais dados.
        if proposta_referencia and not proposta_referencia.documento_gerado:
            initial={
                'email': proposta_referencia.email_proposto,
                'rua': proposta_referencia.rua_do_proposto,
                'bairro_texto': proposta_referencia.bairro_do_proposto,
                'cep': proposta_referencia.cep_do_proposto,
                'cidade_texto': proposta_referencia.cidade_do_proposto,
                'uf_texto': proposta_referencia.estado_do_proposto,
                'tipo': proposta_referencia.precliente.tipo,
                'cpf': proposta_referencia.precliente.cpf,
                'cnpj': proposta_referencia.precliente.cnpj,
                'origem': proposta_referencia.precliente.origem
            }
        else:
            initial = {
                'tipo': precliente.tipo,
                'cpf': precliente.cpf,
                'cnpj': precliente.cnpj,
                'origem': precliente.origem,
                'telefone_fixo': precliente.telefone_fixo,
                'telefone_celular': precliente.telefone_celular,
                'cep': precliente.cep,
                'rua': precliente.rua,
                'numero': precliente.numero,
                'bairro_texto': precliente.bairro_texto,
                'cidade_texto': precliente.cidade_texto,
                'uf_texto': precliente.uf_texto,
                'complemento': precliente.complemento,
            }
            #a

        form = AdicionarCliente(precliente=precliente, com_endereco=True, initial=initial )
    return render_to_response('frontend/comercial/comercial-precliente-converter.html', locals(), context_instance=RequestContext(request),)

# propostas comerciais
@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_ver(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    return render_to_response('frontend/comercial/comercial-propostas-ver.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_cliente_adicionar(request, cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id, ativo=True)
    if request.POST:
        form = AdicionarPropostaForm(request.POST)
        if form.is_valid():
            proposta = form.save(commit=False)
            # primeira expiracao, pega sugestão padrao
            proposta.data_expiracao = proposta.sugere_data_reagendamento_expiracao()
            proposta.cliente = cliente
            proposta.criador_por = request.user.funcionario
            proposta.designado = cliente.designado
            # puxa configuracoes padrao de lucro, administrativo e impostos
            proposta.lucro = getattr(settings, "LUCRO", 0)
            proposta.administrativo = getattr(settings, "ADMINISTRATIVO", 0)
            proposta.impostos = getattr(settings, "IMPOSTOS", 0)
            proposta.save()
            # cria documento gerado da proposta com base em modelo
            modelos_proposta = DocumentoGerado.objects.filter(
                modelo=True,
                tipo_proposta=proposta.tipo,
                tipo='proposta',
                empresa_vinculada=request.user.perfilacessocomercial.empresa
            )
            if not modelos_proposta:
                modelos_proposta = DocumentoGerado.objects.filter(
                    modelo=True,
                    tipo_proposta=proposta.tipo,
                    tipo='proposta',
                    empresa_vinculada=None
                )
            if modelos_proposta:
                proposta.cria_documento_gerado(modelo=modelos_proposta[0])
                # Auto Preenche Endereco da Obra
                item = ItemGrupoDocumento.objects.filter(grupo__documento__propostacomercial=proposta, chave_identificadora='endereco_obra').first()
                if proposta.precliente and item:
                    item.texto = precliente.logradouro_completo()
                if proposta.cliente and item:
                    item.texto = cliente.logradouro_completo()
                if item:
                    item.save()
                # auto preenche Prezado
                item = ItemGrupoDocumento.objects.filter(grupo__documento__propostacomercial=proposta, chave_identificadora='prezado').first()
                if proposta.precliente and item:
                    item.texto = "Prezado(a) %s" % proposta.precliente.nome
                if proposta.cliente and item:
                    item.texto = "Prezado(a) %s" % proposta.cliente.nome
                if item:
                    item.save()

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
            # primeira expiracao, pega sugestão padrao
            proposta.data_expiracao = proposta.sugere_data_reagendamento_expiracao()
            proposta.precliente = precliente
            proposta.criado_por = request.user.funcionario
            proposta.designado = precliente.designado
            # puxa configuracoes padrao de lucro, administrativo e impostos
            proposta.lucro = getattr(settings, "LUCRO", 0)
            proposta.administrativo = getattr(settings, "ADMINISTRATIVO", 0)
            proposta.impostos = getattr(settings, "IMPOSTOS", 0)
            proposta.save()
            # cria documento gerado da proposta com base em modelo
            modelos_proposta = DocumentoGerado.objects.filter(
                modelo=True,
                tipo_proposta=proposta.tipo,
                tipo='proposta',
                empresa_vinculada=request.user.perfilacessocomercial.empresa
            )
            if not modelos_proposta:
                modelos_proposta = DocumentoGerado.objects.filter(
                    modelo=True,
                    tipo_proposta=proposta.tipo,
                    tipo='proposta',
                    empresa_vinculada=None
                )
            if modelos_proposta:
                proposta.cria_documento_gerado(modelo=modelos_proposta[0])
                # Auto Preenche Endereco da Obra
                item = ItemGrupoDocumento.objects.filter(grupo__documento__propostacomercial=proposta, chave_identificadora='endereco_obra').first()
                item.texto = precliente.logradouro_completo()
                item.save()
                # auto preenche Prezado
                item = ItemGrupoDocumento.objects.filter(grupo__documento__propostacomercial=proposta, chave_identificadora='prezado').first()
                if proposta.precliente and item:
                    item.texto = "Prezado(a) %s" % proposta.precliente.nome
                if proposta.cliente and item:
                    item.texto = "Prezado(a) %s" % proposta.cliente.nome
                if item:
                    item.save()
            # salva

            messages.success(request, "Sucesso! Proposta Adicionada para Pré Cliente.")
            return redirect(reverse('comercial:editar_proposta', args=[proposta.id]))
    else:
        form = AdicionarPropostaForm()
    return render_to_response('frontend/comercial/comercial-propostas-precliente-adicionar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_minhas(request):
    form_adicionar_follow_up = FormAdicionarFollowUp(perfil=request.user.perfilacessocomercial)

    if not request.user.perfilacessocomercial.gerente:
        propostas_abertas_validas = PropostaComercial.objects.filter(
            status='aberta', data_expiracao__gte=datetime.date.today()).order_by('cliente', 'precliente').filter(
            Q(cliente__designado=request.user.funcionario) | Q(precliente__designado=request.user.funcionario) | Q(designado=request.user.funcionario) | Q(designado=None) & \
            (Q(precliente__designado=None) & Q(cliente__designado=None))
            )
        propostas_abertas_expiradas_count = PropostaComercial.objects.filter(status='aberta', data_expiracao__lt=datetime.date.today()).filter(
            Q(cliente__designado=request.user.funcionario) | Q(precliente__designado=request.user.funcionario) | Q(designado=request.user.funcionario) | Q(designado=None) & \
            (Q(precliente__designado=None) & Q(cliente__designado=None))
            ).count()
    else:
        if request.user.perfilacessocomercial.super_gerente:
            propostas_abertas_validas = PropostaComercial.objects.filter(status='aberta', data_expiracao__gte=datetime.date.today()).order_by('precliente', 'cliente')
            propostas_abertas_expiradas_count = PropostaComercial.objects.filter(status='aberta', data_expiracao__lt=datetime.date.today()).count()
        else:
            propostas_abertas_validas = PropostaComercial.objects.filter(
                status='aberta',
                data_expiracao__gte=datetime.date.today()).filter(
                    Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                    Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
            ).order_by('-criado', 'precliente', 'cliente')
            propostas_abertas_expiradas_count = PropostaComercial.objects.filter(
                status='aberta', data_expiracao__lt=datetime.date.today(),
                designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
            ).count()

    designados_propostas_validas = propostas_abertas_validas.values('designado__nome', 'designado__id').annotate(Count('designado__nome')).order_by('designado__nome')

    return render_to_response('frontend/comercial/comercial-propostas-minhas.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def propostas_comerciais_minhas_expiradas_ajax(request):

    
    if not request.user.perfilacessocomercial.gerente:
        propostas_abertas_expiradas = PropostaComercial.objects.filter(status='aberta', data_expiracao__lt=datetime.date.today()).filter(
            Q(cliente__designado=request.user.funcionario) | Q(precliente__designado=request.user.funcionario) | Q(designado=request.user.funcionario)
            )
    else:
        if request.user.perfilacessocomercial.super_gerente:
            propostas_abertas_expiradas = PropostaComercial.objects.filter(status='aberta', data_expiracao__lt=datetime.date.today())
        else:
            propostas_abertas_expiradas = PropostaComercial.objects.filter(
                    status='aberta', data_expiracao__lt=datetime.date.today(),
                    designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
            )



    designados_propostas_expiradas = propostas_abertas_expiradas.values('designado__nome', 'designado__id').annotate(Count('designado__nome'))
    return render_to_response('frontend/comercial/comercial-propostas-minhas-expiradas-ajax.html', locals(), context_instance=RequestContext(request),)
    
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
    
    
    clientes = forms.ModelMultipleChoiceField(required=False, queryset=Cliente.objects.filter(ativo=True))
    preclientes = forms.ModelMultipleChoiceField(required=False, queryset=PreCliente.objects.filter(cliente_convertido=None))

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def designacoes(request):
    escolher_clientes_form = FormEscolherClientesEPreClientes()
    cliente_sem_designacao = Cliente.objects.filter(designado=None, ativo=True)
    precliente_sem_designacao = PreCliente.objects.filter(designado=None, cliente_convertido=None)
    cliente_designacao_invalida = Cliente.objects.exclude(designado=None).filter(designado__periodo_trabalhado_corrente=None, ativo=True)
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
            self.fields['clientes'].queryset = Cliente.objects.filter(ativo=True)
            self.fields['clientes'].initial = clientes
        # pre
        if preclientes:
            self.fields['preclientes'].queryset = PreCliente.objects.filter(cliente_convertido=None)
            self.fields['preclientes'].initial = preclientes
            
        
    designado = forms.ModelChoiceField(required=True, queryset=None, label="Novo Designado", empty_label=None)
    clientes = forms.ModelMultipleChoiceField(required=False, queryset=Cliente.objects.filter(ativo=True))
    preclientes = forms.ModelMultipleChoiceField(required=False, queryset=PreCliente.objects.filter(cliente_convertido=None))

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def designacoes_confirmar(request):
    if request.POST:
        if request.POST.get('analisar-desginacoes-btn'):
            clientes_id = request.POST.getlist('clientes')
            clientes = Cliente.objects.filter(id__in=clientes_id, ativo=True)
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
        gerente = kwargs.pop('gerente', False)
        super(ConfigurarPropostaComercialParaImpressao, self).__init__(*args, **kwargs)
        if gerente:
            self.fields['vendedor'] = forms.ModelChoiceField(queryset=Funcionario.objects.exclude(user__perfilacessocomercial=None).exclude(user__funcionario__periodo_trabalhado_corrente=None), label="Vendedor")
            if self.instance.cliente and self.instance.cliente.designado:
                vendedor = self.instance.cliente.designado
            else:
                vendedor = self.instance.precliente.designado
            self.fields['vendedor'].initial = vendedor
        # 
        self.fields['nome_do_proposto'].required = True
        self.fields['rua_do_proposto'].required = True
        self.fields['bairro_do_proposto'].required = True
        self.fields['cidade_do_proposto'].required = True
        self.fields['endereco_obra_proposto'].required = True
        self.fields['representante_legal_proposto'].required = True
        self.fields['telefone_contato_proposto'].required = True
        self.fields['objeto_proposto'].required = True
        self.fields['descricao_items_proposto'].required = True
        self.fields['items_nao_incluso'].required = True
        
    
    def clean(self):
        cleaned_data = super(ConfigurarPropostaComercialParaImpressao, self).clean()
        representante_legal = cleaned_data.get("representante_legal_proposto")
        if self.instance and self.instance.cliente:
            if self.instance.cliente.tipo == "pj" and not representante_legal:
                raise ValidationError(u"Erro! Para clientes do tipo Pessoa Jurídica é obrigatório um Representante Legal!")
        return cleaned_data

    class Meta:
        model = PropostaComercial
        fields = 'nome_do_proposto', 'documento_do_proposto', 'cep_do_proposto', 'rua_do_proposto', 'bairro_do_proposto', \
        'cidade_do_proposto', 'estado_do_proposto', 'endereco_obra_proposto', 'representante_legal_proposto', \
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
            footer.drawOn(canvas, 30, 10)
            # Release the canvas
            canvas.restoreState()
    
    def print_proposta(self, proposta, tipo='servico', perfil=None):
        
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
            styles.add(ParagraphStyle(name='centered_h1', alignment=TA_CENTER, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))
            styles.add(ParagraphStyle(name='left_h1', alignment=TA_LEFT, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left_h2', alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='right', alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name='right_h2', alignment=TA_RIGHT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='justify', alignment=TA_JUSTIFY))

            # Our container for 'Flowable' objects
            elements = []
            # logo empresa
            if perfil.empresa:
                im = Image(perfil.empresa.logo.path, width=2*inch,height=1*inch,kind='proportional')
            else:
                im = Image(getattr(settings, 'IMG_PATH_LOGO_EMPRESA'), width=2*inch,height=1*inch,kind='proportional')
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
                texto_endereco = u"%s, <strong>Bairro</strong>: %s, <strong>CEP</strong>: %s, <strong>Cidade</strong>: %s, <strong>Estado</strong>: %s" % \
                    (proposta.rua_do_proposto, proposta.bairro_do_proposto, proposta.cep_do_proposto, proposta.cidade_do_proposto, proposta.estado_do_proposto)
                texto = u"<b>Cliente</b>: %s<br />\
            	<b>Telefone</b>: %s<br />\
            	<b>Endereço do Cliente</b>: %s <br />"% (
                        proposta.nome_do_proposto, proposta.telefone_contato_proposto, 
                        texto_endereco
                    )
                contratante_p = Paragraph(texto, styles['justify'])
                elements.append(contratante_p)
                
                if proposta.email_proposto:
                    texto = u"<b>Email</b>: %s<br />" % proposta.email_proposto
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
                # espaco
                elements.append(Spacer(1, 12))
                # objeto texto
                texto_objeto_p = Paragraph(proposta.objeto_proposto.replace('\n', '<br />'), styles['justify'])
                elements.append(texto_objeto_p)
                
                # space
                elements.append(Spacer(1, 24))
                
                # 1.1 - Descrição dos Itens
                desc_itens_titulo = Paragraph("1.1 - DESCRIÇÃO DOS ITENS", styles['left_h2'])
                elements.append(desc_itens_titulo)
                # space
                elements.append(Spacer(1, 12))
                
                # objeto texto
                # 1.1 - Descrição dos Itens
                desc_itens_titulo = Paragraph("1.1.1 - ITENS INCLUSOS", styles['left_h2'])
                elements.append(desc_itens_titulo)
                # space
                elements.append(Spacer(1, 12))
                
                
                texto_desc_itens_p = Paragraph(proposta.descricao_items_proposto.replace('\n', '<br />'), styles['justify'])
                elements.append(texto_desc_itens_p)
                
                # space
                elements.append(Spacer(1, 12))
                
                
                # 1.2 - Descrição dos Itens Não Inclusos
                desc_itens_titulo = Paragraph("1.1.2 - ITENS NÃO INCLUSOS", styles['left_h2'])
                elements.append(desc_itens_titulo)
                # space
                elements.append(Spacer(1, 12))
                
                # objeto texto
                texto_desc_itens_p = Paragraph(proposta.items_nao_incluso.replace('\n', '<br />'), styles['justify'])
                elements.append(texto_desc_itens_p)
                # space
                elements.append(Spacer(1, 12))
                
                                
                # 2 - Do valor e formas de pagamento
                titulo = Paragraph("2 - DOS VALORES", styles['left_h2'])
                elements.append(titulo)
                # space
                elements.append(Spacer(1, 12))
                
                
                locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")
                valor_formatado = locale.currency(proposta.valor_proposto, grouping=True)
                texto = "O valor global da proposta é de <strong>%s</strong> (<em>%s</em>)" % (valor_formatado, proposta.valor_extenso())
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
                validade = "Essa proposta é válida até %s e foi emitida em %s" % \
                ( proposta.data_expiracao.strftime("%d/%m/%Y"), datetime.date.today().strftime("%d/%m/%Y"))
                texto = Paragraph(validade, styles['justify'])
                elements.append(texto)
                
                # space
                elements.append(Spacer(1, 24))
                
            # TEXTO ESQUERDA FINAL
            if perfil.user.funcionario:
                responsavel_proposta = perfil.user.funcionario
            else:
                responsavel_proposta = proposta.designado
            

            
            
            if perfil and perfil.imagem_assinatura:
                # space
                elements.append(Spacer(1, 12))
                
                try:
                    im = Image(perfil.imagem_assinatura.path, width=2*inch,height=1*inch,kind='proportional')
                    im.hAlign = 'LEFT'
                    elements.append(im)
                except:
                    pass
            
            texto_esquerda_final = "Atenciosamente,<br /><b>%s</b>" % responsavel_proposta
            
            if perfil.user.funcionario.sexo == "m":
                texto_esquerda_final += "<br />Consultor de Vendas<br />"
            else:
                texto_esquerda_final += "<br />Consultora de Vendas<br />"
                
            if perfil.user.funcionario.email or perfil.user.email:
                texto_esquerda_final += "Email: %s<br />" % perfil.user.funcionario.email or perfil.user.email
            
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


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def proposta_comercial_reabrir(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    id_original = proposta.id
    orcamentos = proposta.orcamento_set.all()
    # clona a proposta atual para uma nova, aberta
    proposta.id = None
    proposta.save()
    proposta.status = "aberta"
    # marca como reaberta
    proposta.reaberta = True
    # nova data de expiracao
    proposta.data_expiracao = proposta.sugere_data_reagendamento_expiracao()
    proposta.valor_proposto = 0
    proposta.save()
    # registra followup falando que foi reaberto
    proposta.followupdepropostacomercial_set.create(texto="Reaberto de Proposta #%s" % id_original, criado_por=request.user.funcionario)
    if request.GET['next']:
        return redirect(request.GET['next'])
    else: 
        return redirect(reverse('comercial:home'))
        

@user_passes_test(possui_perfil_acesso_comercial)
def proposta_comercial_editar_item_documento(request, proposta_id, item_id):
    if request.POST:
        proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
        item = get_object_or_404(ItemGrupoDocumento, pk=item_id)
        form = item.formulario(request=request)
        if form.is_valid():
            form.save()

    return redirect(reverse('comercial:proposta_comercial_imprimir', args=[proposta_id]))



# cria form que edita multiplos textos editaveis
from django.forms.models import modelformset_factory

TextosEditaveisFormBase = modelformset_factory(ItemGrupoDocumento, extra=0, fields=('texto', 'imagem'))

# now we want to add a checkbox so we can do stuff to only selected items
class TextosEditaveisForm(TextosEditaveisFormBase):
  # this is where you can add additional fields to a ModelFormSet
  # this is also where you can change stuff about the auto generated form
  def __init__(self, *args, **kwargs):
    super(TextosEditaveisForm, self).__init__(*args, **kwargs)
    no_of_forms = len(self)
    for i in range(0, no_of_forms):
        self[i].fields['texto'].label = "Grupo %s Item %s - TEXTO: %s" % (self[i].instance.grupo.peso, self[i].instance.peso, self[i].instance.titulo_label())
        self[i].fields['imagem'].label = "Grupo %s Item %s - IMAGEM: %s" % (self[i].instance.grupo.peso, self[i].instance.peso, self[i].instance.titulo_label())
        if not self[i].instance.texto_editavel:
            self[i].fields['texto'].widget = forms.HiddenInput()
        if not self[i].instance.imagem_editavel:
           self[i].fields['imagem'].widget = forms.HiddenInput()

class DocumentoGeradoPrint:
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
            footer = Paragraph('<Br /><br/>POP CO 001-F01<br />REV-00%s' % self.documento.versao, styles['Normal'])
            footer.wrap(doc.width, doc.bottomMargin)
            footer.drawOn(canvas, 30, 10)
            # Release the canvas
            canvas.restoreState()

    def print_documento(self, documento, perfil=None):
            self.documento = documento
            self.perfil = perfil
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
            styles.add(ParagraphStyle(name='centered_h1', alignment=TA_CENTER, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))
            styles.add(ParagraphStyle(name='left_h1', alignment=TA_LEFT, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left_h2', alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='centered_h2', alignment=TA_CENTER, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='right', alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name='right_h2', alignment=TA_RIGHT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='justify', alignment=TA_JUSTIFY))

            # Our container for 'Flowable' objects
            elements = []
            # logo empresa
            if perfil.empresa:
                im = Image(perfil.empresa.logo.path, width=2*inch,height=1*inch,kind='proportional')
            else:
                im = Image(getattr(settings, 'IMG_PATH_LOGO_EMPRESA'), width=2*inch,height=1*inch,kind='proportional')
            im.hAlign = 'LEFT'

            # id da proposta
            if documento.propostacomercial:
                id_documento = Paragraph("Nº PROPOSTA: %s" % str(documento.propostacomercial.id), styles['right'])
            else:
                id_documento = Paragraph("Nº CONTRATO: %s" % str(documento.contratofechado.id), styles['right'])

            imprime_logo = getattr(self.documento, 'imprime_logo', False)
            if imprime_logo:
                data=[(im,id_documento)]
            else:
                data=[('',id_documento)]

            table_logo = Table(data, colWidths=270, rowHeights=79)
            table_logo.setStyle(TableStyle([('VALIGN',(-1,-1),(-1,-1),'MIDDLE')]))
            elements.append(table_logo)
            elements.append(Spacer(1, 12))
            # para cada grupo
            for grupo in self.documento.grupodocumento_set.all():
                # para cada item de cada grupo
                for item in grupo.itemgrupodocumento_set.all():
                    # objeto texto
                    if item.titulo:
                        if item.titulo_centralizado:
                            estilo = 'centered_h2'
                        else:
                            estilo = 'left_h2'
                        desc_itens_titulo = Paragraph(item.titulo, styles[estilo])
                        elements.append(desc_itens_titulo)
                    if item.imagem:
                        #img = utils.ImageReader(item.imagem.path)
                        #iw, ih = img.getSize()
                        #aspect = ih / float(iw)
                        #im = Image(item.imagem.path,  width=19*cm, height=(19*cm * aspect))
                        im = Image(item.imagem.path)
                        elements.append(im)
                    if item.texto:
                        texto = Paragraph(item.texto.replace('\n', '<br />'), styles['justify'])
                        elements.append(texto)

                    if item.quebra_pagina:
                        elements.append(PageBreak())
                    elements.append(Spacer(1, 10))

                elements.append(Spacer(1, 12))
                            # texto validade
                if documento.propostacomercial:
                    validade = "Essa proposta é válida até %s e foi emitida em %s" % \
                    ( documento.propostacomercial.data_expiracao.strftime("%d/%m/%Y"), datetime.date.today().strftime("%d/%m/%Y"))
                    texto = Paragraph(validade, styles['justify'])
                    elements.append(texto)
                    # TEXTO ESQUERDA FINAL
            if perfil.user.funcionario:
                responsavel_proposta = perfil.user.funcionario
            else:
                # id da proposta
                if documento.propostacomercial:
                    responsavel_proposta = documento.propostacomercial.designado
                else:
                    responsavel_proposta = documento.contratofechado.responsavel

            if perfil and perfil.imagem_assinatura:
                # space
                elements.append(Spacer(1, 12))

                try:
                    im = Image(perfil.imagem_assinatura.path, width=2*inch,height=1*inch,kind='proportional')
                    im.hAlign = 'LEFT'
                    elements.append(im)
                except:
                    pass

                texto_esquerda_final = "Atenciosamente,<br /><b>%s</b>" % responsavel_proposta

                if perfil.user.funcionario.sexo == "m":
                    texto_esquerda_final += "<br />Consultor de Vendas<br />"
                else:
                    texto_esquerda_final += "<br />Consultora de Vendas<br />"

                if perfil.user.funcionario.email or perfil.user.email:
                    texto_esquerda_final += "Email: %s<br />" % perfil.user.funcionario.email or perfil.user.email

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
                texto_direita_final = """
                Aceito por <br /><br /> ____________________________________________<br /><br />
                Em ___________ de _____________________ de %s.""" % (datetime.date.today().strftime("%Y"))

                texto_direita_final_p = Paragraph(texto_direita_final, styles['left'])

                data=[(texto_esquerda_final_p,texto_direita_final_p)]
                table = Table(data, colWidths=270, rowHeights=79)

                elements.append(table)

            # build pdf
            doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer, canvasmaker=NumberedCanvas)

            # Get the value of the BytesIO buffer and write it to the response.
            pdf = buffer.getvalue()
            buffer.close()
            return pdf


@user_passes_test(possui_perfil_acesso_comercial)
def proposta_comercial_imprimir(request, proposta_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    # mantem propostas antigas no esquema antigo
    if not proposta.documento_gerado:
        # redireciona pra view antiga
        return redirect(reverse("comercial:proposta_comercial_imprimir2", args=[proposta.id]))

    # puxa todos os itens dessa proposta que sao editaveis
    itens_editaveis = ItemGrupoDocumento.objects.filter(
        (Q(texto_editavel=True)| Q(imagem_editavel=True)) & \
        Q(grupo__documento__propostacomercial=proposta)
    ).order_by('grupo__peso', 'peso').distinct()
    if proposta.cliente:
         email_inicial = proposta.cliente.email
    else:
        email_inicial = None
    # instancia formulario de envio por email
    enviar_proposta_email = FormEnviarPropostaEmail(initial={'email': email_inicial})

    if request.POST:
        form_textos_editaveis = TextosEditaveisForm(request.POST, request.FILES, queryset=itens_editaveis)
        if form_textos_editaveis.is_valid():
            form_textos_editaveis.save()

    else:
        if request.GET.get('imprimir'):
            messages.info(request, "Documento Impresso Gerado")
            # Create the HttpResponse object with the appropriate PDF headers.
            response = HttpResponse(content_type='application/pdf')
            nome_arquivo_gerado = "proposta-%s.pdf" % proposta.id
            response['Content-Disposition'] = 'attachment; filename="%s"' % nome_arquivo_gerado
            buffer = BytesIO()
            report = DocumentoGeradoPrint(buffer, 'Letter')
            perfil = request.user.perfilacessocomercial
            pdf = report.print_documento(proposta.documento_gerado, perfil=perfil)
            response.write(pdf)
            return response
        form_textos_editaveis = TextosEditaveisForm(queryset=itens_editaveis)

    # busca modelos pra esta proposta
    modelos_proposta = DocumentoGerado.objects.filter(
        modelo=True,
        tipo_proposta=proposta.tipo,
        tipo='proposta',
        empresa_vinculada=request.user.perfilacessocomercial.empresa
    )
    if not modelos_proposta:
        modelos_proposta = DocumentoGerado.objects.filter(
            modelo=True,
            tipo_proposta=proposta.tipo,
            tipo='proposta',
            empresa_vinculada=None
        )
    return render_to_response('frontend/comercial/comercial-configurar-proposta-para-imprimir.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial)
def proposta_comercial_imprimir_gerar_documento(request, proposta_id, documento_id):
    proposta = get_object_or_404(PropostaComercial, pk=proposta_id)
    modelo_documento = get_object_or_404(DocumentoGerado, pk=documento_id)
    if proposta.documento_gerado:
        proposta.documento_gerado.delete()
        messages.info(request, "Documento Apagado")
    proposta.cria_documento_gerado(modelo=modelo_documento)
    messages.info(request, u"Documento Gerado")
    return redirect(reverse('comercial:proposta_comercial_imprimir', args=[proposta_id]))

@user_passes_test(possui_perfil_acesso_comercial)
def proposta_comercial_imprimir2(request, proposta_id):
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

    #    pega o endreco principal
    try:
        endereco_principal = proposta.cliente.enderecocliente_set.first()
    except:
        endereco_principal = None
    # rua
    if endereco_principal:
        if not proposta.rua_do_proposto and endereco_principal.rua:
            proposta.rua_do_proposto = "%s - %s" % (
                endereco_principal.rua, endereco_principal.numero
            )
        # bairro
        if not proposta.bairro_do_proposto and endereco_principal.bairro_texto:
            proposta.bairro_do_proposto = endereco_principal.bairro_texto

        # CEP
        if not proposta.cep_do_proposto  and endereco_principal.cep:
            proposta.cep_do_proposto = endereco_principal.cep

        # cidade
        if not proposta.cidade_do_proposto  and endereco_principal.cidade_texto:
            proposta.cidade_do_proposto = endereco_principal.cidade_texto

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

    #proposta.save()
    # modelos de texto
    modelo_objeto = getattr(settings, 'MODELOS_OBJETO_CONTRATO', None)
    modelo_garantia = getattr(settings, 'MODELOS_GARANTIA_CONTRATO', None)
    # modelos de texto
    modelo_itens_inclusos = getattr(settings, 'MODELOS_ITENS_INCLUSOS', None)
    modelo_itens_nao_inclusos = getattr(settings, 'MODELOS_ITENS_NAO_INCLUSOS', None)


    dicionario_template_propostas = getattr(settings, 'DICIONARIO_DE_LOCAL_DE_PROPOSTA', {})
    form_configura = ConfigurarPropostaComercialParaImpressao(instance=proposta, gerente=request.user.perfilacessocomercial.gerente)
    if request.POST:
        form_configura = ConfigurarPropostaComercialParaImpressao(request.POST, instance=proposta, gerente=request.user.perfilacessocomercial.gerente)
        if form_configura.is_valid():
            proposta = form_configura.save()
            proposta.save()
            # com tudo configurado, gera a proposta


            # nome do arquivo
            nome_arquivo_gerado = "proposta-%s.pdf" % proposta.id

            # Create the HttpResponse object with the appropriate PDF headers.
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="%s"' % nome_arquivo_gerado
            buffer = BytesIO()
            report = OrcamentoPrint(buffer, 'Letter')
            try:
                perfil = form_configura.cleaned_data['vendedor'].user.perfilacessocomercial
            except:
                perfil = request.user.perfilacessocomercial

            pdf = report.print_proposta(proposta, perfil=perfil)
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
                if request.user.funcionario.email:
                    dest.append(request.user.funcionario.email)
                assunto = "%s - Proposta Comercial %s" % (getattr(settings, "NOME_EMPRESA", "NOME DA EMPRESA"), proposta.id)
                conteudo = getattr(settings, "TEXTO_DO_EMAIL_COM_PROPOSTA_ANEXA", "Segue em anexo a proposta. ")
                try:
                    nome_do_proposto = form_configura.cleaned_data['representante_legal_proposto']
                    nome_do_funcionario = request.user.funcionario.nome
                    conteudo = conteudo % {'nome_do_proposto': nome_do_proposto, 'nome_do_funcionario': nome_do_funcionario}
                    bbc = [i[0] for i in PerfilAcessoComercial.objects.filter(gerente=True).values_list('user__funcionario__email')]
                except:
                    raise
                email = EmailMessage(
                        assunto,
                        conteudo,
                        settings.DEFAULT_FROM_EMAIL,
                        dest,
                        bbc,
                    )
                email.attach(nome_arquivo_gerado, pdf, 'application/pdf')
                try:
                    email.send(fail_silently=False)
                    messages.success(request, u'Sucesso! Proposta enviada para %s com sucesso.' % dest)
                    if bbc:
                        messages.info(request, u"Cópia Oculta enviada para: %s" % bbc)
                except:
                    messages.error(request, u'Atenção! Não foi enviado uma mensagem por email para os Gerentes!')

                return redirect(reverse("comercial:propostas_comerciais_minhas"))
            else:
                return response
            # descobre o template
            return render_to_response(template_escolhido, locals(), context_instance=RequestContext(request),)
    return render_to_response('frontend/comercial/comercial-configurar-proposta-para-imprimir2.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial)
def adicionar_follow_up(request, proposta_id):
    follow_up = False
    proposta = get_object_or_404(PropostaComercial, status="aberta", pk=proposta_id)
    if request.POST:
        form_adicionar_follow_up = FormAdicionarFollowUp(request.POST, perfil=request.user.perfilacessocomercial)
        if form_adicionar_follow_up.is_valid():
            follow_up = form_adicionar_follow_up.save(commit=False)
            follow_up.proposta = proposta
            follow_up.criado_por = request.user.funcionario
            follow_up.save()
        else:
            if request.POST.get('somente-texto'):
                follow_up, created = proposta.followupdepropostacomercial_set.create(texto=request.POST.get('texto'), criado_por=request.user.funcionario)
                # avisa que follow up foi criado
        if follow_up:
            messages.success(request, u"Sucesso! Novo Follow Up Adicionado na proposta")
        else:
            messages.error(request, u"Erro! Follow Up Não adicionado.")
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
    if request.user.perfilacessocomercial.super_gerente:
        meus_contratos = ContratoFechado.objects.all().order_by('responsavel').exclude(status="arquivado")
    else:
        if request.user.perfilacessocomercial.gerente:
            meus_contratos = ContratoFechado.objects.all().order_by('responsavel').exclude(status="arquivado").filter(
                responsavel__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
            )
        else:
            meus_contratos = ContratoFechado.objects.filter(responsavel=request.user.funcionario).order_by('status').exclude(status="arquivado")
    return render_to_response('frontend/comercial/comercial-contratos-meus.html', locals(), context_instance=RequestContext(request),)


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
        self.drawRightString(200 * mm, 15 * mm + (0.2 * inch),
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
            footer.drawOn(canvas, 30, 10)
            # Release the canvas
            canvas.restoreState()
    
    def print_contrato(self, contrato, testemunha1=None, testemunha2=None, imprime_logo=False, perfil=None):
            
        
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
            styles.add(ParagraphStyle(name='centered_h1', alignment=TA_CENTER, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))
            styles.add(ParagraphStyle(name='left_h1', alignment=TA_LEFT, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left_h1_vermelho', alignment=TA_LEFT, fontSize=13, fontName="Helvetica-Bold", textColor = colors.red,))
            styles.add(ParagraphStyle(name='left_h2', alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='right', alignment=TA_RIGHT, fontSize=10))
            styles.add(ParagraphStyle(name='right_h2', alignment=TA_RIGHT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='justify', alignment=TA_JUSTIFY))
            
            # Our container for 'Flowable' objects
            elements = []
            
            # logo empresa
            if perfil.empresa:
                im = Image(perfil.empresa.logo.path, width=2*inch,height=1*inch,kind='proportional')
            else:
                im = Image(getattr(settings, 'IMG_PATH_LOGO_EMPRESA'), width=2*inch,height=1*inch,kind='proportional')
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
            
            # mostra mensagem de status, menos se for emaberto ou lancado
            if contrato.status not in ('assinatura', 'emaberto', 'lancado'):
                # space
                elements.append(Spacer(1, 40))
                
                id_contrato_status_p = Paragraph(u"STATUS DO CONTRATO: %s" % contrato.get_status_display() , styles['left_h1_vermelho'])
                elements.append(id_contrato_status_p)
                
                elements.append(Spacer(1, 40))
                
                
            
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
            
            if contrato.endereco_obra:
                # space
                elements.append(Spacer(1, 12))                        
                # ENDERECO DA OBRA
                endereco_obra_p = Paragraph(u"<b>ENDEREÇO DA OBRA</b>: %s" % contrato.endereco_obra, styles['justify'])
                elements.append(endereco_obra_p)
            
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
            # space
            elements.append(Spacer(1, 12))
            # itens incluso texto
            itens_inclusos_p = Paragraph(unicode(contrato.items_incluso).replace("\n", "<br />"), styles['justify'])
            elements.append(itens_inclusos_p)
            # space
            elements.append(Spacer(1, 20))
            # itens N incluso titulo
            itens_n_incluso_titulo_p = Paragraph(". Itens não inclusos:", styles['left_h2'])
            elements.append(itens_n_incluso_titulo_p)
            # space
            elements.append(Spacer(1, 12))
            # itens N incluso texto
            itens_n_inclusos_p = Paragraph(unicode(contrato.items_nao_incluso).replace("\n", "<br />"), styles['justify'])
            elements.append(itens_n_inclusos_p)
            
            # space
            elements.append(Spacer(1, 20))
            
            #
            # CLAUSULA 2 - NORMAS DE EXECUÇÃO
            #
            clausula_2_p = Paragraph(u"CLÁUSULA 2ª - DIREITOS E OBRIGAÇÕES DA CONTRATADA E CONTRATANTE", styles['left_h1'])
            elements.append(clausula_2_p)
            # space
            elements.append(Spacer(1, 12))
            if contrato.normas_execucao:
                normas_execucao_texto = unicode(contrato.normas_execucao)
            else:
                normas_execucao_texto = str(getattr(settings, "TEXTO_NORMAS_EXECUCAO", "Settings: TEXTO_NORMAS_EXECUCAO - Texto descrevendo as normas de execução do contrato"))
            normas_execucao_p = Paragraph(normas_execucao_texto.replace("\n", "<br />"), styles['justify'])
            elements.append(normas_execucao_p)
            
            elements.append(Spacer(1, 12))
            
            #
            # CLAUSULA 3 - FORMAS DE PAGAMENTO
            #
            clausula_3_p = Paragraph("CLÁUSULA 3ª – DO VALOR E FORMA DE PAGAMENTO", styles['left_h1'])
            elements.append(clausula_3_p)

            # space
            if contrato.conta_transferencia:
                elements.append(Spacer(1, 12))
                conta_transferencia_p = Paragraph(unicode(u"Conta Para Transferência: %s" % contrato.conta_transferencia), styles['justify'])
                elements.append(conta_transferencia_p)


            elements.append(Spacer(1, 12))

            for lancamento in contrato.lancamentofinanceiroreceber_set.all():
                observacao = ''
                if lancamento.observacao_recebido:
                    observacao = u" Observação: %s " % lancamento.observacao_recebido
                lancamento_text = u"<b>Parcela %s</b> de R$ %s no dia %s na forma de %s.%s" % (lancamento.peso, lancamento.valor_cobrado, lancamento.data_cobranca.strftime("%d/%m/%y"), lancamento.get_modo_recebido_display(), observacao)
                lancamento_p = Paragraph(unicode(lancamento_text).replace("\n", "<br />"), styles['justify'])
                elements.append(lancamento_p)
                elements.append(Spacer(1, 12))
            
            import locale
            locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")
            valor_formatado = locale.currency(contrato.valor, grouping=True)
            
            total_texto = u"Total: %s (%s)" % (valor_formatado.decode('utf-8'), contrato.valor_extenso().decode('utf-8'))
            total_p = Paragraph(total_texto.replace("\n", "<br />"), styles['left_h2'])
            elements.append(total_p)
            elements.append(Spacer(1, 12))
                
            #
            # CLÁUSULA 4ª – DOS PRAZOS
            #
            clausula_4_p = Paragraph("CLÁUSULA 4ª – DOS PRAZOS", styles['left_h1'])
            elements.append(clausula_4_p)
            # space
            elements.append(Spacer(1, 12))
            
            if contrato.prazo_execucao:
                prazos_texto = unicode(contrato.prazo_execucao)
            else:
                prazos_texto = str(getattr(settings, "TEXTO_HTML_PRAZOS", "Settings: TEXTO_HTML_PRAZOS - Texto descrevendo as normas de execução do contrato"))
            
            prazos_p = Paragraph(prazos_texto.replace("\n", "<br />"), styles['justify'])
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
            if contrato.rescisao:
                rescisao_texto = unicode(contrato.rescisao)
            else:
                rescisao_texto = str(getattr(settings, "TEXTO_HTML_RESCISAO", "Settings: TEXTO_HTML_RESCISAO - Texto descrevendo as normas de Execucao"))
            rescisao_p = Paragraph(rescisao_texto.replace("\n", "<br />"), styles['justify'])
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
            if contrato.foro:
                foro_texto = unicode(contrato.foro)
            else:
                foro_texto = str(getattr(settings, "TEXTO_HTML_FORO", "Settings: TEXTO_HTML_FORO - Texto descrevendo O FORO do contrato"))
            foro_p = Paragraph(foro_texto.replace("\n", "<br />"), styles['justify'])
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
            representante_linha = Paragraph(str("_"*90), styles['justify'])
            elements.append(representante_linha)
            representante_empresa = getattr(settings, "REPRESENTATE_LEGAL_EMPRESA", "Settings: REPRESENTATE_LEGAL_EMPRESA - Texto descrevendo Representante Legal da Empresa")    
            representante_p = Paragraph(str(representante_empresa), styles['left'])
            elements.append(representante_p)
            
            # CLIENTE / PROPOSTO LEGAL
            #
            elements.append(Spacer(1, espaco_assinaturas))
            cliente_linha = Paragraph(str("_"*90), styles['justify'])
            elements.append(cliente_linha)
            representante_p = Paragraph(unicode(contrato.sugerir_texto_contratante()), styles['left'])
            elements.append(representante_p)
            
            # TESTEMUNHA 1
            #
            elements.append(Spacer(1, espaco_assinaturas))
            testemunha_linha = Paragraph(str("_"*90), styles['justify'])
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
            testemunha_linha = Paragraph(str("_"*90), styles['justify'])
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




class ContratoPrintDocumento:
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
            footer = Paragraph('<Br /><br/>POP CO 001-F01<br />REV-00%s' % self.documento.versao, styles['Normal'])
            footer.wrap(doc.width, doc.bottomMargin)
            footer.drawOn(canvas, 30, 10)
            # Release the canvas
            canvas.restoreState()

    def print_contrato(self, contrato, testemunha1=None, testemunha2=None, imprime_logo=False, perfil=None):

            self.contrato = contrato
            self.documento = contrato.documento_gerado
            self.perfil = perfil
            self.espaco_assinaturas = 30
            espaco_assinaturas = self.espaco_assinaturas
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
            styles.add(ParagraphStyle(name='centered_h1', alignment=TA_CENTER, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))
            styles.add(ParagraphStyle(name='left_h1', alignment=TA_LEFT, fontSize=13, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='left_h1_vermelho', alignment=TA_LEFT, fontSize=13, fontName="Helvetica-Bold", textColor = colors.red,))
            styles.add(ParagraphStyle(name='left_h2', alignment=TA_LEFT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='centered_h2', alignment=TA_CENTER, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='right', alignment=TA_RIGHT, fontSize=10))
            styles.add(ParagraphStyle(name='right_h2', alignment=TA_RIGHT, fontSize=10, fontName="Helvetica-Bold"))
            styles.add(ParagraphStyle(name='justify', alignment=TA_JUSTIFY))

            # Our container for 'Flowable' objects
            elements = []
            espaco_assinaturas = 30
            # logo empresa
            if perfil.empresa:
                im = Image(perfil.empresa.logo.path, width=2*inch,height=1*inch,kind='proportional')
            else:
                im = Image(getattr(settings, 'IMG_PATH_LOGO_EMPRESA'), width=2*inch,height=1*inch,kind='proportional')
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

            # para cada grupo
            for grupo in self.documento.grupodocumento_set.all():
                # para cada item de cada grupo
                for item in grupo.itemgrupodocumento_set.all():
                    # objeto texto
                    if item.titulo:
                        if item.titulo_centralizado:
                            estilo = 'centered_h2'
                        else:
                            estilo = 'left_h2'
                        desc_itens_titulo = Paragraph(item.titulo, styles[estilo])
                        elements.append(desc_itens_titulo)
                    if item.texto:
                        texto = Paragraph(item.texto.replace('\n', '<br />'), styles['justify'])
                        elements.append(texto)
                    if item.imagem:
                        elements.append(Spacer(1, 10))
                        #img = utils.ImageReader(item.imagem.path)
                        #iw, ih = img.getSize()
                        #aspect = ih / float(iw)
                        #im = Image(item.imagem.path,  width=19*cm, height=(19*cm * aspect))
                        im = Image(item.imagem.path)
                        elements.append(im)
                    if item.quebra_pagina:
                        elements.append(PageBreak())
                    elements.append(Spacer(1, 10))

                elements.append(Spacer(1, 12))

            # TESTEMUNHA 1
            #
            elements.append(Spacer(1, self.espaco_assinaturas))
            testemunha_linha = Paragraph(str("_"*90), styles['justify'])
            elements.append(testemunha_linha)
            if testemunha1:
                texto = "TESTEMUNHA 1, Nome: %s, CPF: %s" % (testemunha1, testemunha1.cpf)
            else:
                if contrato.responsavel_comissionado:
                    texto = u"TESTEMUNHA 1, Nome: %s, CPF: %s" % (contrato.responsavel_comissionado, contrato.responsavel_comissionado.cpf)
                else:
                    texto = u"TESTEMUNHA 1"
            testemunha_texto = Paragraph(unicode(texto), styles['left'])
            elements.append(testemunha_texto)

            # TESTEMUNHA 2
            #
            elements.append(Spacer(1, espaco_assinaturas))
            testemunha_linha = Paragraph(str("_"*90), styles['justify'])
            elements.append(testemunha_linha)
            if testemunha2:
                texto = u"TESTEMUNHA 2, Nome: %s, CPF: %s" % (testemunha2, testemunha2.cpf)
            else:
                texto = u"TESTEMUNHA 2"
            testemunha_texto = Paragraph(unicode(texto), styles['left'])
            elements.append(testemunha_texto)

            # REPRESENTANTE LEGAL EMPRESA
            #

            elements.append(Spacer(1, espaco_assinaturas))
            representante_linha = Paragraph(str("_"*90), styles['justify'])
            elements.append(representante_linha)
            empresa = self.contrato.responsavel.user.perfilacessocomercial.empresa
            representante_empresa = u"REPRESENTANTE LEGAL DA EMPRESA: %s - CPF: %s" % (empresa.responsavel_legal, empresa.responsavel_legal_cpf)
            representante_p = Paragraph(representante_empresa, styles['left'])
            elements.append(representante_p)
            # CONTRATANTE
            #
            elements.append(Spacer(1, espaco_assinaturas))
            representante_linha = Paragraph(str("_"*90), styles['justify'])
            elements.append(representante_linha)
            representante_empresa = u"CONTRATANTE: %s" % (self.contrato.cliente.sugerir_texto_contratante())
            representante_p = Paragraph(representante_empresa, styles['left'])
            elements.append(representante_p)


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
        contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status__in=["assinatura", "emaberto", "emanalise"])
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="CONTRATO-%s.pdf"' % contrato.id

    buffer = BytesIO()
    # manter compatibilidade com contratos sem documentos gerados
    if contrato.documento_gerado:
        report = ContratoPrintDocumento(buffer, 'Letter')
    else:
        report = ContratoPrint(buffer, 'Letter')
    if request.GET.get('testemunha1'):
        testemunha1 = Funcionario.objects.get(pk=int(request.GET.get('testemunha1')))
    else:
        testemunha1 = None
    if request.GET.get('testemunha2'):
        testemunha2 = Funcionario.objects.get(pk=int(request.GET.get('testemunha2')))
    else:
        testemunha2 = None
    if testemunha1 and testemunha2:
        if testemunha1 == testemunha2:
            messages.error(request, "Erro! Impossível testemunhas iguais para gerar a impressão do contrato!")
            return redirect(reverse("comercial:contratos_meus"))
    imprime_logo = request.GET.get('imprime_logo')
    pdf = report.print_contrato(contrato, testemunha1=testemunha1, testemunha2=testemunha2, imprime_logo=imprime_logo, perfil=request.user.perfilacessocomercial)
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
        esconde_textos = kwargs.pop('esconde_textos')
        super(FormRevalidarContrato, self).__init__(*args, **kwargs)
        self.fields['valor'].localize = True
        self.fields['valor'].widget.is_localized = True
        self.fields['documento_proposto_legal'] = BRCPFField()

        if esconde_textos:
            del self.fields['objeto']
            del self.fields['garantia']
            del self.fields['items_incluso']
            del self.fields['items_nao_incluso']

    class Meta:
        model = ContratoFechado
        fields = ('objeto', 'valor', 'garantia', 'categoria', 'items_incluso', 'items_nao_incluso', 'tipo', 'responsavel_comissionado', 'responsavel', 'nome_proposto_legal', 'documento_proposto_legal', 'apoio_tecnico', 'endereco_obra')
        #fields = 'categoria', 'objeto', 'garantia', 'items_incluso', 'items_nao_incluso', 'valor', 'tipo',
        localized_fields = 'valor',


@user_passes_test(possui_perfil_acesso_comercial)
def contratos_meus_definir_assinado(request, contrato_id):
    # TODO: guardar a data de assinatura do contrato
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status="assinatura")
    contrato.status = "emaberto"
    contrato.save()
    return redirect(reverse("comercial:contratos_meus"))

@user_passes_test(possui_perfil_acesso_comercial)
def contratos_meus_arquivar(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status="emaberto")
    messages.success(request, u"Sucesso! Contrato #%s Arquivado" % contrato.pk)
    contrato.status = "arquivado"
    contrato.save()
    return redirect(reverse("comercial:contratos_meus"))

@user_passes_test(possui_perfil_acesso_comercial)
def contratos_meus_revalidar(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status="invalido")
    itens_editaveis = ItemGrupoDocumento.objects.filter(grupo__documento=contrato.documento_gerado, texto_editavel=True)
    form_textos_editaveis = TextosEditaveisForm(queryset=itens_editaveis)
    if contrato.documento_gerado:
        esconde_textos = True
    else:
        esconde_textos = False

    ConfigurarConversaoPropostaFormset = forms.models.inlineformset_factory(ContratoFechado, LancamentoFinanceiroReceber, extra=0, can_delete=True, form=LancamentoFinanceiroReceberComercialForm)
    if request.POST:
        form_contrato = FormRevalidarContrato(request.POST, instance=contrato, esconde_textos=esconde_textos)
        form_configurar_contrato = ConfigurarConversaoPropostaFormset(request.POST, prefix="revalidar_contrato", instance=contrato)
        form_textos_editaveis = TextosEditaveisForm(request.POST, queryset=itens_editaveis)
        if form_contrato.is_valid() and form_configurar_contrato.is_valid() and form_textos_editaveis.is_valid():
            total_lancamentos = 0
            for form in form_configurar_contrato.forms:
                if form.cleaned_data:
                    if not form.cleaned_data['DELETE']:
                        total_lancamentos += float(form.cleaned_data['valor_cobrado'])
            if float(total_lancamentos) == float(contrato.valor):
                contrato = form_contrato.save(commit=False)
                # salva contrato em novo status
                contrato.status = "emanalise"
                contrato.save()
                # salva textos
                form_textos_editaveis.save()
                # salva configuracao de lancamentos
                form_configurar_contrato.save()
                messages.success(request, u"Sucesso! Contrato Revalidado")
                # envia email para gerentes do comercial
                dest = []
                # filtra por empresa
                gerentes_minha_empresa = PerfilAcessoComercial.objects.filter(gerente=True, empresa=request.user.perfilacessocomercial.empresa)

                for perfil in gerentes_minha_empresa:
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
                diferenca = float(contrato.valor) - float(total_lancamentos)
                messages.error(request, u"Erro! Valor de Lançamentos (R$ %s) é diferente do valor do Contrato (R$ %s). Diferença: R$ %s" % (total_lancamentos, contrato.valor, diferenca))
            
    else:
        form_contrato = FormRevalidarContrato(instance=contrato,  esconde_textos=esconde_textos)
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
            if request.POST.get('notacao'):
                novo_modelo.interpreta_notacao(request.POST.get('notacao'))
                novo_modelo.reajusta_custo()
            return redirect(reverse("comercial:orcamentos_modelo_editar", args=[novo_modelo.id]))
    else:
        form_adicionar_modelo = FormAdicionaModelo()
    return render_to_response('frontend/comercial/comercial-orcamentos-modelo-novo.html', locals(), context_instance=RequestContext(request),)


class ListaProduto(forms.Form):
    
    produto = forms.ChoiceField(widget=forms.HiddenInput())
    

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo(request):
    lista_produtos = ListaProduto()
    if request.GET.get('produto', None):
        modelos = Orcamento.objects.filter(ativo=True, modelo=True, linharecursomaterial__produto__id=request.GET.get('produto', None))
    else:
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


class ModeloOrcamentoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ModeloOrcamentoForm, self).__init__(*args, **kwargs)
        self.fields['descricao'].widget.attrs['class'] = "input-xxlarge"
        self.fields['descricao'].required = True
        self.fields['inicio_promocao'].widget.attrs['class'] = 'datepicker'
        self.fields['fim_promocao'].widget.attrs['class'] = 'datepicker'


    class Meta:
        model = Orcamento
        fields = 'ativo', 'descricao', 'tabelado', 'promocao', 'inicio_promocao', 'fim_promocao', 'custo_total', 'custo_material', 'custo_humano'



class LinhaOrcamentoMaterialForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LinhaOrcamentoMaterialForm, self).__init__(*args, **kwargs)
        self.fields['produto'].widget = forms.HiddenInput()
        self.fields['produto'].widget.attrs['class'] = 'select2-ajax-material'
        self.fields['quantidade'].widget.attrs['class'] = 'recalcula_quantidade_quando_muda'

    class Meta:
        model = LinhaRecursoMaterial
        fields = 'quantidade', 'produto'

class LinhaOrcamentoMaterialModeloForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LinhaOrcamentoMaterialModeloForm, self).__init__(*args, **kwargs)
        self.fields['produto'].widget = forms.HiddenInput()
        self.fields['produto'].widget.attrs['class'] = 'select2-ajax-material'
        self.fields['quantidade'].widget.attrs['class'] = 'recalcula_quantidade_quando_muda input-mini'
        self.fields['custo_total'].widget.attrs['class'] = 'recalcula_quantidade_quando_muda input-mini'
        self.fields['custo_total'].localize = True
        self.fields['custo_total'].widget.is_localized = True

    class Meta:
        model = LinhaRecursoMaterial
        fields = 'quantidade', 'produto', 'custo_total'
        localized_fields = 'custo_total',




class LinhaOrcamentoHumanoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LinhaOrcamentoHumanoForm, self).__init__(*args, **kwargs)
        self.fields['cargo'].widget = forms.HiddenInput()
        self.fields['cargo'].widget.attrs['class'] = 'select2-ajax-humano'
        self.fields['quantidade'].widget.attrs['class'] = 'recalcula_quantidade_quando_muda'

    class Meta:
        model = LinhaRecursoHumano
        fields = 'quantidade', 'cargo'


class LinhaOrcamentoHumanoModeloForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(LinhaOrcamentoHumanoModeloForm, self).__init__(*args, **kwargs)
        self.fields['cargo'].widget = forms.HiddenInput()
        self.fields['cargo'].widget.attrs['class'] = 'select2-ajax-humano'
        self.fields['quantidade'].widget.attrs['class'] = 'recalcula_quantidade_quando_muda input-mini'
        self.fields['custo_total'].widget.attrs['class'] = 'recalcula_quantidade_quando_muda input-mini'

        

    class Meta:
        model = LinhaRecursoHumano
        fields = 'quantidade', 'cargo', 'custo_total'



@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo_editar(request, modelo_id):
    
    orcamento = get_object_or_404(Orcamento, pk=modelo_id)
    OrcamentoMaterialFormSet = forms.models.inlineformset_factory(Orcamento, LinhaRecursoMaterial, extra=1, can_delete=True, form=LinhaOrcamentoMaterialModeloForm)
    OrcamentoRecursoHumanoFormSet = forms.models.inlineformset_factory(Orcamento, LinhaRecursoHumano, extra=1, can_delete=True, form=LinhaOrcamentoHumanoModeloForm)
    if request.POST:
        

        if 'adicionar_linha_material' in request.POST:
            
            try:
                quantidade_material_adicionar = int(request.POST.get('quantidade_material', 1))
            except:
                quantidade_material_adicionar = int(1)
            
            
            messages.info(request, u"Nova Linha de Materiais adicionada")
            cp = request.POST.copy()
            form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(cp, instance=orcamento, prefix='orcamento-humano')
            cp['orcamento-material-TOTAL_FORMS'] = int(cp['orcamento-material-TOTAL_FORMS'])+ quantidade_material_adicionar
            form_editar_linhas_material = OrcamentoMaterialFormSet(cp, instance=orcamento, prefix='orcamento-material')
            form_orcamento = OrcamentoForm(cp, instance=orcamento)

        if 'adicionar_linha_humano' in request.POST:
            
            try:
                quantidade_humano_adicionar = int(request.POST.get('quantidade_humano', 1))
            except:
                quantidade_humano_adicionar = int(1)
            
            
            messages.info(request, u"Nova Linha de Mão de Obra adicionada")
            cp = request.POST.copy()
            form_editar_linhas_material = OrcamentoMaterialFormSet(cp, instance=orcamento, prefix='orcamento-material')
            cp['orcamento-humano-TOTAL_FORMS'] = int(cp['orcamento-humano-TOTAL_FORMS'])+ quantidade_humano_adicionar   
            form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(cp, instance=orcamento, prefix='orcamento-humano')
            form_orcamento = OrcamentoForm(cp, instance=orcamento)
        
        
        
        
        
        elif 'alterar-orcamento' in request.POST:
            form_editar_linhas_material = OrcamentoMaterialFormSet(request.POST, instance=orcamento, prefix="orcamento-material")
            form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(request.POST, instance=orcamento, prefix="orcamento-humano")
            form_orcamento = ModeloOrcamentoForm(request.POST, instance=orcamento)
            if form_editar_linhas_material.is_valid() and form_editar_linhas_humano.is_valid() and form_orcamento.is_valid():
                linhas_material = form_editar_linhas_material.save()
                linhas_humano = form_editar_linhas_humano.save()
                orcamento = form_orcamento.save()
                if orcamento.proposta:
                    messages.success(request, u"Sucesso! Orçamento (%s) Alterado da Proposta #%s" % (orcamento.descricao, orcamento.proposta.id))
                    # se cliente, mostra ficha
                    return redirect(reverse('comercial:editar_proposta', args=[orcamento.proposta.id]))
                else:
                    messages.success(request, u"Sucesso! Orçamento (%s) Alterado" % (orcamento.descricao))
                    return redirect(reverse('comercial:orcamentos_modelo_editar', args=[orcamento.id]))
            else:
                form_orcamento = ModeloOrcamentoForm(request.POST, instance=orcamento)
        
                
    else:
        form_editar_linhas_material = OrcamentoMaterialFormSet(instance=orcamento, prefix="orcamento-material")
        form_editar_linhas_humano = OrcamentoRecursoHumanoFormSet(instance=orcamento, prefix="orcamento-humano")
        form_orcamento = ModeloOrcamentoForm(instance=orcamento)

    return render_to_response('frontend/comercial/comercial-orcamentos-modelo-editar.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo_gerenciar(request, modelo_id):
    modelo = get_object_or_404(Orcamento, pk=modelo_id)
    return render_to_response('frontend/comercial/comercial-orcamentos-modelo-gerenciar.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo_reajustar(request, modelo_id):
    orcamento = get_object_or_404(Orcamento, modelo=True, pk=modelo_id)
    reajustou = orcamento.reajusta_custo()
    if reajustou:
        messages.warning(request, u"Atenção! Houve Reajuste de uma das linhas do Modelo %s!" % orcamento)
    else:
        messages.success(request, u"Não houveram reajustes de preço para o Modelo %s" % orcamento)

    return redirect(reverse("comercial:orcamentos_modelo"))


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def orcamentos_modelo_apagar(request, modelo_id):
    orcamento = get_object_or_404(Orcamento, modelo=True, pk=modelo_id)
    orcamento.ativo = False
    orcamento.save()
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
    # propostas 
    # propostas fechadas
    total_propostas_perdidas = []

    # contratos
    contratos_em_analise = ContratoFechado.objects.filter(
        status='emanalise',
        cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
    )
    contratos_aguardando_assinatura = ContratoFechado.objects.filter(
        status='assinatura',
        cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
    )


    for month in range(1,13):
        # preclientes criados
        preclientes_no_mes = PreCliente.objects.filter(
            criado__year=ano, criado__month=month,
            designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
        ).count()
        total_preclientes_criados.append(preclientes_no_mes)
        # preclientes convertidos
        preclientes_covnertidos_no_mes = PreCliente.objects.filter(
            data_convertido__year=ano, data_convertido__month=month,
            designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
        ).count()
        total_preclientes_convertidos.append(preclientes_covnertidos_no_mes)
        # propostas criadas
        propostas_criadas_mes = PropostaComercial.objects.filter(
            criado__year=ano, criado__month=month,
        ).filter(
            Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
            Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        contagem_propostas_criadas_mes = propostas_criadas_mes.count()
        valores_propostas_criadas_mes = propostas_criadas_mes.aggregate(Sum('valor_proposto'))['valor_proposto__sum'] or 0
        total_propostas_criadas.append((contagem_propostas_criadas_mes, valores_propostas_criadas_mes))
        # propostas convertidas
        propostas_convertidas_mes = PropostaComercial.objects.filter(
            definido_convertido_em__year=ano, definido_convertido_em__month=month
        ).filter(
            Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
            Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        contagem_propostas_convertidas_mes = propostas_convertidas_mes.count()
        valores_propostas_convertidas_mes = propostas_convertidas_mes.aggregate(Sum('valor_proposto'))['valor_proposto__sum'] or 0
        total_propostas_convertidas.append((contagem_propostas_convertidas_mes, valores_propostas_convertidas_mes))
        # propostas perdidas
        propostas_perdidas_mes = PropostaComercial.objects.filter(
            definido_perdido_em__year=ano, definido_perdido_em__month=month
        ).filter(
            Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
            Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        contagem_propostas_criadas_mes = propostas_perdidas_mes.count()
        valores_propostas_criadas_mes = propostas_perdidas_mes.aggregate(Sum('valor_proposto'))['valor_proposto__sum'] or 0
        total_propostas_perdidas.append((contagem_propostas_criadas_mes, valores_propostas_criadas_mes))

    # propostas abertas não expiradas
    propostas_abertas_nao_expiradas = PropostaComercial.objects.filter(
        status="aberta", data_expiracao__gte=datetime.date.today()
    ).filter(
        Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
        Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
    )
    propostas_abertas_nao_expiradas_contagem = propostas_abertas_nao_expiradas.count()
    propostas_abertas_nao_expiradas_por_criador = propostas_abertas_nao_expiradas.values('criado_por__nome').annotate(Count('id'), Sum('valor_proposto'))
    propostas_abertas_nao_expiradas_por_responsavel = propostas_abertas_nao_expiradas.values('designado__nome').annotate(Count('id'), Sum('valor_proposto'))
    propostas_abertas_nao_expiradas_total = propostas_abertas_nao_expiradas.aggregate(Sum('valor_proposto'))['valor_proposto__sum']    

    # propostas abertas expiradas
    propostas_abertas_expiradas = PropostaComercial.objects.filter(
        status="aberta", data_expiracao__lt=datetime.date.today()
    ).filter(
        Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
        Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
    )
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
    
    # Modelo de Orcamento com Propostas Abertas
    modelos = Orcamento.objects.filter(modelo=True)
    
    # Modelo de Orcamento Tabelado em Propostas Abertas
    total_propostas_gerados_tabelado_abertas = {}
    for modelo in Orcamento.objects.filter(modelo=True, tabelado=True).all():
        grupo_month_set = []
        for month in range(1,13):
            quantidades = Orcamento.objects.filter(
                ativo=True,
                proposta__status="aberta",
                proposta__criado__year=ano,
                proposta__criado__month=month,
            ).exclude(Q(tabelado_originario=None)).filter(
                Q(proposta__cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(proposta__precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        ).count()
            grupo_month_set.append(quantidades)
        total_propostas_gerados_tabelado_abertas[modelo.descricao] = grupo_month_set
    total_propostas_gerados_tabelado_abertas = OrderedDict(sorted(total_propostas_gerados_tabelado_abertas.items(), key=lambda t: t[0]))
    
    # Modelo de Orcamento Tabelado em Propostas Fechada
    total_propostas_gerados_tabelado_fechadas = {}
    for modelo in Orcamento.objects.filter(modelo=True, tabelado=True).all():
        grupo_month_set = []
        for month in range(1,13):
            quantidades = Orcamento.objects.filter(
                ativo=True,
                proposta__status__in=['perdida', 'perdida_aguardando'],
                proposta__criado__year=ano,
                proposta__criado__month=month,
            ).exclude(Q(tabelado_originario=None)).filter(
                Q(proposta__cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(proposta__precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        ).count()
            grupo_month_set.append(quantidades)
        total_propostas_gerados_tabelado_fechadas[modelo.descricao] = grupo_month_set
    total_propostas_gerados_tabelado_fechadas = OrderedDict(sorted(total_propostas_gerados_tabelado_fechadas.items(), key=lambda t: t[0]))
    
    
    # Modelo de Orcamento Promocional em Proposta Aberta
    total_propostas_gerados_promocionais_abertas = {}
    for modelo in Orcamento.objects.filter(modelo=True, promocao=True).all():
        grupo_month_set = []
        for month in range(1,13):
            quantidades = Orcamento.objects.filter(
                ativo=True,
                proposta__status="aberta",
                proposta__criado__year=ano,
                proposta__criado__month=month,
            ).exclude(Q(promocao_originaria=None)).filter(
                Q(proposta__cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(proposta__precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        ).count()
            grupo_month_set.append(quantidades)
        total_propostas_gerados_promocionais_abertas[modelo.descricao] = grupo_month_set
    total_propostas_gerados_promocionais_abertas = OrderedDict(sorted(total_propostas_gerados_promocionais_abertas.items(), key=lambda t: t[0]))
    
    # Modelo de Orcamento Promocional em Proposta Fechada
    total_propostas_gerados_promocionais_fechadas = {}
    for modelo in Orcamento.objects.filter(modelo=True, promocao=True).all():
        grupo_month_set = []
        for month in range(1,13):
            quantidades = Orcamento.objects.filter(
                ativo=True,
                proposta__status__in=['perdida', 'perdida_aguardando'],
                proposta__criado__year=ano,
                proposta__criado__month=month,
            ).exclude(
                Q(promocao_originaria=None)
            ).filter(
                Q(proposta__cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(proposta__precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        ).count()
            grupo_month_set.append(quantidades)
        total_propostas_gerados_promocionais_fechadas[modelo.descricao] = grupo_month_set
    total_propostas_gerados_promocionais_fechadas = OrderedDict(sorted(total_propostas_gerados_promocionais_fechadas.items(), key=lambda t: t[0]))
    
    
    return render_to_response('frontend/comercial/comercial-indicadores.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial(request):
    return render_to_response('frontend/comercial/comercial-relatorios.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial_propostas_por_periodo_e_vendedor(request):

    erro = False
    try:
        de = request.GET.get('de', None)
        if de:
            de = datetime.datetime.strptime(de, '%d/%m/%Y')
        ate = request.GET.get('ate', None)
        if ate:
            ate = datetime.datetime.strptime(ate, '%d/%m/%Y')
            ate = datetime.datetime(ate.year, ate.month, ate.day, 23, 59, 59)
        if de and ate and ate < de:
            raise
    except:
        messages.error(request, "Intervalo de datas errado")
        erro = True
    if not erro:
        if de and ate:
            propostas = PropostaComercial.objects.filter(criado__range=(de,ate)).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        elif de and not ate:
            de = datetime.datetime.combine(de, datetime.time(00, 00))
            propostas = PropostaComercial.objects.filter(criado__gte=de).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        elif not de and ate:
            ate = datetime.datetime.combine(ate, datetime.time(23, 59))
            propostas = PropostaComercial.objects.filter(criado__lte=ate).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
    try:
        propostas = propostas.order_by('designado')
    except:
        pass
        
    return render_to_response('frontend/comercial/comercial-relatorios-propostas-por-dia.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial_propostas_visitas(request):
    erro = False
    try:
        de = request.GET.get('de', None)
        if de:
            de = datetime.datetime.strptime(de, '%d/%m/%Y')
        ate = request.GET.get('ate', None)
        if ate:
            ate = datetime.datetime.strptime(ate, '%d/%m/%Y')
            ate = datetime.datetime(ate.year, ate.month, ate.day, 23, 59, 59)
        if de and ate and ate < de:
            raise
    except:
        messages.error(request, "Intervalo de datas errado")
        erro = True
    if not erro:
        fups = FollowUpDePropostaComercial.objects.filter(
                Q(proposta__cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(proposta__precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        if de and ate:
            fups = fups.filter(criado__range=(de,ate), visita=True)
        elif de and not ate:
            de = datetime.datetime.combine(de, datetime.time(00, 00))
            fups = fups.filter(criado__gte=de, visita=True)
        elif not de and ate:
            ate = datetime.datetime.combine(ate, datetime.time(23, 59))
            fups = fups.filter(criado__lte=ate, visita=True)

    return render_to_response('frontend/comercial/comercial-relatorios-followups-visita.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def relatorios_comercial_probabilidade(request):
    try:
        probabilidade = int(request.GET.get('probabilidade'))
    except:
        probabilidade = 70
    agrupador = request.GET.get('agrupador', 'tipo')
    propostas = PropostaComercial.objects.filter(probabilidade__gte=probabilidade, status="aberta").filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )

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
    propostas = PropostaComercial.objects.annotate(num_fup=Count('followupdepropostacomercial')).filter(num_fup=followup_n).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
    
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
            propostas = PropostaComercial.objects.filter(definido_perdido_em__range=(de,ate), status__in=['perdida', 'perdida_aguardando']).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        elif de and not ate:
            de = datetime.datetime.combine(de, datetime.time(00, 00))
            propostas = PropostaComercial.objects.filter(definido_perdido_em__gte=de, status__in=['perdida', 'perdida_aguardando']).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        elif not de and ate:
            ate = datetime.datetime.combine(ate, datetime.time(23, 59))
            propostas = PropostaComercial.objects.filter(definido_perdido_em__lte=ate, status__in=['perdida', 'perdida_aguardando']).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        else:
            propostas = PropostaComercial.objects.filter(status__in=['perdida', 'perdida_aguardando']).filter(
                Q(cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa) | \
                Q(precliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa)
        )
        
        if agrupador == "tipo":
            propostas = propostas.order_by('tipo')
        elif agrupador == "funcionario":
            propostas = propostas.order_by('designado')
        
    
            
    return render_to_response('frontend/comercial/comercial-relatorios-propostas-declinadas.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_comercial_gerente)
def analise_de_contratos(request):
    if request.user.perfilacessocomercial.super_gerente:
        contratos_em_analise = ContratoFechado.objects.filter(
            status="emanalise",
        ).order_by('responsavel')
    else:
        contratos_em_analise = ContratoFechado.objects.filter(
            status="emanalise",
            cliente__designado__user__perfilacessocomercial__empresa=request.user.perfilacessocomercial.empresa
        )
    return render_to_response('frontend/comercial/comercial-analise-de-contratos.html', locals(), context_instance=RequestContext(request),)

class FormAnalisarContrato(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        perfil = kwargs.pop('perfil')
        super(FormAnalisarContrato, self).__init__(*args, **kwargs)
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        self.fields['responsavel_comissionado'].queryset = perfil.funcionarios_disponiveis()
        self.fields['responsavel_comissionado'].widget.attrs['class'] = 'select2'
        self.fields['responsavel'].widget.attrs['class'] = 'select2'
        self.fields['responsavel'].queryset = perfil.funcionarios_disponiveis()
        self.fields['apoio_tecnico'].widget.attrs['class'] = 'select2'
        self.fields['apoio_tecnico'].queryset = perfil.funcionarios_disponiveis()
        self.fields['documento_proposto_legal'] =  BRCPFField()
        if self.instance.documento_gerado:
            self.fields['objeto'].widget = forms.HiddenInput()
            self.fields['objeto'].initial = 'objeto do documento gerado'
            self.fields['nome_proposto_legal'].widget = forms.HiddenInput()
            self.fields['nome_proposto_legal'].required = False
            self.fields['nome_proposto_legal'].initial = 'objeto do documento gerado'
            self.fields['documento_proposto_legal'].widget = forms.HiddenInput()
            self.fields['documento_proposto_legal'].required = False
            self.fields['endereco_obra'].widget = forms.HiddenInput()
            self.fields['endereco_obra'].required = False

    class Meta:
        model = ContratoFechado
        fields = ('objeto', 'categoria', 'responsavel_comissionado', 'responsavel', 'nome_proposto_legal', 'documento_proposto_legal', 'apoio_tecnico', 'endereco_obra')

@user_passes_test(possui_perfil_acesso_comercial_gerente)
def analise_de_contratos_analisar(request, contrato_id):
    contrato = get_object_or_404(ContratoFechado, pk=contrato_id, status="emanalise")
    textos_contrato = ItemGrupoDocumento.objects.filter(grupo__documento__contratofechado=contrato)
    if request.POST:
        form_analisar_contrato = FormAnalisarContrato(request.POST, instance=contrato, perfil=request.user.perfilacessocomercial)
        if form_analisar_contrato.is_valid():
            contrato = form_analisar_contrato.save()
            if request.POST.get('aterar-contrato'):
                messages.success(request, u"Sucesso! Contrato em Análise #%s  Alterado." % contrato.pk)
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
        form_analisar_contrato = FormAnalisarContrato(instance=contrato, perfil=request.user.perfilacessocomercial)
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
