# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.contrib import messages

from django.db.models import Q

from models import Ocorrencia
from rh.models import Funcionario, Departamento

from django import forms

# COMERCIAL DECORATORS
def possui_perfil_acesso_ocorrencia(user, login_url="/"):
    try:
        if user.perfilacessoocorrencia and user.funcionario.periodo_trabalhado_corrente:
            return True
    except:
        return False

def possui_perfil_acesso_ocorrencia_gerente(user, login_url="/"):
    try:
        if user.perfilacessoocorrencia and user.funcionario.periodo_trabalhado_corrente and user.perfilacessoocorrencia.gerente:
            return True
    except:
        return False


# FORM
class DespacharOcorrenciaForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(DespacharOcorrenciaForm, self).__init__(*args, **kwargs)
        self.fields['departamento_direto'].widget.attrs['class'] = 'select2'
        self.fields['departamentos_afetados'].widget.attrs['class'] = 'select2'
        self.fields['departamento_direto'].required = True
    
    class Meta:
        model = Ocorrencia
        fields = 'providencia', 'prioridade', 'departamento_direto', 'departamentos_afetados',




# HOME
@login_required
@user_passes_test(possui_perfil_acesso_ocorrencia, login_url='/')
def home(request):
    ocorrencias_aberta = Ocorrencia.objects.filter(
        Q(status="aberta") & (Q(responsavel_contato=None) | \
        Q(responsavel_correcao=None) | \
        Q(responsavel_visto=None))
    )
    ocorrencias_analise = Ocorrencia.objects.filter(status="analise")
    ocorrencias_contato = Ocorrencia.objects.filter(status="contato")
    ocorrencias_visto = Ocorrencia.objects.filter(status="visto")
    ocorrencias_fechada_procede_count = Ocorrencia.objects.filter(status="resolvida", procede=True).count()
    ocorrencias_fechada_nao_procede_count = Ocorrencia.objects.filter(status="resolvida", procede=False).count()
    return render_to_response('frontend/ocorrencia/ocorrencia-home.html', locals(), context_instance=RequestContext(request),)


# HOME
@login_required
@user_passes_test(possui_perfil_acesso_ocorrencia_gerente, login_url='/')
def despachar(request):
    funcionarios_ativos = Funcionario.objects.exclude(periodo_trabalhado_corrente=None).order_by('periodo_trabalhado_corrente__inicio')
    ocorrencias_abertas = Ocorrencia.objects.filter(status="aberta")
    return render_to_response('frontend/ocorrencia/ocorrencia-despachar.html', locals(), context_instance=RequestContext(request),)



# HOME
@login_required
@user_passes_test(possui_perfil_acesso_ocorrencia_gerente, login_url='/')
def despachar_ocorrencia(request, ocorrencia_id):
    ocorrencia = get_object_or_404(Ocorrencia, id=ocorrencia_id)
    if request.POST.get('despachar') or request.POST.get('improceder'):
        if request.POST.get('responsavel_correcao').isdigit():
            ocorrencia.responsavel_correcao_id = request.POST.get('responsavel_correcao', None)
        else:
            ocorrencia.responsavel_correcao_id = None
            messages.warning(request, u"Responsável por Correção por Indefinido")
            
        if request.POST.get('responsavel_contato').isdigit():
            ocorrencia.responsavel_contato_id = request.POST.get('responsavel_contato', None)
        else:
            ocorrencia.responsavel_contato_id = None
            messages.warning(request, u"Responsável por Contato por Indefinido")

        if request.POST.get('responsavel_visto').isdigit():
            ocorrencia.responsavel_visto_id = request.POST.get('responsavel_visto', None)
        else:
            ocorrencia.responsavel_visto_id = None
        ocorrencia.save()
        # procede
        procede = request.POST.get('despachar', None)
        if procede:
            messages.success(request, u"Ocorrência marcada como Procedente. Informe uma providência Abaixo.")
            ocorrencia_form = DespacharOcorrenciaForm(instance=ocorrencia)

        return render_to_response('frontend/ocorrencia/ocorrencia-despachar-ocorrencia.html', locals(), context_instance=RequestContext(request),)
    if request.POST.get('confirmar'):
        if request.POST.get('providencia', None) and request.POST.get('departamento_direto', None):
            if not ocorrencia.responsavel_contato or not ocorrencia.responsavel_correcao:
                messages.error(request, u"Erro. Necessário Definir um Responsável Para Correção e Contato para a Ocorrência #%d." % ocorrencia.id)
            else:
                # DESPACHA pra análise
                ocorrencia_form = DespacharOcorrenciaForm(request.POST, instance=ocorrencia)
                if ocorrencia_form.is_valid():
                    ocorrencia = ocorrencia_form.save()
                    ocorrencia.status = "analise" 
                    ocorrencia.despachado_por = request.user
                    ocorrencia.despachado_data = datetime.datetime.now()
                    ocorrencia.save()               
                    messages.info(request, u"Despachando... Procedente: %s" % request.POST.get('providencia', None))
                

        # nao procede
        elif request.POST.get('motivo_improcedencia', None):
            if not ocorrencia.responsavel_contato:
                messages.error(request, u"Erro. Necessário Definir um Responsável Para Contato para a Ocorrência #%d." % ocorrencia.id)
            else:
                messages.info(request, u"Despachando... IMProcedente: %s" % request.POST.get('motivo_improcedencia', None))
                ocorrencia.despachado_por = request.user
                ocorrencia.procede = False
                ocorrencia.nao_procede_porque = request.POST.get('motivo_improcedencia', None)
                ocorrencia.status = 'contato'
                ocorrencia.resolucao_final_data = datetime.datetime.now()
                ocorrencia.save()
        else:
            messages.error(request, u"Erro. Necessário Uma Providiência e Departamento Direto, ou Motivo de Improcedência para a Ocorrência #%d." % ocorrencia.id)

        return redirect(reverse("ocorrencia:despachar"))
    else:
        return redirect(reverse("ocorrencia:despachar"))