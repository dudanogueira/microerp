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
from django.db.models import Q, Sum, Count
from django.conf import settings

from producao.models import FabricanteFornecedor, FABRICANTE_FORNECEDOR_TIPO_CHOICES
from producao.models import NotaFiscal
from producao.models import LancamentoComponente
from producao.models import Componente
from producao.models import ComponenteTipo
from producao.models import EstoqueFisico
from producao.models import LinhaFornecedorFabricanteComponente


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
    
    def clean_file(self):
            file = self.cleaned_data['file']
            file_type = file.content_type
            if file_type != "text/xml":
                raise forms.ValidationError(u'Formato Não suportado. Use XML de Nota Fiscal')

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
        if created:
            fornecedor.tipo = 'fornecedor'
        fornecedor.save()
        if created:
            print "Fornecedor CRIADO: %s" % fornecedor
        else:
            print "Fornecedor encrontrado: %s" % fornecedor
        total = xmldoc.getElementsByTagName('total')[0]
        frete = total.getElementsByTagName('vFrete')[0].firstChild.nodeValue
        # criando NFE no sistema
        nfe_sistema,created = NotaFiscal.objects.get_or_create(fabricante_fornecedor=fornecedor, numero=idnfe, tipo='n')
        nfe_sistema.taxas_diversas = frete
        nfe_sistema.save()
        # pega itens da nota
        itens = xmldoc.getElementsByTagName('det')
        if not created:
            return "duplicada"
        else:
            for item in itens:
                # cada item da nota...
                peso = int(item.getAttribute('nItem'))
                codigo_produto = item.getElementsByTagName('cProd')[0].firstChild.nodeValue
                quantidade = item.getElementsByTagName('qCom')[0].firstChild.nodeValue
                valor_unitario = item.getElementsByTagName('vUnCom')[0].firstChild.nodeValue
                print u"ITEM: %s" % codigo_produto
                print u"Peso: %d" % peso
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
                item_lancado,created = nfe_sistema.lancamentocomponente_set.get_or_create(part_number_fornecedor=codigo_produto, quantidade=quantidade, valor_unitario= valor_unitario, impostos= total_impostos, peso=peso)
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
                if type(nota) == NotaFiscal:
                    messages.success(request, 'Nota Importada com Sucesso!')
                    return redirect(reverse('producao:ver_nota', args=[nota.id]))
                elif nota == "duplicada":
                    messages.error(request, 'Erro! Nota já Importada!')
                else:
                    messages.error(request, 'Erro ao Importar nota!')
            except:
                raise
                
    return render_to_response('frontend/producao/producao-lancar-nota.html', locals(), context_instance=RequestContext(request),)


# MODEL FORM NOTA FISCAL

class NotaFiscalForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(NotaFiscalForm, self).__init__(*args, **kwargs)    
        self.fields['taxas_diversas'].localize=True
        self.fields['taxas_diversas'].widget.is_localized = True
        self.fields['taxas_diversas'].widget.attrs['class'] = 'nopoint'
        self.fields['cotacao_dolar'].localize=True
        self.fields['cotacao_dolar'].widget.is_localized = True
        self.fields['cotacao_dolar'].widget.attrs['class'] = 'nopoint'
        self.fields['fabricante_fornecedor'].widget.attrs['class'] = 'select2'
        self.fields['tipo'].choices.insert(0, ('','Escolha o Tipo' ) )
        
    
    
    class Meta:
        model = NotaFiscal
        fields = ['fabricante_fornecedor', 'numero', 'tipo', 'taxas_diversas', 'cotacao_dolar',]

# MODEL FORM LANCAMENTO NOTA FISCAL

class LancamentoNotaFiscalForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        nota = kwargs.pop('nota')
        super(LancamentoNotaFiscalForm, self).__init__(*args, **kwargs)
        self.fields['quantidade'].localize=True
        self.fields['quantidade'].widget.is_localized = True
        self.fields['quantidade'].widget.attrs['class'] = 'nopoint'
        self.fields['valor_unitario'].localize=True
        self.fields['valor_unitario'].widget.is_localized = True
        self.fields['valor_unitario'].widget.attrs['class'] = 'nopoint'
        self.fields['impostos'].localize=True
        self.fields['impostos'].widget.is_localized = True
        self.fields['impostos'].widget.attrs['class'] = 'nopoint'
        self.fields['componente'].widget.attrs['class'] = 'select2'
        self.fields['fabricante'].widget.attrs['class'] = 'select2'

        

        if nota.tipo == 'n':
            self.fields['valor_unitario'].help_text ="Nota Nacional: Valor em Reais (R$)"
        else:
            self.fields['valor_unitario'].help_text ="Nota Internacional: Valor em Dolar (USD)"
    
    
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
            # calcular todas os lancamentos
            for lancamento in notafiscal.lancamentocomponente_set.all():
                lancamento.calcula_totais_lancamento()
            # calcula total da nota
            notafiscal.calcula_totais_nota()
            messages.info(request, u'Nota Fiscal Recalculada!')
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
        lancamento_form = LancamentoNotaFiscalForm(request.POST, instance=lancamento, nota=lancamento.nota)
        if lancamento_form.is_valid():
            lancamento_form.save()
            messages.success(request, u'Lançamento %d Editado com Sucesso!' % lancamento.id)
            # calcular todas os lancamentos
            for lancamento in lancamento.nota.lancamentocomponente_set.all():
                lancamento.calcula_totais_lancamento()
            # calcula total da nota
            lancamento.nota.calcula_totais_nota()
            messages.info(request, u'Nota Fiscal Recalculada!')
            
            return redirect(reverse('producao:ver_nota', args=[lancamento.nota.id,]))
            
    else:
        lancamento_form = LancamentoNotaFiscalForm(instance=lancamento, nota=lancamento.nota)
        
    return render_to_response('frontend/producao/producao-editar-lancamento.html', locals(), context_instance=RequestContext(request),)


def adicionar_lancamento(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    if request.POST:
        lancamento_form = LancamentoNotaFiscalForm(request.POST, nota=notafiscal)
        if lancamento_form.is_valid():
            lancamento = lancamento_form.save(commit=False)
            lancamento.nota = notafiscal
            lancamento.save()
            messages.success(request, u'Lançamento %d Adicionado com Sucesso à nota %s!' % (lancamento.id, notafiscal))
            return redirect(reverse('producao:ver_nota', args=[notafiscal.id,]))
    else:
        lancamento_form = LancamentoNotaFiscalForm(nota=notafiscal)
    return render_to_response('frontend/producao/producao-adicionar-lancamento.html', locals(), context_instance=RequestContext(request),)


def lancar_nota_fechar(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id, status="a")
    if notafiscal.lancamentocomponente_set.filter(componente=None).count() == 0:
        if notafiscal.lancar_no_estoque():
            messages.success(request, u'Nota Fiscal %s Lançada com Sucesso!' % notafiscal)
        else:
            messages.error(request, u'ERRO! Nota Fiscal %s Não Lancada!' % notafiscal)
        return redirect(reverse('producao:lancar_nota'))
    else:
        messages.error(request, u'ERRO! Nota Fiscal %s Possui Lançamentos não vinculados à Componente! (em vermelho)' % notafiscal.numero)
        return redirect(reverse('producao:ver_nota', args=[notafiscal.id,]))
    

# COMPONENTES

## FORMS

class ComponenteFormAdd(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        identificador = kwargs.pop('identificador')
        tipo = kwargs.pop('tipo')
        super(ComponenteFormAdd, self).__init__(*args, **kwargs)
        self.fields['identificador'].initial  = identificador
        self.fields['identificador'].widget = forms.HiddenInput()
        self.fields['tipo'].initial  = tipo
        self.fields['tipo'].widget = forms.HiddenInput()
        
    class Meta:
        fields = ('identificador', 'tipo', 'descricao', 'nacionalidade', 'ncm', 'lead_time', 'medida')
        model = Componente
    

class ComponenteFormPreAdd(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ComponenteFormPreAdd, self).__init__(*args, **kwargs)
        self.fields['tipo'].required = True
        self.fields['tipo'].widget.attrs['class'] = 'select2'
    
    class Meta:
        model = Componente
        fields = ['tipo',]



class TipoComponenteAdd(forms.ModelForm):
    
    def clean_nome(self):
        """
        If somebody enters into this form ' hello ', or 'hello friend'
        the extra whitespace will be stripped and replaced
        return 'hello' and 'hellofriend'
        """
        return self.cleaned_data.get('nome', '').strip().replace(' ', '').upper()
    
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
            else:
                return render_to_response('frontend/producao/producao-listar-componentes.html', locals(), context_instance=RequestContext(request),)
    
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
        part_number = u"%s-%s%s" % (pn_prepend, tipo.slug.upper(), "%05d" % identificador)
        return render_to_response('frontend/producao/producao-adicionar-componentes.html', locals(), context_instance=RequestContext(request),)    
    else:
        # retorna à listagem
        messages.warning(request, u"Nenhuma ação tomada. É preciso escolher o tipo de Componente para adicionar")
        return redirect(reverse('producao:listar_componentes'))
    
def ver_componente(request, componente_id):
    componente = get_object_or_404(Componente, pk=componente_id)
    lancamentos = LancamentoComponente.objects.filter(componente=componente, nota__status='l').order_by('-criado')
    # memorias: LinhaFornecedorFabricanteComponente
    memorias = LinhaFornecedorFabricanteComponente.objects.filter(componente=componente)
    fornecedores = LancamentoComponente.objects.filter(componente=componente, nota__status='l').values('nota__fabricante_fornecedor__nome').annotate(total=Sum('quantidade'))
    fabricantes = LancamentoComponente.objects.filter(componente=componente, nota__status='l').values('fabricante__nome').annotate(total=Sum('quantidade'))
    posicoes_estoque = []
    for estoque in EstoqueFisico.objects.all():
        try:
            posicao = estoque.posicaoestoque_set.filter(componente=componente).order_by('-data_entrada')[0]
        except:
            posicao = None
        if posicao:
            posicoes_estoque.append(posicao)
    return render_to_response('frontend/producao/producao-ver-componente.html', locals(), context_instance=RequestContext(request),)    
    

# MEMORIA DE COMPONENTE

class AdicionarMemoriaComponenteForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        componente = kwargs.pop('componente')
        super(AdicionarMemoriaComponenteForm, self).__init__(*args, **kwargs)
        self.fields['part_number_fabricante'].required = True
        if componente:
            self.fields['componente'].initial = componente.id
        self.fields['fornecedor'].widget.attrs['class'] = 'select2'
        self.fields['fabricante'].widget.attrs['class'] = 'select2'
        self.fields['componente'].widget.attrs['class'] = 'select2'
        
    
    class Meta:
        model = LinhaFornecedorFabricanteComponente

def adicionar_memoria_componente(request, componente_id):
    componente = get_object_or_404(Componente, pk=componente_id)
    if request.POST:
        form = AdicionarMemoriaComponenteForm(request.POST, componente=componente)
        if form.is_valid():
            memoria = form.save()
            messages.success(request, "Sucesso! Memória de Conversão adicionada!")
            return(redirect(reverse('producao:ver_componente', args=[componente.id,]) + "#memoria"))
    else:
        form = AdicionarMemoriaComponenteForm(componente=componente)
    return render_to_response('frontend/producao/producao-componente-adicionar-memoria.html', locals(), context_instance=RequestContext(request),)    


def apagar_memoria_componente(request, memoria_id, componente_id):
    componente = get_object_or_404(Componente, pk=componente_id)
    memoria = get_object_or_404(LinhaFornecedorFabricanteComponente, componente=componente, pk=memoria_id)
    memoria.delete()
    messages.success(request, "Sucesso! Mensagem apagada com sucesso!")
    return redirect(reverse("producao:ver_componente", args=[componente.id]) + "#memoria")

# FABRICANTES E FORNECEDORES

# FORMS FABRICANTES E FORNECEDORES
class AdicionarFabricanteFornecedor(forms.ModelForm):
    
    class Meta:
        model = FabricanteFornecedor

def listar_fabricantes_fornecedores(request):
    tipos_possiveis = FABRICANTE_FORNECEDOR_TIPO_CHOICES
    if request.GET:
        q_fab_for = request.GET.get('q_fab_for', True)
        q_tipo = request.GET.get('q_tipo')
        if q_fab_for:
            if q_fab_for == "todos":
                fab_for_encontrados = FabricanteFornecedor.objects.all()
            else:
                fab_for_encontrados = FabricanteFornecedor.objects.filter(
                    Q(cnpj__icontains=q_fab_for) | Q(nome__icontains=q_fab_for)
                )
        if q_tipo:
            fab_for_encontrados = fab_for_encontrados.filter(tipo=q_tipo)
    return render_to_response('frontend/producao/producao-listar-fabricantes-fornecedores.html', locals(), context_instance=RequestContext(request),)    


def ver_fabricantes_fornecedores(request, fabricante_fornecedor_id):
    fabricante_fornecedor = get_object_or_404(FabricanteFornecedor, pk=fabricante_fornecedor_id)
    fornecidos = LancamentoComponente.objects.filter(nota__fabricante_fornecedor=fabricante_fornecedor, nota__status='l').values('componente__part_number', 'componente__id', 'componente__ativo').annotate(total=Sum('quantidade')).order_by('-total')
    fabricados = LancamentoComponente.objects.filter(fabricante=fabricante_fornecedor, nota__status='l').values('componente__part_number', 'componente__medida', 'componente__ativo', 'componente__id').annotate(total=Sum('quantidade')).order_by('-total')
    memorias = LinhaFornecedorFabricanteComponente.objects.filter(fornecedor=fabricante_fornecedor)
    return render_to_response('frontend/producao/producao-ver-fabricante-fornecedor.html', locals(), context_instance=RequestContext(request),)    
    

def adicionar_fabricantes_fornecedores(request):
    if request.POST:
        form_add_fabricante_fornecedor = AdicionarFabricanteFornecedor(request.POST)
        if form_add_fabricante_fornecedor.is_valid():
            fabricante_fornecedor = form_add_fabricante_fornecedor.save()
            messages.success(request, 'Sucesso! Fabricante Fornecedor %s Adicionado!' % fabricante_fornecedor)
            return redirect(reverse('producao:ver_fabricantes_fornecedores', args=[fabricante_fornecedor.id]))
    else:
        form_add_fabricante_fornecedor = AdicionarFabricanteFornecedor()
        
    return render_to_response('frontend/producao/producao-adicionar-fabricante-fornecedor.html', locals(), context_instance=RequestContext(request),)    


def editar_fabricantes_fornecedores(request, fabricante_fornecedor_id):
    fabricante_fornecedor = get_object_or_404(FabricanteFornecedor, pk=fabricante_fornecedor_id)
    if request.POST:
        form_add_fabricante_fornecedor = AdicionarFabricanteFornecedor(request.POST, instance=fabricante_fornecedor)
        if form_add_fabricante_fornecedor.is_valid():
            fabricante_fornecedor = form_add_fabricante_fornecedor.save()
            messages.success(request, 'Sucesso! Fabricante Fornecedor %s Editado!' % fabricante_fornecedor)
            return redirect(reverse('producao:ver_fabricantes_fornecedores', args=[fabricante_fornecedor.id]))
    else:
        form_add_fabricante_fornecedor = AdicionarFabricanteFornecedor(instance=fabricante_fornecedor)
        
    return render_to_response('frontend/producao/producao-editar-fabricante-fornecedor.html', locals(), context_instance=RequestContext(request),)    