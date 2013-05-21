# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.contrib import messages

from django.db.models import Q

from models import Solicitacao
from rh.models import Funcionario, Departamento

from django import forms

# COMERCIAL DECORATORS
def possui_perfil_acesso_solicitacao(user, login_url="/"):
    try:
        if user.perfilacessosolicitacao and user.funcionario.periodo_trabalhado_corrente:
            return True
    except:
        return False


def possui_perfil_acesso_solicitacao_gerente(user, login_url="/"):
    try:
        if user.perfilacessosolicitacao and user.funcionario.periodo_trabalhado_corrente and user.perfilacessosolicitacao.gerente:
            return True
    except:
        return False


# FORM
class DespacharSolicitacaoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(DespacharSolicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['departamento_direto'].widget.attrs['class'] = 'select2'
        self.fields['departamentos_afetados'].widget.attrs['class'] = 'select2'
        self.fields['departamento_direto'].required = True
    
    class Meta:
        model = Solicitacao
        fields = 'providencia', 'prioridade', 'departamento_direto', 'departamentos_afetados',



# HOME
@login_required
@user_passes_test(possui_perfil_acesso_solicitacao, login_url='/')
def home(request):
    solicitacoes_aberta = Solicitacao.objects.filter(
        Q(status="aberta") & (Q(responsavel_contato=None) | \
        Q(responsavel_correcao=None) | \
        Q(responsavel_visto=None))
    )
    solicitacoes_analise = Solicitacao.objects.filter(status="analise")
    solicitacoes_contato = Solicitacao.objects.filter(status="contato")
    solicitacoes_visto = Solicitacao.objects.filter(status="visto")
    solicitacoes_fechada_procede_count = Solicitacao.objects.filter(status="resolvida", procede=True).count()
    solicitacoes_fechada_nao_procede_count = Solicitacao.objects.filter(status="resolvida", procede=False).count()
    return render_to_response('frontend/solicitacao/solicitacao-home.html', locals(), context_instance=RequestContext(request),)



@login_required
@user_passes_test(possui_perfil_acesso_solicitacao_gerente, login_url='/')
def despachar(request):
    funcionarios_ativos = Funcionario.objects.exclude(periodo_trabalhado_corrente=None).order_by('periodo_trabalhado_corrente__inicio')
    solicitacoes_abertas = Solicitacao.objects.filter(status="aberta")
    return render_to_response('frontend/solicitacao/solicitacao-despachar.html', locals(), context_instance=RequestContext(request),)




@login_required
@user_passes_test(possui_perfil_acesso_solicitacao_gerente, login_url='/')
def despachar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, id=solicitacao_id)
    procede = request.POST.get('despachar', None)
    if request.POST.get('despachar') or request.POST.get('improceder'):
        if request.POST.get('responsavel_correcao').isdigit():
            solicitacao.responsavel_correcao_id = request.POST.get('responsavel_correcao', None)
        else:
            if procede:
                solicitacao.responsavel_correcao_id = None
                messages.warning(request, u"Responsável por Correção por Indefinido")
            
        if request.POST.get('responsavel_contato').isdigit():
            solicitacao.responsavel_contato_id = request.POST.get('responsavel_contato', None)
        else:
            solicitacao.responsavel_contato_id = None
            messages.warning(request, u"Responsável por Contato por Indefinido")

        if request.POST.get('responsavel_visto').isdigit():
            solicitacao.responsavel_visto_id = request.POST.get('responsavel_visto', None)
        else:
            solicitacao.responsavel_visto = request.user.funcionario
        solicitacao.save()
        # procede
        if procede:
            messages.success(request, u"Solicitação marcada como Procedente. Informe uma providência Abaixo.")
            solicitacao_form = DespacharSolicitacaoForm(instance=solicitacao)

        return render_to_response('frontend/solicitacao/solicitacao-despachar-solicitacao.html', locals(), context_instance=RequestContext(request),)
    if request.POST.get('confirmar'):
        if request.POST.get('providencia', None) and request.POST.get('departamento_direto', None):
            if not solicitacao.responsavel_contato or not solicitacao.responsavel_correcao:
                messages.error(request, u"Erro. Necessário Definir um Responsável Para Correção e Contato para a Solicitação #%d." % solicitacao.id)
            else:
                # DESPACHA pra análise
                solicitacao_form = DespacharSolicitacaoForm(request.POST, instance=solicitacao)
                if solicitacao_form.is_valid():
                    solicitacao = solicitacao_form.save()
                    solicitacao.status = "analise" 
                    solicitacao.despachado_por = request.user
                    solicitacao.despachado_data = datetime.datetime.now()
                    solicitacao.save()               
                    messages.info(request, u"Despachando... Procedente: %s" % request.POST.get('providencia', None))
                

        # nao procede
        elif request.POST.get('motivo_improcedencia', None):
            if not solicitacao.responsavel_contato:
                messages.error(request, u"Erro. Necessário Definir um Responsável Para Contato para a Solicitação #%d." % solicitacao.id)
            else:
                messages.info(request, u"Despachando... IMProcedente: %s" % request.POST.get('motivo_improcedencia', None))
                solicitacao.despachado_por = request.user
                solicitacao.procede = False
                solicitacao.nao_procede_porque = request.POST.get('motivo_improcedencia', None)
                solicitacao.status = 'contato'
                solicitacao.resolucao_final_data = datetime.datetime.now()
                solicitacao.save()
        else:
            messages.error(request, u"Erro. Necessário Uma Providiência e Departamento Direto, ou Motivo de Improcedência para a Solicitação #%d." % solicitacao.id)
            solicitacao.save()

        return redirect(reverse("solicitacao:despachar"))
    else:
        return redirect(reverse("solicitacao:despachar"))