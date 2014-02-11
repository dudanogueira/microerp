# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from comercial.models import ContratoFechado

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
# VIEWS
#

@user_passes_test(possui_perfil_acesso_programacao, login_url='/')
def home(request):
    contratos = ContratoFechado.objects.filter(status='lancado').order_by('status_execucao')
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