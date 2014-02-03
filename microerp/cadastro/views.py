# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import user_passes_test
from django.core.mail import EmailMessage

# SITES
from django.contrib.sites.models import Site
# RH
from rh.models import Funcionario, Departamento
# Cadastro
from cadastro.models import Cliente, PreCliente
from cadastro.models import Recado
# solicitacao
from solicitacao.models import Solicitacao
# comercial
from comercial.models import RequisicaoDeProposta, PerfilAcessoComercial

from django import forms
#
# FORMS
#

from django_select2.widgets import Select2Widget

from django_select2 import AutoModelSelect2Field


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
    
    avisar_departamento = forms.BooleanField(label="Avisar à todos", required=False)

    class Meta:
        model = Recado
        fields = ('texto', 'tipo', 'tipo_outros', 'remetente', 'cliente', 'destinatario', 'avisar_departamento')
    



class PreClienteAdicionarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        sugestao = kwargs.pop('sugestao')
        super(PreClienteAdicionarForm, self).__init__(*args, **kwargs)
        self.fields['designado'].empty_label = "Nenhum"
        ids_possiveis_responsaveis = PerfilAcessoComercial.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        self.fields['designado'].queryset = Funcionario.objects.filter(pk__in=ids_possiveis_responsaveis)
        
        
        if sugestao:
            self.fields['nome'].initial = sugestao
    
    class Meta:
        model = PreCliente
        fields = 'nome', 'contato', 'dados', 'designado'



#
# DECORATORS
#
def possui_perfil_acesso_recepcao(user, login_url="/"):
    try:
        if user.perfilacessorecepcao and user.funcionario.ativo():
            return True
    except:
        return False

#
# VIEWS
#
@user_passes_test(possui_perfil_acesso_recepcao)
def home(request):
    # widget funcionario
    funcionario_q = request.GET.get('funcionario', False)
    if funcionario_q:
        funcionarios = Funcionario.objects.filter(nome__icontains=funcionario_q)
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
    nao_lidos = Recado.objects.filter(destinatario=funcionario, lido=False)
    lidos = Recado.objects.filter(destinatario=funcionario, lido=True)
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
            recado.adicionado_por = request.user.funcionario
            recado.save()
            messages.success(request, u'Recado Adicionado com sucesso para o Remetente!')
            recados = []
            recados.append(recado)
            # clona e agrega todos os recados
            if form.cleaned_data['avisar_departamento']:
                for colega in funcionario.colegas_ativos_mesmo_dpto():
                    recado.id = None
                    recado.destinatario = colega
                    recado.save()
                    messages.success(request, u'Recado Copiado com sucesso para %s!' % colega)            
                    recados.append(recado)
            # MANDA EMAIL, SE POSSÍVEL            
            for recado in recados:
                dest = []
                # se possuir email, envia
                if recado.destinatario.email or recado.destinatario.user:
                    dest.append(recado.destinatario.email or recado.destinatario.user.email)
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
                        recado.email_enviado = True
                        recado.save()            
                        messages.success(request, u'Sucesso! Uma mensagem de email foi enviada para este recado!')
                    except:
                        messages.error(request, u'Atenção! Não foi enviado uma mensagem por email para este recado!')
                        recado.save()            
                # caso contrario, marca e avisa que nao enviou
                else:
                    recado.email_enviado = False
                    recado.save()
                    messages.error(request, u'Informação: Não foi enviado um email para este recado.')
                
            return redirect(reverse('cadastro:funcionarios_recados_listar', args=[funcionario_id]))

    else:    
        form = AdicionarRecadoForm(destinatario=funcionario.id, remetente=remetente_id)
    return render_to_response('frontend/cadastro/cadastro-funcionario-recados-adicionar.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_recepcao)
def recados_gerenciar(request):
    nao_lidos = Recado.objects.filter(lido=False)
    return render_to_response('frontend/cadastro/cadastro-gerenciar-recados.html', locals(), context_instance=RequestContext(request),)


#
# VIEWS EXTERNAS / COM MODULOS
#

@user_passes_test(possui_perfil_acesso_recepcao)
def preclientes_adicionar(request):
    if request.POST:
        try:
            form = form_add_precliente = PreClienteAdicionarForm(data=request.POST, sugestao=None)
            if form.is_valid():
                precliente = form.save(commit=False)
                precliente.adicionado_por = request.user.funcionario
                precliente.save()
                messages.success(request, u'Pré Cliente %s adicionado com sucesso!' % precliente)
                return redirect(reverse('cadastro:home'))
        except:
            raise
        
    else:
        sugestao = request.GET.get('sugestao', None)
        form_add_precliente = PreClienteAdicionarForm(sugestao=sugestao)
    return render_to_response('frontend/cadastro/cadastro-preclientes-adicionar.html', locals(), context_instance=RequestContext(request),)



@user_passes_test(possui_perfil_acesso_recepcao)
def solicitacao_adicionar(request):
    if not 'solicitacao' in settings.INSTALLED_APPS:
            messages.error(request, u'Modulo de Solicitações não instalado')
            return redirect(reverse('cadastro:home'))
    cliente_id = request.GET.get('cliente', None)
    precliente_id = request.GET.get('precliente', None)
    if request.POST:
        form = AdicionarSolicitacaoForm(request.POST, cliente=cliente_id, precliente=precliente_id)
        if form.is_valid():
            solicitacao = form.save()
            messages.success(request, 'Solicitação #%d criada com sucesso!' % solicitacao.id)
            return redirect(reverse('cadastro:home'))
    else:
        form = AdicionarSolicitacaoForm(cliente=cliente_id, precliente=precliente_id)
    return render_to_response('frontend/cadastro/cadastro-solicitacao-adicionar.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_recepcao)
def preclientes_listar(request):
    return render_to_response('frontend/cadastro/cadastro-preclientes-listar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_recepcao)
def requisicao_proposta_cliente(request):
    if request.POST:
        if request.POST.get('descricao-requisicao-proposta', None):
            try:
                cliente = get_object_or_404(Cliente, pk=request.POST.get('cliente-requisicao-proposta'))
                # adiciona requisicao
                requisicao = cliente.requisicaodeproposta_set.create(criado_por=request.user, descricao=request.POST.get('descricao-requisicao-proposta', None))
                messages.success(request, u"Requisição de Proposta para %s realizada para Funcionário %s" % (cliente, cliente.designado))
            except:
                raise
        else:
            messages.info(request, 'É obrigatório uma Descrição.')
    else:
        messages.info(request, u'Não pode ser acessado diretamente');
    return redirect(reverse("cadastro:home"))