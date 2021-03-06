# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader, Context
from django.contrib.auth import logout

from django.db.models import Q

from django.contrib.auth.forms import AuthenticationForm

from cadastro.models import PerfilClienteLogin
from rh.models import Funcionario
from solicitacao.models import Solicitacao

from django import forms
# forms

class SolicitacaoResolvidaForm(forms.ModelForm):

    class Meta:
        model = Solicitacao
        fields = 'resolucao_final',

def home(request):
    next = request.GET.get('next', None)
    if request.user.is_authenticated():
        try:
            funcionario = request.user.funcionario
            return(redirect("interface_home_funcionario"))
        except:
            messages.error(request, 'ERRO! Acesso Exclusivo para Funcionários. Nenhum Funcionário Vinculado.')
            logout(request)
            return(redirect("login"))
        try:
            cliente_perfil = request.user.perfilclientelogin
            return(redirect("login"))
        except PerfilClienteLogin.DoesNotExist:
            messages.error(request, 'ERRO! Nenhum cliente ou funcionário Vinculado a esta conta')
            return(redirect("interface_home_funcionario"))

    else:
        form = AuthenticationForm()
        context = {
            'form': form
        }
        return render(request, 'registration/login.html', context)


def funcionario(request):
    if request.user.is_authenticated():
        try:
            funcionario = request.user.funcionario
            # verifica se o funcionario possui periodo de trabalho ativo
            if funcionario.periodo_trabalhado_corrente and funcionario.periodo_trabalhado_corrente.ativo():
                solicitacoes_abertas = Solicitacao.objects.filter(
                    Q(status="aberta") & Q(responsavel_contato=funcionario) | \
                    Q(responsavel_correcao=funcionario) | \
                    Q(responsavel_visto=funcionario)
                )
            else:
                messages.error(request, 'ERRO! Conta inativa')
                return(redirect("login"))

        except Funcionario.DoesNotExist:
            messages.error(request, 'ERRO! Nenhum funcionário vinculado a esta conta')
            return(redirect("login"))
    else:
        form = AuthenticationForm()

    return render(request, 'frontend/funcionario-home.html', locals())


def cliente(request):
    # esconde o menu lateral principal
    mostra_menu_principal_lateral = False
    if request.user.is_authenticated():
        try:
            funcionario = request.user.funcionario
            solicitacoes_abertas = Solicitacao.objects.filter(
                Q(status="aberta") & Q(responsavel_contato=funcionario) | \
                Q(responsavel_correcao=funcionario) | \
                Q(responsavel_visto=funcionario)
            )
        except Funcionario.DoesNotExist:
            pass
    else:
        form = AuthenticationForm()

    return render(request, 'frontend/cliente-home.html', locals())

def meus_recados(request):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    nao_lidos = Recado.objects.filter(destinatario=funcionario, lido=False)
    lidos = Recado.objects.filter(destinatario=funcionario, lido=True)
    enviados = Recado.objects.filter(remetente=funcionario)
    return render(request, 'frontend/main-meus-recados.html', locals())
def meus_recados_marcar_lido(request, recado_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    recado = get_object_or_404(Recado, destinatario=funcionario, pk=recado_id)
    recado.lido = True
    recado.lido_em = datetime.now()
    recado.save()

    messages.success(request, "Mensagem ID#%d marcado como lido!" % recado.id)
    return redirect(reverse('meus_recados'))


def minhas_solicitacoes(request):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    solicitacoes_correcao = funcionario.solicitacao_correcao_set.filter(status="analise")
    # pega solicitoes em status contato
    # solicitacoess status resolvidas, porem sem contato realizado
    solicitacoes_contato = funcionario.solicitacao_contato_set.filter(
        Q(status="contato") |
        Q(status="resolvida", contato_realizado=None)
    )

    solicitacoes_visto = funcionario.solicitacao_visto_set.filter(status="visto")
    return render(request, 'frontend/main-minhas-solicitacoes.html', locals())

def minhas_solicitacoes_resolvido(request, solicitacao_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id, responsavel_correcao=funcionario)
    if request.POST:
        form = SolicitacaoResolvidaForm(request.POST, instance=solicitacao)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.resolucao_final_data = datetime.now()
            solicitacao.status = 'contato'
            solicitacao.save()
            return redirect(reverse('minhas_solicitacoes'))
    else:
        form = SolicitacaoResolvidaForm(instance=solicitacao)
    return render(request, 'frontend/main-minhas-solicitacoes-resolvido.html', locals())

def minhas_solicitacoes_abrir_correcao(request, solicitacao_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id, responsavel_correcao=funcionario)
    if solicitacao.responsavel_correcao == funcionario:
        solicitacao.correcao_iniciada = datetime.now()
        solicitacao.save()
        messages.success(request, "Solicitação #%d Aberta para Correção" % solicitacao.id)
    return redirect(reverse('minhas_solicitacoes'))

def minhas_solicitacoes_fechar_contato(request, solicitacao_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id, responsavel_contato=funcionario)
    if solicitacao.responsavel_contato == funcionario:
        solicitacao.contato_realizado = datetime.now()
        solicitacao.status = 'visto'
        solicitacao.save()
    return redirect(reverse('minhas_solicitacoes'))

def minhas_solicitacoes_fechar_visto(request, solicitacao_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id, responsavel_visto=funcionario)
    if solicitacao.responsavel_visto == funcionario:
        solicitacao.visto_data = datetime.now()
        solicitacao.status = 'resolvida'
        solicitacao.save()
    return redirect(reverse('minhas_solicitacoes'))

def teste(request):
    from templated_docs import fill_template
    from templated_docs.http import FileResponse
    context = {
        'teste': 'okgo',
        'uai': 10.23,
        'v1': 56789,
        'v2': 2,
        'v3': 3,
        'v4': 4,
        'v5': 5,
        'v6': 6,
    }

    filename = fill_template('/code/teste.odt', context, output_format='docx')
    visible_filename = 'greeting.pdf'
    return FileResponse(filename, visible_filename)


class PasswordResetRequestForm(forms.Form):
    email_or_username = forms.CharField(label=("Usuário"), max_length=254)