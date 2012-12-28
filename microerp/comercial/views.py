import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse

from django.db import models

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.db.models import Count

from rh.models import Departamento
from comercial.models import SolicitacaoComercial, ContatoComercial, TipoContatoComercial
from cadastro.models import Cliente

from django.conf import settings

from rh import utils

from django.http import HttpResponse

# forms
from forms import ContatoComercialAdd

@login_required
def home(request):
      departamento = Departamento.objects.get(pk=settings.DEPARTAMENTO_COMERCIAL_ID)
      sc_aberta_total = SolicitacaoComercial.objects.filter(status="aberta").count()
      sc_perdida_total = SolicitacaoComercial.objects.filter(status="perdida").count()
      sc_convertida_total = SolicitacaoComercial.objects.filter(status="convertida").count()
      contatos_programados = ContatoComercial.objects.filter(status="programado")
      contatos_programados_total = contatos_programados.count()
      contatos_programados_stats_tipo = contatos_programados.values('tipo',).annotate(Count('tipo'))
      contatos_realizados_total = ContatoComercial.objects.filter(status="programado").count()
      return render_to_response('comercial/index.html', locals(), context_instance=RequestContext(request),)

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
    tipo_contatos_comerciais = TipoContatoComercial.objects.all()
    return render_to_response('comercial/contato-comercial-list.html', locals(), context_instance=RequestContext(request),)

@login_required
def contato_comercial_agenda_api(request, tipo):
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    start_date = datetime.datetime.fromtimestamp(int(start))+datetime.timedelta(1)
    end_date = datetime.datetime.fromtimestamp(int(end))+datetime.timedelta(1)
    tipo_contato = TipoContatoComercial.objects.get(pk=tipo)
    contatos = tipo_contato.get_from_range(start_date, end_date)
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
            return redirect(reverse("comercial:contato-comercial-list"))
    else:
        form = ContatoComercialAdd()
    return render_to_response('comercial/contato-comercial-adicionar.html', locals(), context_instance=RequestContext(request),)

@login_required
def cadastro_clientes_list(request):
    clientes = Cliente.objects.filter(funcionario_responsavel=request.user.get_profile())
    return render_to_response('comercial/cadastro-clientes-list.html', locals(), context_instance=RequestContext(request),)

@login_required
def cadastro_clientes_detalhe(request, id):
    cliente = get_object_or_404(Cliente, id=id, funcionario_responsavel=request.user.get_profile())
    return render_to_response('comercial/cadastro-clientes-detalhe.html', locals(), context_instance=RequestContext(request),)