# -*- coding: utf-8 -*-
import datetime
from xml.dom import minidom
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test

from producao.models import FabricanteFornecedor
from producao.models import NotaFiscal


from django import forms

#
# DECORATORS
#

def possui_perfil_acesso_producao(user, login_url="/"):
    try:
        if user.perfilacessoproducao:
            return True
    except:
        return False

@user_passes_test(possui_perfil_acesso_producao)
def home(request):
    return render_to_response('frontend/producao/producao-home.html', locals(), context_instance=RequestContext(request),)
    
    
# lancamento de nota
# FORMULARIO DA NOTA
class UploadFileForm(forms.Form):
    file  = forms.FileField()

def importa_nota_sistema(f):
    try:
        xmldoc = minidom.parse(f)
        infNFE = xmldoc.getElementsByTagName('chNFe')[0]
        idnfe = infNFE.firstChild.nodeValue[22:34]
        nome_emissor = xmldoc.getElementsByTagName('xNome')[0]
        nome = nome_emissor.firstChild.nodeValue
        print "NOME DO EMISSOR: %s" % nome
        print "ID NOTA FISCAL %s" % idnfe
        emissor = xmldoc.getElementsByTagName('emit')[0]
        cnpj_emissor = xmldoc.getElementsByTagName('CNPJ')[0].firstChild.nodeValue
        # busca emissor
        fornecedor,created = FabricanteFornecedor.objects.get_or_create(cnpj=cnpj_emissor)
        fornecedor.nome = nome
        fornecedor.save()
        if created:
            print "Fornecedor CRIADO: %s" % fornecedor
        else:
            print "Fornecedor encrontrado: %s" % fornecedor
        frete = xmldoc.getElementsByTagName('vFrete')[0].firstChild.nodeValue
        # criando NFE no sistema
        nfe_sistema,created = NotaFiscal.objects.get_or_create(fabricante_fornecedor=fornecedor, numero=idnfe)
        nfe_sistema.taxas_diversas = frete
        nfe_sistema.save()
        # pega itens da nota
        itens = xmldoc.getElementsByTagName('det')
        for item in itens:
            # cada item da nota...
            codigo_produto = item.getElementsByTagName('cProd')[0].firstChild.nodeValue
            quantidade = item.getElementsByTagName('qCom')[0].firstChild.nodeValue
            valor_unitario = item.getElementsByTagName('vUnCom')[0].firstChild.nodeValue
            print u"ITEM: %s" % codigo_produto
            print u"Quantidade: %s" % quantidade
            print u"Valor Unitário: %s" % valor_unitario
            # impostos
            try:
                aliquota_icms = float(item.getElementsByTagName('pICMS')[0].firstChild.nodeValue)
            except:
                aliquota_icms = 0
            try:
                aliquota_ipi = float(item.getElementsByTagName('pIPI')[0].firstChild.nodeValue)
            except:
                aliquota_ipi = 0
            try:
                aliquota_pis = float(item.getElementsByTagName('pPIS')[0].firstChild.nodeValue)
            except:
                aliquota_pis = 0
            try:
                aliquota_cofins = float(item.getElementsByTagName('pCOFINS')[0].firstChild.nodeValue)
            except:
                aliquota_cofins = 0

            
            total_impostos = aliquota_ipi + aliquota_icms + aliquota_cofins + aliquota_cofins
            total_impostos = aliquota_ipi
            print "Valor %% ICMS: %s" % aliquota_icms
            print "Valor %% IPI: %s" % aliquota_ipi
            print "Valor %% COFNS: %s" % aliquota_cofins
            print "Valor %% PIS: %s" % aliquota_pis
            print "Incidência de %% impostos: %s" % total_impostos
        
            # busca o lancamento, para evitar dois lancamentos iguais do mesmo partnumber
            item_lancado,created = nfe_sistema.lancamentocomponente_set.get_or_create(part_number_fornecedor=codigo_produto, quantidade=quantidade, valor_unitario= valor_unitario, impostos= total_impostos)
            # salva
            item_lancado.save()
            # busca na memoria automaticamente
            item_lancado.busca_part_number_na_memoria()

        # calcula total da nota
        nfe_sistema.calcula_totais_nota()
        # printa tudo
        print "#"*10
        print "NOTA %s importada" % nfe_sistema.numero
        frete = nfe_sistema.taxas_diversas 
        produtos = nfe_sistema.total_com_imposto
        print "TOTAL DA NOTA: %s (Frete) + %s (Produtos + Impostos)" % (frete, produtos)
        print "Produtos"
        for lancamento in nfe_sistema.lancamentocomponente_set.all():
            print u"----- PN-FORNECEDOR: %s, QTD: %s VALOR: %s, Impostos: %s%% = TOTAL: %s Unitário (considerando frete proporcional) %s" % (lancamento.part_number_fornecedor, lancamento.quantidade, lancamento.valor_unitario, lancamento.impostos, lancamento.valor_total_com_imposto, lancamento.valor_unitario_final)
        return nfe_sistema
    except:
        raise
        return False
    

def lancar_nota(request):
    # nota nacional, com XML, upload do arquivo, importa e direcina pra edição da nota
    if request.GET.get('tipo', None) == 'nfe':
        tipo = 'nfe'
        upload_form = UploadFileForm() 
    # nota manual
    elif request.GET.get('tipo', None) == 'outros':
        tipo = 'outros'
    if request.POST.get('arquivo_nfe', None):
        # formulario de arquivo NFE enviado
        upload_form = UploadFileForm(request.POST, request.FILES)
        if upload_form.is_valid():
            # importa nota pra dentro do sistema
            try:
                nota = importa_nota_sistema(request.FILES['file'])
                if nota:
                    messages.success(request, 'Nota Importada com Sucesso!')
                    return redirect(reverse('producao:editar_nota', args=[nota.id]))
                else:
                    messages.success(request, 'Erro ao Importar nota!')
            except:
                raise
                
    return render_to_response('frontend/producao/producao-lancar-nota.html', locals(), context_instance=RequestContext(request),)


# MODEL FORM NOTA FISCAL

class NotaFiscalForm(forms.ModelForm):
    class Meta:
        model = NotaFiscal

def adicionar_nota(request):
    '''nota fiscal manual / Internacional'''
    form_adicionar_notafiscal = NotaFiscalForm()
    return render_to_response('frontend/producao/producao-adicionar-nota.html', locals(), context_instance=RequestContext(request),)

def editar_nota(request, notafiscal_id):
    notafiscal = NotaFiscal.objects.get(id=notafiscal_id)
    form_notafiscal = NotaFiscalForm(instance=notafiscal)
    return render_to_response('frontend/producao/producao-editar-nota.html', locals(), context_instance=RequestContext(request),)
    