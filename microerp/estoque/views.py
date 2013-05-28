# -*- coding: utf-8 -*-
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm, cm

from django.http import HttpResponse

import datetime
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.conf import settings

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q

from estoque.models import Produto

from django_select2 import AutoModelSelect2MultipleField


#
# DECORADORES
#

def possui_perfil_acesso_estoque(user, login_url="/"):
    try:
        if user.perfilacessoestoque and user.funcionario.periodo_trabalhado_corrente:
            return True
    except:
        return False


def possui_perfil_acesso_estoque_gerente(user, login_url="/"):
    try:
        if user.perfilacessoestoque and user.funcionario.periodo_trabalhado_corrente and user.perfilacessoestoque.gerente and user.funcionario:
            return True
    except:
        return False


## FORMS

class SelecionaProdutosField(AutoModelSelect2MultipleField):
    queryset = Produto.objects
    search_fields = ['codigo', 'nome__icontains', 'descricao__icontains']

class SelecionaProdutos(forms.Form):
    produtos_adicionar = SelecionaProdutosField(label="Produtos para Adicionar:")

#
# VIEWS
#

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def home(request):
    return render_to_response('frontend/estoque/estoque-home.html', locals(), context_instance=RequestContext(request),)


# ETIQUETAS
@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas(request):
    if request.GET:
        produtos_adicionar = request.GET.getlist('produtos_adicionar')
        produtos_selecionados_get = request.GET.getlist('produtos_selecionados')
        produtos_selecionados = Produto.objects.filter(id__in=produtos_adicionar)

    form = SelecionaProdutos()
    return render_to_response('frontend/estoque/estoque-etiquetas.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas_configurar(request):
    if request.GET.get('todos', None):
        todos = True
    return render_to_response('frontend/estoque/estoque-etiquetas-configurar.html', locals(), context_instance=RequestContext(request),)


def geraPagina(formato, numeros, c, pagesize, SHOW_BORDER=False):
    w, h = pagesize
    for linha in range(formato['Linhas']):
        for coluna in range(formato['Colunas']):
            try:
                numero = numeros[linha][coluna]
            except IndexError:
                return
            x = formato['Esquerda']*cm + (formato['Horizontal']*cm * coluna)
            y = h - formato['Superior']*cm - (formato['Vertical']*cm * (linha+1))
            import string
            string = string.uppercase * 4
            string = numero.descricao
            c.drawString(x+4*mm, y+(20*mm), string[0:21])
            c.drawString(x+24*mm, y+(15*mm), string[21:35])
            c.drawString(x+24*mm, y+(10*mm), string[35:49])
            c.drawString(x+24*mm, y+(5*mm), string[49:64])
            if SHOW_BORDER:
                c.rect(x, y, formato['Largura']*cm, formato['Altura']*cm)

            barcode = code128.Code128(numero.codigo, barWidth=0.26*mm, barHeight=13*mm, 
                                      quiet=False, humanReadable=True)
            barcode.drawOn(c, x+(1*mm), y+(4*mm))


def _geraPaginaObjetos(formato, lista):
    l = []
    for linha in range(formato['Linhas']):
        c = []
        for coluna in range(formato['Colunas']):
            try:
                c.append(lista.pop())
            except:
                pass
        l.append(c)
    return l

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas_gerar(request):
    '''
    view que gera as etiquetas
    '''
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquetas.pdf"'
    formato = settings.FORMATOS_ETIQUETA_SUPORTADOS[2]
    pagesize = formato['Papel'] == 'A4' and A4 or letter
    c = canvas.Canvas(response)
    # Create the PDF object, using the response object as its "file." 
    lista_produtos = request.GET.getlist('produtos_adicionar')
    if lista_produtos:
        produtos = Produto.objects.filter(id__in=lista_produtos)
    else:
        produtos = Produto.objects.all()
    total = formato['Colunas'] * formato['Linhas']
    #objetos_por_pagina = zip(*(iter(produtos),) * total)
    objetos_por_pagina = list(chunks(produtos, total))
    for pagina_objetos in objetos_por_pagina:
        #lista_objetos = [objeto for objeto in pagina_objetos]
        numeros = _geraPaginaObjetos(formato, pagina_objetos)
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        geraPagina(formato, numeros, c, pagesize)
        # Close the PDF object cleanly, and we're done.
        c.showPage()
    c.save()
    return response
    
    
    for pagina in objetos_por_pagina:
        lista_objetos = [objeto for objeto in pagina]
        l = []
        for linha in range(formato['Linhas']):
            cols = []
            for coluna in range(formato['Colunas']):
                cols.append(lista_objetos.pop())
            l.append(cols)
        return l
    # retorna
    return response
        
    
    
