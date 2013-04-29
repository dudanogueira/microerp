from datetime import datetime
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader, Context

from django.contrib.auth.forms import AuthenticationForm

from cadastro.models import Recado
from rh.models import Funcionario

def home(request):
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