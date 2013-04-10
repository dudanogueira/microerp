# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

# RH
from rh.models import Funcionario

from cadastro.models import Cliente, PreCliente

def home(request):
    # widget funcionario
    funcionario_q = request.GET.get('funcionario', False)
    if funcionario_q:
        funcionarios = Funcionario.objects.filter(nome__contains=funcionario_q)
    # widget cliente
    cliente_q = request.GET.get('cliente', False)
    if cliente_q:
        clientes = Cliente.objects.filter(nome__contains=cliente_q)
        preclientes = PreCliente.objects.filter(nome__contains=cliente_q, cliente_convertido=None) 
    return render_to_response('frontend/cadastro/cadastro-home.html', locals(), context_instance=RequestContext(request),)


def funcionarios_contatos_ver(request, funcionario_id):
    return render_to_response('frontend/cadastro/cadastro-funcionario-ver-contatos.html', locals(), context_instance=RequestContext(request),)
    
def funcionarios_list(request):
    funcionarios = Funcionario.objects.exclude(periodo_trabalhado_corrente=None)
    return render_to_response('frontend/cadastro/cadastro-funcionario-list.html', locals(), context_instance=RequestContext(request),)

def funcionarios_ver_recados(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)
    return render_to_response('frontend/cadastro/cadastro-funcionario-recados.html', locals(), context_instance=RequestContext(request),)
    
    