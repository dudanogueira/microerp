# -*- coding: utf-8 -*-
"""This file is part of the microerp project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Duda Nogueira <dudanogueira@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Duda Nogueira'
__version__ = '0.0.1'

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm, cm

from django.http import HttpResponse

from django.core import management

import datetime
import operator
import decimal
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.conf import settings

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q

from estoque.models import Produto, ArquivoImportacaoProdutos
from almoxarifado.models import ListaMaterialDoContrato, LinhaListaMaterial

#
# DECORADORES
#

def possui_perfil_acesso_estoque(user, login_url="/"):
    try:
        if user.perfilacessoestoque and user.funcionario.ativo():
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

class SelecionaProdutos(forms.Form):
    produtos_adicionar = forms.CharField()

#
# VIEWS
#

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def home(request):
    return render_to_response('frontend/estoque/estoque-home.html', locals(), context_instance=RequestContext(request),)


# ETIQUETAS
@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas(request):
    
    # nome,id
    formatos = []
    for formato in settings.FORMATOS_ETIQUETA_SUPORTADOS:
        formatos.append((formato, settings.FORMATOS_ETIQUETA_SUPORTADOS[formato]['Codigo']))        
    
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


def geraPagina(formato, numeros, c, pagesize, SHOW_BORDER=True, pular=0):
    w, h = pagesize
    i = 0
    for linha in range(formato['Linhas']):
        for coluna in range(formato['Colunas']):
            i += 1
            try:
                numero = numeros[linha][coluna]
            except IndexError:
                return
            x = formato['Esquerda']*cm + (formato['Horizontal']*cm * coluna)
            y = h - formato['Superior']*cm - (formato['Vertical']*cm * (linha) +1)
            import string
            string = string.uppercase * 4
            string = numero.descricao
            c.drawString(x+4*mm, y+(20*mm), string[0:21])
            c.drawString(x+24*mm, y+(15*mm), string[21:35])
            c.drawString(x+24*mm, y+(10*mm), string[35:49])
            c.drawString(x+24*mm, y+(5*mm), string[49:64])
            if SHOW_BORDER:
                c.rect(x, y, formato['Largura']*cm, formato['Altura']*cm)
        
            if len(numero.codigo) == 1:
                codigo = "000%d" % int(numero.codigo)
            else:
                codigo = numero.codigo
            barcode = code128.Code128(codigo, barWidth=0.26*mm, barHeight=13*mm, 
                                      quiet=False, humanReadable=True)
            barcode.drawOn(c, x+(1*mm)+(4*mm), y+(4*mm))

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


class EnviarArquivoImportacao(forms.ModelForm):
    class Meta:
        model = ArquivoImportacaoProdutos
        fields = 'tipo', 'arquivo'

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def importacao_ver(request):
    if request.POST:
        form = EnviarArquivoImportacao(request.POST, request.FILES)
        if form.is_valid():
            novo_arquivo = form.save(commit=False)
            novo_arquivo.enviado_por = request.user.funcionario
            novo_arquivo.save()
            return redirect(reverse("estoque:importacao_ver"))
    else:
        form = EnviarArquivoImportacao()
    disponiveis = ArquivoImportacaoProdutos.objects.filter(importado=False)
    importados = ArquivoImportacaoProdutos.objects.filter(importado=True).order_by('importado_em')
    
    return render_to_response('frontend/estoque/estoque-importacao.html', locals(), context_instance=RequestContext(request),) 

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def importacao_apagar_arquivo(request, arquivo_id):
    arquivo = get_object_or_404(ArquivoImportacaoProdutos, pk=arquivo_id)
    arquivo.delete()
    return redirect(reverse("estoque:importacao_ver"))

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def importacao_importar(request):
    try:
        management.call_command('importar_estoque_do_bd')
        messages.success(request, u"Sucesso! Importação de Estoque realizada")
    except:
        messages.error(request, u"Erro! Importação de Estoque FALHOU!")
        
    return redirect(reverse("estoque:importacao_ver"))


@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def etiquetas_gerar(request):
    '''
    view que gera as etiquetas
    '''
    lista_produtos = request.GET.get('produtos_adicionar')
    show_border_q = request.GET.get('show_border', 0)
    formato_id = request.GET.get('formato', 17)
    if show_border_q == 0:
        show_border = False
    else:
        show_border = True

    try:
        pular_espacos = int(request.GET.get('pular_espacos', 0))
    except:
        pular_espacos = 0

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="etiquetas.pdf"'
    try:
        formato = settings.FORMATOS_ETIQUETA_SUPORTADOS[int(formato_id)]
    except:
        formato = settings.FORMATOS_ETIQUETA_SUPORTADOS[17]
    pagesize = formato['Papel'] == 'A4' and A4 or letter
    c = canvas.Canvas(response)
    
    if lista_produtos:
        produtos_lista = lista_produtos.split(',')
        produtos = Produto.objects.filter(codigo__in=produtos_lista, ativo=True)
    else:
        produtos = Produto.objects.filter(ativo=True)
    total = formato['Colunas'] * formato['Linhas']
    # ordena por grupo
    produtos.order_by('tipo')
    objetos_por_pagina = list(chunks(produtos, total))
    
    # SISTEMA DE IMPRESSAO DE AVULSOS
    try:
        pular = int(pular_espacos)
    except:
        pular = 0
    
    for pagina_objetos in objetos_por_pagina:
        
        numeros = _geraPaginaObjetos(formato, pagina_objetos)
        for item in range(1, pular_espacos+1):
            numeros.insert(0, None)
        #lista_objetos = [objeto for objeto in pagina_objetos]
        
        geraPagina(formato, numeros, c, pagesize, SHOW_BORDER=show_border, pular=pular)
        c.setPageSize(pagesize)
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
        
from django.views.decorators.csrf import csrf_exempt    
try:
    from django.utils import simplejson
except:
    import json as simplejson

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def listas_materiais_ver(request):
    listas = ListaMaterialDoContrato.objects.filter(ativa=True)
    return render_to_response('frontend/estoque/estoque-listas-materiais-ver.html', locals(), context_instance=RequestContext(request),) 

class FormLinhaMaterial(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormLinhaMaterial, self).__init__(*args, **kwargs)
        if self.instance.quantidade_requisitada == self.instance.quantidade_ja_atendida:
            sugerido = 0
        else:
            sugerido = self.instance.quantidade_requisitada - self.instance.quantidade_ja_atendida
        self.fields['modificador'] = forms.FloatField(initial=sugerido)
        self.fields['modificador'].widget.attrs['class'] = 'input-mini'
        self.fields['comprador'] = forms.FloatField(initial=0)
        self.fields['comprador'].widget.attrs['class'] = 'input-mini'
        self.fields['produto'].widget = forms.HiddenInput()

@user_passes_test(possui_perfil_acesso_estoque, login_url='/')
def listas_materiais_alterar(request, lista_id):
    lista = get_object_or_404(ListaMaterialDoContrato, pk=lista_id)
    ListaMaterialDoContratoFormSet = forms.models.inlineformset_factory(ListaMaterialDoContrato, LinhaListaMaterial, extra=0, can_delete=False, form=FormLinhaMaterial)
    if request.POST:
        form_editar_linhas_materiais = ListaMaterialDoContratoFormSet(request.POST, instance=lista, prefix="lista-material")
        entregues = {}
        for i in range(form_editar_linhas_materiais.total_form_count()):
            if form_editar_linhas_materiais[i].data['lista-material-%s-modificador' % i]:
                entregues[form_editar_linhas_materiais[i].data['lista-material-%s-produto' % i]] = form_editar_linhas_materiais[i].data['lista-material-%s-modificador' % i]
                form_editar_linhas_materiais[i].instance.quantidade_ja_atendida += decimal.Decimal(form_editar_linhas_materiais[i].data['lista-material-%s-modificador' % i])
                form_editar_linhas_materiais[i].instance.save()
    else:
        form_editar_linhas_materiais = ListaMaterialDoContratoFormSet(instance=lista, prefix="lista-material")
    return render_to_response('frontend/estoque/estoque-listas-materiais-alterar.html', locals(), context_instance=RequestContext(request),)

@csrf_exempt
@login_required
def ajax_consulta_produto(request):
    q = request.GET.get('q', None)
    mostra_preco = request.GET.get('mostra_preco', None)
    id_produto = request.GET.get('id', None)
    if q:
        queries = q.split()
        qset1 =  reduce(operator.__and__, [Q(codigo=query) | Q(descricao__icontains=query) | Q(nome__icontains=query)  for query in queries])
        produtos = Produto.objects.filter(qset1)
    if id_produto:
        produto = Produto.objects.get(
            pk=id_produto
        )
        if mostra_preco:
            nome_produto = "%s - %s (V: R$ %s / C: R$ %s)" % (produto.codigo,produto.nome, produto.preco_venda, produto.preco_custo)
        else:
            nome_produto = "%s - %s" % (produto.codigo,produto.nome)
        result={"text":nome_produto, "id": str(produto.id), "preco": float(produto.preco_venda)}
        return HttpResponse(simplejson.dumps(result), content_type='application/json')
    result = []
    for produto in produtos:
        if mostra_preco:
            nome_produto = "%s - %s (V: R$ %s / C: R$ %s)" % (produto.codigo,produto.nome, produto.preco_venda, produto.preco_custo)
        else:
            nome_produto = "%s - %s" % (produto.codigo,produto.nome)
        
        result.append({"text":nome_produto, "id": str(produto.id), "preco": float(produto.preco_venda), "preco_custo": float(produto.preco_custo)})
    return HttpResponse(simplejson.dumps(result), content_type='application/json')

