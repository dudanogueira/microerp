# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader, Context

from django.db.models import Q

from django.contrib.auth.forms import AuthenticationForm

from cadastro.models import Recado
from rh.models import Funcionario
from ocorrencia.models import Ocorrencia

from django import forms
# forms

class OcorrenciaResolvidaForm(forms.ModelForm):
    
    class Meta:
        model = Ocorrencia
        fields = 'resolucao_final',

def home(request):
    if request.user.is_authenticated():
        try:
            funcionario = request.user.funcionario
            ocorrencias_abertas = Ocorrencia.objects.filter(
                Q(status="aberta") & Q(responsavel_contato=funcionario) | \
                Q(responsavel_correcao=funcionario) | \
                Q(responsavel_visto=funcionario)
            )
        except Funcionario.DoesNotExist:
            pass
    else:
        form = AuthenticationForm()
    
    return render_to_response('frontend/main-home.html', locals(), context_instance=RequestContext(request),)

def meus_recados(request):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    nao_lidos = Recado.objects.filter(destinatario=funcionario, lido=False)
    lidos = Recado.objects.filter(destinatario=funcionario, lido=True)
    enviados = Recado.objects.filter(remetente=funcionario)
    return render_to_response('frontend/main-meus-recados.html', locals(), context_instance=RequestContext(request),)

def meus_recados_marcar_lido(request, recado_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    recado = get_object_or_404(Recado, destinatario=funcionario, pk=recado_id)
    recado.lido = True
    recado.lido_em = datetime.now()
    recado.save()
    messages.success(request, "Mensagem ID#%d marcado como lido!" % recado.id)
    return redirect(reverse('meus_recados'))


def minhas_ocorrencias(request):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    ocorrencias_correcao = funcionario.ocorrencia_correcao_set.filter(status="analise")
    # pega ocorrencias em status contato
    # ocorrencias status resolvidas, porem sem contato realizado
    ocorrencias_contato = funcionario.ocorrencia_contato_set.filter(
        Q(status="contato") |
        Q(status="resolvida", contato_realizado=None)
    )
    
    ocorrencias_visto = funcionario.ocorrencia_visto_set.filter(status="visto")
    return render_to_response('frontend/main-minhas-ocorrencias.html', locals(), context_instance=RequestContext(request),)

def minhas_ocorrencias_resolvido(request, ocorrencia_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id, responsavel_correcao=funcionario)
    if request.POST:
        form = OcorrenciaResolvidaForm(request.POST, instance=ocorrencia)
        if form.is_valid():
            ocorrencia = form.save(commit=False)
            ocorrencia.resolucao_final_data = datetime.now()
            ocorrencia.status = 'contato'
            ocorrencia.save()
            return redirect(reverse('minhas_ocorrencias'))
    else:
        form = OcorrenciaResolvidaForm(instance=ocorrencia)
    return render_to_response('frontend/main-minhas-ocorrencias-resolvido.html', locals(), context_instance=RequestContext(request),)

def minhas_ocorrencias_abrir_correcao(request, ocorrencia_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id, responsavel_correcao=funcionario)
    if ocorrencia.responsavel_correcao == funcionario:
        ocorrencia.correcao_iniciada = datetime.now()
        ocorrencia.save()
        messages.success(request, "Ocorrência #%d Aberta para Correção" % ocorrencia.id)
    return redirect(reverse('minhas_ocorrencias'))

def minhas_ocorrencias_fechar_contato(request, ocorrencia_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id, responsavel_contato=funcionario)
    if ocorrencia.responsavel_contato == funcionario:
        ocorrencia.contato_realizado = datetime.now()
        ocorrencia.status = 'visto'
        ocorrencia.save()
    return redirect(reverse('minhas_ocorrencias'))

def minhas_ocorrencias_fechar_visto(request, ocorrencia_id):
    funcionario = get_object_or_404(Funcionario, user=request.user)
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id, responsavel_visto=funcionario)
    if ocorrencia.responsavel_visto == funcionario:
        ocorrencia.visto_data = datetime.now()
        ocorrencia.status = 'resolvida'
        ocorrencia.save()
    return redirect(reverse('minhas_ocorrencias'))