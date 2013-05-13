# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse

from django.db import models

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.db.models import Count

from rh.models import Departamento
from comercial.models import SolicitacaoComercial, ContatoComercial, TipoContatoComercial, FonteDeAgendaComercial
from cadastro.models import Cliente, PreCliente

from django.conf import settings

from rh import utils

from django.http import HttpResponse

# forms
from forms import ContatoComercialAdd

from django.contrib.auth.decorators import user_passes_test

# COMERCIAL DECORATORS
def possui_perfil_acesso_comercial(user, login_url="/"):
    try:
        if user.perfilacessocomercial and user.funcionario.periodo_trabalhado_corrente:
            return True
    except:
        return False

# HOME
@login_required
@user_passes_test(possui_perfil_acesso_comercial, login_url='/')
def home(request):
    # widget cliente
    cliente_q = request.GET.get('cliente', False)
    if cliente_q:
        clientes = Cliente.objects.filter(nome__icontains=cliente_q)
        preclientes = PreCliente.objects.filter(nome__icontains=cliente_q, cliente_convertido=None) 
    
    return render_to_response('frontend/comercial/comercial-home.html', locals(), context_instance=RequestContext(request),)


@login_required
def contato_comercial_list(request):
    semanas_proximas = utils.get_weeks(weeks=3)
    weekview = []
    for semana in semanas_proximas:
        start_date = datetime.datetime.combine(semana[0], datetime.time(23,59))
        end_date = datetime.datetime.combine(semana[-1], datetime.time(23,59))
        weekview_text = (start_date, end_date)
        objs = ContatoComercial.objects.filter(
        (models.Q(inicio__gt=start_date) & models.Q(inicio__lt=end_date)) |
        (models.Q(fim__lt=end_date) & models.Q(fim__gt=start_date)) |
        (models.Q(inicio__lt=start_date) & models.Q(fim__gt=end_date)) |
        (models.Q(inicio__gt=start_date) & models.Q(fim__lt=end_date))
        ).order_by('inicio')
        weekview.append((weekview_text, objs))

    # para a agenda
    fontes_de_agenda = FonteDeAgendaComercial.objects.filter(funcionario=request.user.get_profile())
    return render_to_response('comercial/contato-comercial-list.html', locals(), context_instance=RequestContext(request),)

@login_required
def contato_comercial_agenda_api(request, agenda_id):
    agenda = FonteDeAgendaComercial.objects.get(id=agenda_id, funcionario=request.user.get_profile())
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    start_date = datetime.datetime.fromtimestamp(int(start))+datetime.timedelta(1)
    end_date = datetime.datetime.fromtimestamp(int(end))+datetime.timedelta(1)
    tipo_contato = agenda.tipo
    contatos = agenda.filtra_intervalo(start_date, end_date)
    out_items = [i.json_event_object() for i in contatos]
    return HttpResponse("[%s]" % ",".join(out_items), mimetype="application/json")

@login_required
def detalhes_evento_html(request):
    pk = request.GET.get('id', None)
    evento = get_object_or_404(ContatoComercial, pk=pk, funcionario=request.user.get_profile())
    return render_to_response('comercial/contato-comercial-modal-detalhes.html', locals(), context_instance=RequestContext(request),)

@login_required
def contato_comercial_adicionar(request):
    # form add agenda
    if request.POST:
        form = ContatoComercialAdd(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.funcionario = request.user.get_profile()
            contato.save()
            return redirect(reverse("frontend:contato-comercial-list"))
    else:
        form = ContatoComercialAdd()
    return render_to_response('comercial/contato-comercial-adicionar.html', locals(), context_instance=RequestContext(request),)

@login_required
def cadastro_clientes_list(request):
    clientes = Cliente.objects.all()
    return render_to_response('comercial/cadastro-clientes-list.html', locals(), context_instance=RequestContext(request),)

@login_required
def cadastro_clientes_detalhe(request, id):
    cliente = get_object_or_404(Cliente, id=id, funcionario_responsavel=request.user.get_profile())
    return render_to_response('comercial/cadastro-clientes-detalhe.html', locals(), context_instance=RequestContext(request),)