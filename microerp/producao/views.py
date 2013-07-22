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
from django.db.models import Q
from django.conf import settings

from producao.models import FabricanteFornecedor
from producao.models import NotaFiscal
from producao.models import LancamentoComponente
from producao.models import Componente
from producao.models import ComponenteTipo


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
        total = xmldoc.getElementsByTagName('total')[0]
        frete = total.getElementsByTagName('vFrete')[0].firstChild.nodeValue
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
            print u"Valor Unitario: %s" % valor_unitario
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
            print "Incidencia de %% impostos: %s" % total_impostos
        
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
            print u"----- PN-FORNECEDOR: %s, QTD: %s VALOR: %s, Impostos: %s%% = TOTAL: %s Unitario (considerando frete proporcional) %s" % (lancamento.part_number_fornecedor, lancamento.quantidade, lancamento.valor_unitario, lancamento.impostos, lancamento.valor_total_com_imposto, lancamento.valor_unitario_final)
        return nfe_sistema
    except:
        raise
        return False
    


def lancar_nota(request):
    notas_abertas = NotaFiscal.objects.filter(status='a')
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
                    return redirect(reverse('producao:ver_nota', args=[nota.id]))
                else:
                    messages.success(request, 'Erro ao Importar nota!')
            except:
                raise
                
    return render_to_response('frontend/producao/producao-lancar-nota.html', locals(), context_instance=RequestContext(request),)


# MODEL FORM NOTA FISCAL

class NotaFiscalForm(forms.ModelForm):
    class Meta:
        model = NotaFiscal
        fields = ['fabricante_fornecedor', 'numero', 'tipo', 'taxas_diversas', 'cotacao_dolar', 'total_com_imposto', 'total_da_nota_em_dolar']

# MODEL FORM LANCAMENTO NOTA FISCAL

class LancamentoNotaFiscalForm(forms.ModelForm):
    class Meta:
        model = LancamentoComponente
        fields = 'part_number_fornecedor', 'quantidade', 'valor_unitario', 'impostos', 'componente', 'fabricante', 'part_number_fabricante', 'aprender'



def adicionar_nota(request):
    '''nota fiscal manual / Internacional'''
    if request.POST:
        form_adicionar_notafiscal = NotaFiscalForm(request.POST)
        if form_adicionar_notafiscal.is_valid():
            nota = form_adicionar_notafiscal.save()
            messages.success(request, u'Nota Adicionada com Sucesso!')
            return redirect(reverse('producao:ver_nota', args=[nota.id,]))
            
    else:
        form_adicionar_notafiscal = NotaFiscalForm()
    return render_to_response('frontend/producao/producao-adicionar-nota.html', locals(), context_instance=RequestContext(request),)


def apagar_nota(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    notafiscal.delete()
    messages.success(request, u'Nota Fiscal Apagada com Sucesso!')
    return redirect(reverse('producao:lancar_nota'))


def editar_nota(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    if request.POST:
        form_notafiscal = NotaFiscalForm(request.POST, instance=notafiscal)
        if form_notafiscal.is_valid():
            form_notafiscal.save()
            messages.success(request, u'Nota Fiscal Alterada com Sucesso!')
            return redirect(reverse('producao:ver_nota', args=[notafiscal.id,]))
            
    else:
        form_notafiscal = NotaFiscalForm(instance=notafiscal)
    return render_to_response('frontend/producao/producao-editar-nota.html', locals(), context_instance=RequestContext(request),)


def calcular_nota(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    # calcular todas os lancamentos
    for lancamento in notafiscal.lancamentocomponente_set.all():
        lancamento.calcula_totais_lancamento()
    # calcula total da nota
    notafiscal.calcula_totais_nota()
    # retorna para ver a nota
    messages.success(request, u'Totais e Impostos Calculados com Sucesso!')
    return redirect(reverse('producao:ver_nota', args=[notafiscal.id,]))


def ver_nota(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    return render_to_response('frontend/producao/producao-ver-nota.html', locals(), context_instance=RequestContext(request),)


def editar_lancamento(request, notafiscal_id, lancamento_id):
    lancamento = get_object_or_404(LancamentoComponente, nota__id=notafiscal_id, id=lancamento_id)
    if request.POST:        
        lancamento_form = LancamentoNotaFiscalForm(request.POST, instance=lancamento)
        if lancamento_form.is_valid():
            lancamento_form.save()
            messages.success(request, u'Lançamento %d Editado com Sucesso!' % lancamento.id)
            return redirect(reverse('producao:ver_nota', args=[lancamento.nota.id,]))
            
    else:
        lancamento_form = LancamentoNotaFiscalForm(instance=lancamento)
        
    return render_to_response('frontend/producao/producao-editar-lancamento.html', locals(), context_instance=RequestContext(request),)


def adicionar_lancamento(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    if request.POST:
        lancamento_form = LancamentoNotaFiscalForm(request.POST)
        if lancamento_form.is_valid():
            lancamento = lancamento_form.save(commit=False)
            lancamento.nota = notafiscal
            lancamento.save()
            messages.success(request, u'Lançamento %d Adicionado com Sucesso à nota %s!' % (lancamento.id, notafiscal))
            return redirect(reverse('producao:ver_nota', args=[notafiscal.id,]))
    else:
        lancamento_form = LancamentoNotaFiscalForm()
    return render_to_response('frontend/producao/producao-adicionar-lancamento.html', locals(), context_instance=RequestContext(request),)



# COMPONENTES

## FORMS

class ComponenteFormAdd(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        identificador = kwargs.pop('identificador')
        tipo = kwargs.pop('tipo')
        super(ComponenteFormAdd, self).__init__(*args, **kwargs)
        self.fields['identificador'].initial  = identificador
        self.fields['identificador'].widget.attrs['readonly'] = True
        self.fields['tipo'].initial  = tipo
        self.fields['tipo'].widget.attrs['readonly'] = True
        

    class Meta:
        fields = ('identificador', 'tipo', 'descricao', 'importado', 'ncm', 'lead_time', 'quantidade_minima', 'medida')
        model = Componente



class ComponenteFormPreAdd(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ComponenteFormPreAdd, self).__init__(*args, **kwargs)
        self.fields['tipo'].required = True
    
    class Meta:
        model = Componente
        fields = ['tipo',]


class TipoComponenteAdd(forms.ModelForm):
    class Meta:
        model = ComponenteTipo
## VIEWS

def listar_componentes(request):
    if request.POST:
        if request.POST.get('adicionar-tipo-componente', None):
            tipo_componente_form = TipoComponenteAdd(request.POST)
            if tipo_componente_form.is_valid():
                tipo = tipo_componente_form.save()
                messages.success(request, u'Tipo de Componente %s Adicionado com  Sucesso!' % tipo)
                return redirect(reverse('producao:listar_componentes'))
    
    elif request.GET:
        q_componente = request.GET.get('q_componente', True)
        if q_componente:
            if q_componente == "todos":
                componentes_encontrados = Componente.objects.all()
            else:
                componentes_encontrados = Componente.objects.filter(
                    Q(part_number__icontains=q_componente) | Q(descricao__icontains=q_componente) | Q(tipo__nome__icontains=q_componente)
                )
        
    componente_form = ComponenteFormPreAdd()
    tipo_componente_form = TipoComponenteAdd()
    return render_to_response('frontend/producao/producao-listar-componentes.html', locals(), context_instance=RequestContext(request),)


def adicionar_componentes(request):
    if request.POST.get('adicionar-componente', None):
        identificador = request.POST.get('identificador', None)
        tipo = request.POST.get('tipo', None)
        form_add_componente = ComponenteFormAdd(request.POST, identificador=identificador, tipo=tipo)
        if form_add_componente.is_valid():
            componente = form_add_componente.save()
            messages.success(request, u"Sucesso! Componente %s Adicionado!" % componente)
            return redirect(reverse('producao:listar_componentes'))
        else:
            messages.error(request, u"Erro! Componente NÃO Adicionado!")
            return render_to_response('frontend/producao/producao-adicionar-componentes.html', locals(), context_instance=RequestContext(request),)    
            
    
    if request.POST.get('pre-adicionar-componente', None):        
        # componente pre adicionado (tipo escolhido)
        tipo_componente_form = ComponenteFormPreAdd(request.POST)
        if tipo_componente_form.is_valid():
            tipo = tipo_componente_form.save(commit=False).tipo
            if tipo:
                messages.success(request, u"Adicionando um Componente do tipo <strong>%s</strong>" % tipo)
                # seleciona o último componente nessa situação
                ultimo_identificador = Componente.objects.filter(tipo=tipo).order_by('-identificador')
                if ultimo_identificador.count():
                    ultimo_identificador = ultimo_identificador[0].identificador
                else:
                    # caso não exista nenhum componente deste tipo, assumir identificador inicial
                    ultimo_identificador = 0                    
                identificador = ultimo_identificador + 1
                form_add_componente = ComponenteFormAdd(tipo=tipo, identificador=identificador)
        else:
            messages.warning(request, u"Nenhuma ação tomada. É preciso escolher o Tipo de Componente para adicionar")
            return redirect(reverse('producao:listar_componentes'))
        
        
        pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
        part_number = u"%s-%s%s" % (pn_prepend, tipo.nome[0:3].upper(), "%05d" % identificador)
        return render_to_response('frontend/producao/producao-adicionar-componentes.html', locals(), context_instance=RequestContext(request),)    
    else:
        # retorna à listagem
        messages.warning(request, u"Nenhuma ação tomada. É preciso escolher o tipo de Componente para adicionar")
        return redirect(reverse('producao:listar_componentes'))
    
def ver_componente(request, componente_id):
    componente = get_object_or_404(Componente, pk=componente_id)
    return render_to_response('frontend/producao/producao-ver-componente.html', locals(), context_instance=RequestContext(request),)    
    