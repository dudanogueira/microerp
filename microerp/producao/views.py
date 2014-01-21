# -*- coding: utf-8 -*-
import datetime, urllib, calendar
from xml.dom import minidom
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django import forms

from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Sum, Count
from django.conf import settings

from django.core.mail import EmailMessage

from producao.models import FabricanteFornecedor, FABRICANTE_FORNECEDOR_TIPO_CHOICES
from producao.models import NotaFiscal, STATUS_NOTA_FISCAL
from producao.models import LancamentoComponente
from producao.models import Componente
from producao.models import ComponenteTipo
from producao.models import EstoqueFisico
from producao.models import LinhaFornecedorFabricanteComponente
from producao.models import PosicaoEstoque
from producao.models import ArquivoAnexoComponente
from producao.models import SubProduto
from producao.models import LinhaSubProduto
from producao.models import OpcaoLinhaSubProduto
from producao.models import DocumentoTecnicoSubProduto
from producao.models import LinhaSubProdutoAgregado
from producao.models import ProdutoFinal
from producao.models import LinhaSubProdutodoProduto
from producao.models import LinhaComponenteAvulsodoProduto
from producao.models import DocumentoTecnicoProduto
from producao.models import OrdemProducaoSubProduto
from producao.models import OrdemProducaoProduto
from producao.models import RegistroEnvioDeTesteSubProduto
from producao.models import RegistroSaidaDeTesteSubProduto
from producao.models import RegistroValorEstoque
from producao.models import OrdemDeCompra
from producao.models import AtividadeDeOrdemDeCompra
from producao.models import ComponentesDaOrdemDeCompra
from producao.models import RequisicaoDeCompra
from producao.models import PerfilAcessoProducao
from producao.models import OrdemConversaoSubProduto
from producao.models import LancamentoProdProduto
from producao.models import LinhaTesteLancamentoProdProduto
from producao.models import MovimentoEstoqueSubProduto
from producao.models import MovimentoEstoqueProduto
from producao.models import FalhaDeTeste
from producao.models import NotaFiscalLancamentosProducao
from producao.models import LancamentoDeFalhaDeTeste
from producao.models import LinhaLancamentoFalhaDeTeste

from rh.models import Funcionario

ORDEM_DE_COMPRA_CRITICIDADE_CHOICES_VAZIO = (
    ('', '-----'),
    (0, 'Baixa'),
    (1, 'Média'),
    (2, 'Urgente'),
)

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
    # componentes
    componentes_total = Componente.objects.all().count()
    componentes_ativos = Componente.objects.filter(ativo=True).count()
    componentes_inativos = Componente.objects.filter(ativo=False).count()
    # subprodutos
    subprodutos_total = SubProduto.objects.all().count()
    subprodutos_ativos = SubProduto.objects.filter(ativo=True).count()
    subprodutos_inativos = SubProduto.objects.filter(ativo=False).count()
    # produtos
    produtos_total = ProdutoFinal.objects.all().count()
    produtos_ativos = ProdutoFinal.objects.filter(ativo=True).count()
    produtos_inativos = ProdutoFinal.objects.filter(ativo=False).count()
    fornecedores_total = NotaFiscal.objects.all().values('fabricante_fornecedor').distinct().count()
    notas_total = NotaFiscal.objects.all().count()
    notas_abertas = NotaFiscal.objects.filter(status="a").count()
    notas_lancadas = NotaFiscal.objects.filter(status="l").count()
    estoques = EstoqueFisico.objects.all()
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
        numero = idnfe[3:]
        serie = idnfe[0:3] 
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
        nfe_sistema,created = NotaFiscal.objects.get_or_create(fabricante_fornecedor=fornecedor, numero=numero, tipo='n')
        nfe_sistema.serie = serie
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
                # calcula valores de lancamentos
                item_lancado.calcula_totais_lancamento()
                # busca na memoria automaticamente
                item_lancado.busca_part_number_na_memoria()
                # calcula totais do lancamento


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

class FormFiltrarNotaFiscal(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FormFiltrarNotaFiscal, self).__init__(*args, **kwargs)
        self.fields['fornecedor'].widget.attrs['class'] = 'select2 input-small'
        self.fields['inicio'].widget.attrs['class'] = 'datepicker input-small'
        self.fields['fim'].widget.attrs['class'] = 'datepicker input-small'
        self.fields['status'].widget.attrs['class'] = 'input-small'
    
    status = forms.ChoiceField(choices=(('', 'Todos',), ('a', 'Abertas'), ('l', u'Lançadas')), required=False, initial='a')    
    fornecedor = forms.ModelChoiceField(queryset=FabricanteFornecedor.objects.all(), required=False, empty_label="Todos os Fornecedores")
    inicio = forms.DateField(label=u"Início", required=True)
    fim = forms.DateField(label=u"Fim", required=True)    

@user_passes_test(possui_perfil_acesso_producao)
def nota_fiscal_dados(request):
    notas_exibir = NotaFiscal.objects.all().order_by('data_entrada')
    if request.POST:
        filtro_notas_form = FormFiltrarNotaFiscal(request.POST)
        if filtro_notas_form.is_valid():
            status = filtro_notas_form.cleaned_data['status']
            fornecedor = filtro_notas_form.cleaned_data['fornecedor']
            inicio = filtro_notas_form.cleaned_data['inicio']
            fim = filtro_notas_form.cleaned_data['fim']
            if status:
                notas_exibir = notas_exibir.filter(status=status)
            if fornecedor:
                notas_exibir = notas_exibir.filter(fabricante_fornecedor=fornecedor)
            if inicio and fim:
                notas_exibir = notas_exibir.filter(data_entrada__range=(datetime.datetime.combine(inicio, datetime.time.min), datetime.datetime.combine(fim, datetime.time.max)))
                    
    tipo = request.GET.get('tipo')
    periodo = request.GET.get('periodo')
    if periodo == "dia":
        total_notas_por_dia = notas_exibir.extra({'data_entrada':"date(data_entrada)"}).\
            values('data_entrada').\
            annotate(soma=Sum('total_sem_imposto'))

    if periodo == "mes":
        from django.db import connections
        total_notas_por_mes = notas_exibir.extra(select={'month': connections[NotaFiscal.objects.db].ops.date_trunc_sql('month', 'data_entrada')}).values('month').annotate(soma=Sum('total_sem_imposto'))
        
    return render_to_response('frontend/producao/producao-lancar-nota-dados2.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def lancar_nota(request):
    notas_exibir = NotaFiscal.objects.all().order_by('-criado')
    try:
        inicio_lancamentos = NotaFiscal.objects.all().order_by('data_entrada')[0].data_entrada
        fim_lancamentos = NotaFiscal.objects.all().order_by('-data_entrada')[0].data_entrada
    except:
        inicio_lancamentos = None
        fim_lancamentos = None
    if inicio_lancamentos:
        form_initial = {'inicio': inicio_lancamentos, 'fim': fim_lancamentos}
    else:
        form_initial = None
    filtro_notas_form = FormFiltrarNotaFiscal(form_initial)
    if request.POST.get('filtrar-notas-fiscais-btn', None):
            filtro_notas_form = FormFiltrarNotaFiscal(request.POST)
            if filtro_notas_form.is_valid():
                status = filtro_notas_form.cleaned_data['status']
                fornecedor = filtro_notas_form.cleaned_data['fornecedor']
                inicio = filtro_notas_form.cleaned_data['inicio']
                fim = filtro_notas_form.cleaned_data['fim']
                if status:
                    notas_exibir = notas_exibir.filter(status=status)
                if fornecedor:
                    notas_exibir = notas_exibir.filter(fabricante_fornecedor=fornecedor)
                if inicio and fim:
                    notas_exibir = notas_exibir.filter(data_entrada__range=(datetime.datetime.combine(inicio, datetime.time.min), datetime.datetime.combine(fim, datetime.time.max)))

    notas_filtro_total_sem_imposto = notas_exibir.aggregate(Sum('total_sem_imposto'))
    notas_filtro_total_com_imposto = notas_exibir.aggregate(Sum('total_com_imposto'))

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
        fields = ['fabricante_fornecedor', 'serie', 'numero', 'tipo', 'taxas_diversas', 'cotacao_dolar',]

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
        self.fields['componente'].queryset = Componente.objects.filter(ativo=True)
        self.fields['fabricante'].widget.attrs['class'] = 'select2'

        

        if nota.tipo == 'n':
            self.fields['valor_unitario'].label = "Valor Unitário (R$):"
        else:
            self.fields['valor_unitario'].label = "Valor Unitário (USD):"
    
        self.fields['valor_unitario'].help_text = ""
        self.fields['impostos'].help_text = ""
    
    class Meta:
        model = LancamentoComponente
        fields = 'part_number_fornecedor', 'quantidade', 'valor_unitario', 'impostos', 'componente', 'fabricante', 'part_number_fabricante', 'aprender'

@user_passes_test(possui_perfil_acesso_producao)
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


@user_passes_test(possui_perfil_acesso_producao)
def apagar_nota(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    if request.user.perfilacessoproducao.gerente:
        notafiscal.delete()
        messages.success(request, u'Nota Fiscal Apagada com Sucesso!')
    else:
        messages.error(request, u"Somente gerente pode apagar")
    return redirect(reverse('producao:lancar_nota'))



@user_passes_test(possui_perfil_acesso_producao)
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



@user_passes_test(possui_perfil_acesso_producao)
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



@user_passes_test(possui_perfil_acesso_producao)
def ver_nota(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    return render_to_response('frontend/producao/producao-ver-nota.html', locals(), context_instance=RequestContext(request),)



@user_passes_test(possui_perfil_acesso_producao)
def editar_lancamento(request, notafiscal_id, lancamento_id):
    lancamento = get_object_or_404(LancamentoComponente, nota__id=notafiscal_id, id=lancamento_id)
    if request.POST:        
        lancamento_form = LancamentoNotaFiscalForm(request.POST, instance=lancamento, nota=lancamento.nota)
        if lancamento_form.is_valid():
            lancamento_form.save()
            messages.success(request, u'Lançamento %d Editado com Sucesso!' % lancamento.id)
            lancamento.busca_part_number_na_memoria()
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


@user_passes_test(possui_perfil_acesso_producao)
def adicionar_lancamento(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id)
    if request.POST:
        lancamento_form = LancamentoNotaFiscalForm(request.POST, nota=notafiscal)
        if lancamento_form.is_valid():
            # checa se já existe lancamento com este part_number
            part_number_fornecedor = lancamento_form.cleaned_data['part_number_fornecedor']
            if notafiscal.lancamentocomponente_set.filter(part_number_fornecedor=part_number_fornecedor):
                messages.error(request, u"Erro! Já existe um part number de Fornecedor %s nesta nota" % part_number_fornecedor)
            else:
                lancamento = lancamento_form.save(commit=False)
                lancamento.nota = notafiscal
                lancamento.calcula_totais_lancamento()
                lancamento.busca_part_number_na_memoria()
                lancamento.save()
                notafiscal.calcula_totais_nota()
                messages.success(request, u'Lançamento %d Adicionado com Sucesso à nota %s!' % (lancamento.id, notafiscal))
                return redirect(reverse('producao:ver_nota', args=[notafiscal.id,]))
    else:
        lancamento_form = LancamentoNotaFiscalForm(nota=notafiscal)
    return render_to_response('frontend/producao/producao-adicionar-lancamento.html', locals(), context_instance=RequestContext(request),)



@user_passes_test(possui_perfil_acesso_producao)
def lancar_nota_fechar(request, notafiscal_id):
    notafiscal = get_object_or_404(NotaFiscal, id=notafiscal_id, status="a")
    if notafiscal.lancamentocomponente_set.filter(componente=None).count() == 0:
        if notafiscal.lancar_no_estoque(user_id=request.user.id):
            notafiscal.data_lancado_estoque = datetime.datetime.now()
            notafiscal.lancado_por = request.user
            notafiscal.save()
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
        fields = ('identificador', 'tipo', 'imagem', 'descricao', 'nacionalidade', 'ncm', 'lead_time', 'medida')
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
    
    def clean_nome_outro(self):
        """
        If somebody enters into this form ' hello ', or 'hello friend'
        the extra whitespace will be stripped and replaced
        return 'hello' and 'hellofriend'
        """
        return self.cleaned_data.get('nome', '').strip().replace(' ', '').upper()
    
    class Meta:
        model = ComponenteTipo

class ImagemComponenteForm(forms.ModelForm):

    class Meta:
        model = Componente
        fields = 'imagem',

class ArquivoAnexoComponenteForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        componente = kwargs.pop('componente')
        super(ArquivoAnexoComponenteForm, self).__init__(*args, **kwargs)
        self.fields['componente'].initial  = componente
        self.fields['componente'].widget = forms.HiddenInput()
        self.fields['nome'].widget.attrs['class'] = 'input-xxlarge'
        
    
    
    class Meta:
        model = ArquivoAnexoComponente
    

## VIEWS

@user_passes_test(possui_perfil_acesso_producao)
def listar_componentes(request):
    componentes_encontrados = Componente.objects.filter(ativo=True).order_by('part_number')
    componentes_inativos = Componente.objects.filter(ativo=False).order_by('part_number')
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
                componentes_encontrados = Componente.objects.filter(ativo=True)
                componentes_inativos = Componente.objects.filter(ativo=False).order_by('part_number')
            else:
                componentes_encontrados = componentes_encontrados.filter(
                    Q(part_number__icontains=q_componente) | Q(descricao__icontains=q_componente) | Q(tipo__nome__icontains=q_componente)
                )
                componentes_inativos = componentes_inativos.filter(
                    Q(part_number__icontains=q_componente) | Q(descricao__icontains=q_componente) | Q(tipo__nome__icontains=q_componente)
                )
                
        
    componente_form = ComponenteFormPreAdd()
    tipo_componente_form = TipoComponenteAdd()
    return render_to_response('frontend/producao/producao-listar-componentes.html', locals(), context_instance=RequestContext(request),)




@user_passes_test(possui_perfil_acesso_producao)
def adicionar_componentes(request):
    if request.POST.get('adicionar-componente', None):
        identificador = request.POST.get('identificador', None)
        tipo = request.POST.get('tipo', None)
        form_add_componente = ComponenteFormAdd(request.POST, request.FILES, identificador=identificador, tipo=tipo)
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
        part_number = u"%s-%s%s" % (pn_prepend, tipo.slug.upper(), "%04d" % identificador)
        return render_to_response('frontend/producao/producao-adicionar-componentes.html', locals(), context_instance=RequestContext(request),)    
    else:
        # retorna à listagem
        messages.warning(request, u"Nenhuma ação tomada. É preciso escolher o tipo de Componente para adicionar")
        return redirect(reverse('producao:listar_componentes'))

class FormEditarComponente(forms.ModelForm):
    class Meta:
        model = Componente
        fields = "descricao", "nacionalidade", 'ncm', 'lead_time', 'medida'

@user_passes_test(possui_perfil_acesso_producao)
def editar_componente(request, componente_id):
    componente = get_object_or_404(Componente.objects.select_related(), pk=componente_id)
    if request.POST:
        editar_componente_form = FormEditarComponente(request.POST, instance=componente)
        if editar_componente_form.is_valid():
            editar_componente_form.save()
            messages.success(request, u"Sucesso! Componente alterado.")
            return redirect(reverse("producao:ver_componente", args=[componente.id]))
    else:
        editar_componente_form = FormEditarComponente(instance=componente)
    return render_to_response('frontend/producao/producao-editar-componente.html', locals(), context_instance=RequestContext(request),)    


@user_passes_test(possui_perfil_acesso_producao)
def inativar_componente(request, componente_id):
    componente = get_object_or_404(Componente.objects.select_related(), pk=componente_id)
    pode = True
    if componente.total_em_estoques() or componente.total_unico_participacoes():
        pode = False
    if request.GET.get('confirmar'):
        componente.ativo = False
        componente.save()
        messages.success(request, "Sucesso! Componente Inativado")
        return redirect(reverse("producao:ver_componente", args=[componente.id]))
    # verifica se possui no estoque
    return render_to_response('frontend/producao/producao-inativar-componente.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def ativar_componente(request, componente_id):
    componente = get_object_or_404(Componente.objects.select_related(), pk=componente_id)
    pode = True
    if componente.total_em_estoques() or componente.total_unico_participacoes():
        pode = False
    if request.GET.get('confirmar'):
        componente.ativo = True
        componente.save()
        messages.success(request, "Sucesso! Componente Ativado")
        return redirect(reverse("producao:ver_componente", args=[componente.id]))
    # verifica se possui no estoque
    return render_to_response('frontend/producao/producao-ativar-componente.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def matriz_componente_padrao_por_subproduto(request, componente_id):
    componente = get_object_or_404(Componente, pk=componente_id)
    return render_to_response('frontend/producao/producao-ver-componente-matriz-componente-padrao-por-subproduto.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def ver_componente(request, componente_id):
    componente = get_object_or_404(Componente.objects.select_related(), pk=componente_id)
    lancamentos = LancamentoComponente.objects.filter(componente=componente, nota__status='l').order_by('criado')
    # memorias: LinhaFornecedorFabricanteComponente
    memorias = LinhaFornecedorFabricanteComponente.objects.filter(componente=componente)
    fornecedores = LancamentoComponente.objects.filter(componente=componente, nota__status='l').values('nota__fabricante_fornecedor__nome').annotate(total=Sum('quantidade'))
    fabricantes = LancamentoComponente.objects.filter(componente=componente, nota__status='l').values('fabricante__nome').annotate(total=Sum('quantidade'))
    posicoes_estoque = []
    participacoes_linha_componente_padrao = componente.opcaolinhasubproduto_set.filter(padrao=True)
    participacoes_linha_componente_alternativo = componente.opcaolinhasubproduto_set.exclude(padrao=True)
    for estoque in EstoqueFisico.objects.all():
        try:
            posicao = estoque.posicaoestoque_set.filter(componente=componente).order_by('-data_entrada')[0]
        except:
            posicao = None
        if posicao:
            valor = posicao.quantidade * posicao.componente.preco_medio_unitario
            posicoes_estoque.append((posicao, valor))
    # Anexos
    if request.POST:
        if request.POST.get('anexar-documento', None):
            form_anexos = ArquivoAnexoComponenteForm(request.POST, request.FILES, componente=componente)
            if form_anexos.is_valid():
                try:
                    anexo = form_anexos.save()
                    messages.success(request, u"Sucesso! Arquivo %s Anexado!" % anexo)
                    return(redirect(reverse('producao:ver_componente', args=[anexo.componente.id,]) + "#arquivos"))
                except:
                    raise
                    messages.error(request, u"Erro! Arquivo %s NÃO Anexado!" % anexo)
        if request.POST.get('anexar-imagem', None): 
            form_imagem = ImagemComponenteForm(request.POST, request.FILES, instance=componente)
            if form_imagem.is_valid():
                try:
                    anexo = form_imagem.save()
                    messages.success(request, u"Sucesso! Imagem Alterada!")
                except:
                    raise
                    messages.error(request, u"Erro! Imagem NÃO Alterada!")
                
    else:
        form_anexos = ArquivoAnexoComponenteForm(componente=componente)
        form_imagem = ImagemComponenteForm(instance=componente)
    return render_to_response('frontend/producao/producao-ver-componente.html', locals(), context_instance=RequestContext(request),)    
    
    

@user_passes_test(possui_perfil_acesso_producao)
def ver_componente_apagar_anexo(request, componente_id, anexo_id):
    anexo = get_object_or_404(ArquivoAnexoComponente, componente__id=componente_id, pk=anexo_id)
    try:
        anexo.delete()
        messages.success(request, u"Sucesso! Anexo %s Apagado!" % anexo)
    except:
        messages.error(request, u"Erro! Anexo %s não Apagado!" % anexo)
    return(redirect(reverse('producao:ver_componente', args=[anexo.componente.id,]) + "#arquivos"))

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
        self.fields['componente'].widget = forms.HiddenInput()
        
    
    class Meta:
        model = LinhaFornecedorFabricanteComponente


@user_passes_test(possui_perfil_acesso_producao)
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



@user_passes_test(possui_perfil_acesso_producao)
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


@user_passes_test(possui_perfil_acesso_producao)
def listar_fabricantes_fornecedores(request):
    tipos_possiveis = FABRICANTE_FORNECEDOR_TIPO_CHOICES
    fab_for_encontrados = FabricanteFornecedor.objects.all()
    if request.GET:
        q_fab_for = request.GET.get('q_fab_for', None)
        q_tipo = request.GET.get('q_tipo', None)
        if q_fab_for:
            if q_fab_for == "todos":
                fab_for_encontrados = FabricanteFornecedor.objects.all()
            else:
                fab_for_encontrados = FabricanteFornecedor.objects.filter(
                    Q(cnpj__icontains=q_fab_for) | Q(nome__icontains=q_fab_for)
                )
        else:
            fab_for_encontrados = FabricanteFornecedor.objects.all()

        if q_tipo:
            if q_tipo != "no":
                fab_for_encontrados = fab_for_encontrados.filter(tipo=q_tipo)
            else:
                fab_for_encontrados = fab_for_encontrados.filter(tipo='')
                
    return render_to_response('frontend/producao/producao-listar-fabricantes-fornecedores.html', locals(), context_instance=RequestContext(request),)    



@user_passes_test(possui_perfil_acesso_producao)
def ver_fabricantes_fornecedores(request, fabricante_fornecedor_id):
    fabricante_fornecedor = get_object_or_404(FabricanteFornecedor, pk=fabricante_fornecedor_id)
    linhas_de_nota_do_fornecedor = LancamentoComponente.objects.filter(nota__fabricante_fornecedor=fabricante_fornecedor).order_by('componente__part_number')
    linhas_de_nota_do_fabricante = LancamentoComponente.objects.filter(fabricante=fabricante_fornecedor).order_by('componente__part_number')
    memorias = LinhaFornecedorFabricanteComponente.objects.filter(fornecedor=fabricante_fornecedor)
    return render_to_response('frontend/producao/producao-ver-fabricante-fornecedor.html', locals(), context_instance=RequestContext(request),)    
    


@user_passes_test(possui_perfil_acesso_producao)
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


@user_passes_test(possui_perfil_acesso_producao)
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

# ESTOQUES
class ConsultaEstoque(forms.Form):

    componente = forms.ModelChoiceField(queryset=Componente.objects.filter(ativo=True), required=False, empty_label="Todos os Componentes")
    estoque = forms.ModelChoiceField(queryset=EstoqueFisico.objects.all(), required=False, empty_label="Todos os Estoques")
    
    def __init__(self, *args, **kwargs):
        super(ConsultaEstoque, self).__init__(*args, **kwargs)
        self.fields['componente'].widget.attrs.update({'class' : 'select2'})
        self.fields['estoque'].widget.attrs.update({'class' : 'select2'})

class MoverEstoque(forms.Form):
    def __init__(self, *args, **kwargs):
        componente_consultado = kwargs.pop('componente_consultado', None)
        estoque_origem = kwargs.pop('estoque_origem', None)
        super(MoverEstoque, self).__init__(*args, **kwargs)
        if componente_consultado:
                self.fields['componente'].initial = componente_consultado
        if estoque_origem:
            self.fields['estoque_origem'].initial = estoque_origem
        self.fields['componente'].widget.attrs.update({'class' : 'select2'})
    
    
    def clean(self):
        cleaned_data = super(MoverEstoque, self).clean()
        quantidade = cleaned_data.get("quantidade")
        estoque_origem = cleaned_data.get("estoque_origem")
        estoque_destino = cleaned_data.get("estoque_destino")
        componente = cleaned_data.get("componente")
        
        if estoque_origem and estoque_destino:
            if estoque_origem == estoque_destino:
                raise forms.ValidationError("Estoques precisam ser diferentes!")
        
        if componente:
            posicao = componente.posicao_no_estoque(estoque_origem)
            if posicao == 0:
                raise forms.ValidationError(u"Impossível Movimentar o Estoque. Não existe o componente %s no Estoque Origem %s" % (componente, estoque_origem))
            if posicao < quantidade:
                raise forms.ValidationError(u"Impossível Movimentar o Estoque. Só existem %s %s(s) de %s no Estoque %s" % (posicao, componente.get_medida_display(), componente.part_number, estoque_origem))
                
        return cleaned_data    
    
    quantidade = forms.DecimalField(max_digits=15, decimal_places=2, required=True)
    componente = forms.ModelChoiceField(queryset=Componente.objects.filter(ativo=True), required=True)
    estoque_origem = forms.ModelChoiceField(queryset=EstoqueFisico.objects.all(), required=True)
    estoque_destino = forms.ModelChoiceField(queryset=EstoqueFisico.objects.all(), required=True)
    justificativa = forms.CharField(widget=forms.Textarea, required=True)
    

class AlterarEstoque(forms.Form):
    
    def __init__(self, *args, **kwargs):
        estoque = kwargs.pop('estoque', None)
        componente = kwargs.pop('componente', None)
        super(AlterarEstoque, self).__init__(*args, **kwargs)
        self.fields['componente'].widget.attrs.update({'class' : 'select2'})
        if estoque:
            self.fields['estoque'].initial = estoque
        if componente:
            self.fields['componente'].initial = componente
    
    
    def clean(self):
        cleaned_data = super(AlterarEstoque, self).clean()
        quantidade = cleaned_data.get("quantidade")
        alteracao_tipo = cleaned_data.get("alteracao_tipo")
        estoque = cleaned_data.get("estoque")
        componente = cleaned_data.get("componente")
        
        # se operacao for remover, verificar se existe a quantidade
        if alteracao_tipo == "remover":            
            quantidade_atual = componente.posicao_no_estoque(estoque)
            if quantidade_atual < quantidade:
                raise forms.ValidationError(u"Erro! Quantidade no estoque %s é %s, menor do que a quantidade a se remover, %s" % (estoque, quantidade_atual, quantidade))
        
        return cleaned_data
    
    alteracao_tipo = forms.ChoiceField(label="Tipo de Alteração", choices=(('adicionar', 'Adicionar'), ('remover', 'Remover')))
    quantidade = forms.DecimalField(max_digits=15, decimal_places=2, required=True)
    componente = forms.ModelChoiceField(queryset=Componente.objects.filter(ativo=True), required=True,)
    estoque = forms.ModelChoiceField(queryset=EstoqueFisico.objects.all(), required=True)
    justificativa = forms.CharField(widget=forms.Textarea, required=True)

class FiltroMovimentos(forms.Form):

    def __init__(self, *args, **kwargs):
        inicio_initial = kwargs.pop('inicio', None)
        fim_initial = kwargs.pop('fim', None)
        super(FiltroMovimentos, self).__init__(*args, **kwargs)
        self.fields['fim_movimentos'].widget.attrs.update({'class' : 'datepicker'})
        self.fields['inicio_movimentos'].widget.attrs.update({'class' : 'datepicker'})
        if inicio_initial:
            
            self.fields['inicio_movimentos'].initial = inicio_initial
        if fim_initial:
        
            self.fields['fim_movimentos'].initial = fim_initial
        
    inicio_movimentos = forms.DateField(label=u"Início", required=True)
    fim_movimentos = forms.DateField(label=u"Fim", required=True)

class FiltroHistoricos(forms.Form):

    def __init__(self, *args, **kwargs):
        inicio_initial = kwargs.pop('inicio', None)
        fim_initial = kwargs.pop('fim', None)
        super(FiltroHistoricos, self).__init__(*args, **kwargs)
        self.fields['fim_historicos'].widget.attrs.update({'class' : 'datepicker'})
        self.fields['inicio_historicos'].widget.attrs.update({'class' : 'datepicker'})
        if inicio_initial:
            
            self.fields['inicio_historicos'].initial = inicio_initial
        if fim_initial:
        
            self.fields['fim_historicos'].initial = fim_initial
        
    inicio_historicos = forms.DateField(label=u"Início", required=True)
    fim_historicos = forms.DateField(label=u"Fim", required=True)
    
@user_passes_test(possui_perfil_acesso_producao)
def listar_estoque(request):
    try:
        data_ultimo_movimento = PosicaoEstoque.objects.all().order_by('-criado')[0].criado.strftime("%d/%m/%Y")
        data_primeiro_movimento = PosicaoEstoque.objects.all().order_by('-criado').reverse()[0].criado.strftime("%d/%m/%Y")
    except:
        data_ultimo_movimento = None
        data_primeiro_movimento = None
    # totalizadores
    totalizadores = RegistroValorEstoque.objects.all().order_by('-criado')[:10]
    totalizadores_graficos = totalizadores.reverse()
    try:
        data_ultimo_totalizador = RegistroValorEstoque.objects.all().order_by('-data')[0].data.strftime("%d/%m/%Y")
        data_primeiro_totalizador = RegistroValorEstoque.objects.all().order_by('data')[0].data.strftime("%d/%m/%Y")
    except:
        data_ultimo_totalizador = None
        data_primeiro_totalizador = None
    
    form_filtra_historico_totalizador = FiltroHistoricos(inicio=data_primeiro_totalizador, fim=data_ultimo_totalizador)
    form_filtra_historico_movimentos = FiltroMovimentos(inicio=data_primeiro_movimento, fim=data_ultimo_movimento)
    
    if request.POST:
        if request.POST.get('consulta-estoque'):
            form_mover_estoque = MoverEstoque()
            form_alterar_estoque = AlterarEstoque()
            form_consulta_estoque = ConsultaEstoque(request.POST)
            if form_consulta_estoque.is_valid():
                consultado = True
                componente_consultado = form_consulta_estoque.cleaned_data['componente']
                estoque_consultado = form_consulta_estoque.cleaned_data['estoque']
                if not componente_consultado and not estoque_consultado:
                    messages.error(request, "Erro! Deve selecionar pelo menos uma opção!")
                    consultado = False
                # consulta dupla
                elif estoque_consultado and componente_consultado:
                    historicos = PosicaoEstoque.objects.filter(estoque=estoque_consultado, componente=componente_consultado).order_by('-data_entrada')
                    consulta_dupla = True
                    posicaoestoque = componente_consultado.posicao_no_estoque(estoque_consultado)
                    if posicaoestoque and componente_consultado.preco_medio_unitario:
                        valor_no_estoque = posicaoestoque * componente_consultado.preco_medio_unitario
                    else:
                        valor_no_estoque = None
                    # define os forms já sugeridos
                    form_mover_estoque = MoverEstoque(componente_consultado=componente_consultado, estoque_origem=estoque_consultado)
                    form_alterar_estoque = AlterarEstoque(estoque=estoque_consultado, componente=componente_consultado)
                # consulta somente componente
                if componente_consultado and not estoque_consultado:
                    historicos = PosicaoEstoque.objects.filter(componente=componente_consultado).order_by('-data_entrada')
                    consulta_componente = True
                    posicoes_estoque = []
                    for estoque in EstoqueFisico.objects.all():
                        try:
                            posicao = estoque.posicaoestoque_set.filter(componente=componente_consultado).order_by('-data_entrada')[0]
                        except:
                            posicao = None
                        if posicao and posicao.quantidade:
                            valor = posicao.quantidade * posicao.componente.preco_medio_unitario
                            posicoes_estoque.append((posicao, valor, posicao.criado))
                    form_mover_estoque = MoverEstoque(componente_consultado=componente_consultado)
                    form_alterar_estoque = AlterarEstoque(componente=componente_consultado)
                    
                # consulta só estoque
                if not componente_consultado and estoque_consultado:
                    historicos = PosicaoEstoque.objects.filter(estoque=estoque_consultado).order_by('-data_entrada')
                    consulta_estoque = True
                    posicoes_estoque = []
                    for componente_ver in Componente.objects.filter(ativo=True).order_by('part_number'):
                        try:
                            posicao = PosicaoEstoque.objects.filter(componente=componente_ver, estoque=estoque_consultado).order_by('-data_entrada')[0]
                        except:
                            posicao = None
                        if posicao:
                            valor = posicao.quantidade * posicao.componente.preco_medio_unitario
                            posicoes_estoque.append((posicao, valor))
                    total_geral = 0
                    for posicao in posicoes_estoque:
                        total_geral += posicao[1]
                    form_mover_estoque = MoverEstoque(estoque_origem=estoque_consultado)
                    form_alterar_estoque = AlterarEstoque(estoque=estoque_consultado)
        if request.POST.get('movimentar-estoque'):
            form_mover_estoque = MoverEstoque(request.POST)
            form_consulta_estoque = ConsultaEstoque()
            form_alterar_estoque = AlterarEstoque()
            if form_mover_estoque.is_valid():
                # mover estoque
                estoque_origem = form_mover_estoque.cleaned_data['estoque_origem']
                estoque_destino = form_mover_estoque.cleaned_data['estoque_destino']
                componente = form_mover_estoque.cleaned_data['componente']
                quantidade = form_mover_estoque.cleaned_data['quantidade']
                justificativa = form_mover_estoque.cleaned_data['justificativa']
                ## remover a quantidade do estoque origem
                # antiga posicao de origem
                antiga_posicao_origem = componente.posicao_no_estoque(estoque_origem)
                messages.info(request, u"Posição Atual do Estoque Origem %s: %s -> %s" % (estoque_origem, componente.part_number, antiga_posicao_origem))
                # antiga posicao de destino
                antiga_posicao_destino = componente.posicao_no_estoque(estoque_destino)
                messages.info(request, u"Posição Atual do Estoque Destino %s: %s -> %s" % (estoque_destino, componente.part_number, antiga_posicao_destino))
                # REALIZA OPERACAO
                # nova posicao na origem
                nova_posicao_origem = antiga_posicao_origem - quantidade
                PosicaoEstoque.objects.create(componente=componente, estoque=estoque_origem, quantidade=nova_posicao_origem, criado_por=request.user, justificativa=justificativa, quantidade_alterada="- %s" % quantidade)
                messages.warning(request, u"Nova posição no Estoque Origem %s: %s -> %s" % (estoque_origem, componente.part_number, nova_posicao_origem))
                # nova posicao no destino
                nova_posicao_destino = antiga_posicao_destino + quantidade
                PosicaoEstoque.objects.create(componente=componente, estoque=estoque_destino, quantidade=nova_posicao_destino, criado_por=request.user, justificativa=justificativa,  quantidade_alterada="+ %s" % quantidade)
                messages.warning(request, u"Nova posição no Estoque Destino %s: %s -> %s" % (estoque_destino, componente.part_number, nova_posicao_destino))
                # resultado final
                messages.success(request, u"Movido %s %s de Estoque Origem %s para Estoque Destino %s" % (quantidade, componente.part_number, estoque_origem, estoque_destino))
                return redirect(reverse("producao:listar_estoque"))
                
        if request.POST.get('alterar-estoque'):
            form_mover_estoque = MoverEstoque()
            form_consulta_estoque = ConsultaEstoque()
            form_alterar_estoque = AlterarEstoque(request.POST)
            if form_alterar_estoque.is_valid():
                alteracao_tipo = form_alterar_estoque.cleaned_data['alteracao_tipo']
                componente = form_alterar_estoque.cleaned_data['componente']
                estoque = form_alterar_estoque.cleaned_data['estoque']
                quantidade = form_alterar_estoque.cleaned_data['quantidade']
                justificativa = form_alterar_estoque.cleaned_data['justificativa']
                quantidade_atual = componente.posicao_no_estoque(estoque)
                messages.info(request, u"Posição Atual do Estoque %s: %s -> %s" % (estoque, componente.part_number, quantidade_atual))
                if alteracao_tipo == 'remover':
                    nova_quantidade = float(quantidade_atual) - float(quantidade)
                    string_justificada = "- %s" % quantidade
                else:
                    nova_quantidade = float(quantidade_atual) + float(quantidade)
                    string_justificada = "+ %s" % quantidade
                messages.warning(request, u"Nova Posição do Estoque %s: %s -> %s" % (estoque, componente.part_number, nova_quantidade))
                PosicaoEstoque.objects.create(componente=componente, estoque=estoque, quantidade=nova_quantidade, criado_por=request.user, justificativa=justificativa,  quantidade_alterada=string_justificada)
                messages.success(request, u"Sucesso! Posição de Estoque Alterada!")
                return redirect(reverse("producao:listar_estoque"))
                
            
        if request.POST.get('filtrar-historico-estoque'):
            form_consulta_estoque = ConsultaEstoque()
            form_mover_estoque = MoverEstoque()
            form_alterar_estoque = AlterarEstoque()
            form_filtra_historico_totalizador = FiltroHistoricos(request.POST)
            form_filtra_historico_movimentos = FiltroMovimentos()
            if form_filtra_historico_totalizador.is_valid():
                inicio = form_filtra_historico_totalizador.cleaned_data['inicio_historicos']
                fim = form_filtra_historico_totalizador.cleaned_data['fim_historicos']
                totalizadores = RegistroValorEstoque.objects.filter(criado__range=(datetime.datetime.combine(inicio, datetime.time.min), datetime.datetime.combine(fim, datetime.time.max)))
                # reverte ordem do totalizador para gráfico
                totalizadores_graficos = totalizadores.order_by('data')

                filtro_totalizador = True
            
        if request.POST.get('filtrar-historico-movimentos'):
            form_consulta_estoque = ConsultaEstoque()
            form_mover_estoque = MoverEstoque()
            form_alterar_estoque = AlterarEstoque()
            form_filtra_historico_movimentos = FiltroMovimentos(request.POST)
            if form_filtra_historico_movimentos.is_valid():
                inicio = form_filtra_historico_movimentos.cleaned_data['inicio_movimentos']
                fim = form_filtra_historico_movimentos.cleaned_data['fim_movimentos']
                fim = datetime.datetime.combine(fim, datetime.time(23, 59))
                historicos = PosicaoEstoque.objects.filter(criado__range=(datetime.datetime.combine(inicio, datetime.time.min), datetime.datetime.combine(fim, datetime.time.max)))
                filtro_historico = True
                form_filtra_historico_totalizador = FiltroHistoricos(inicio=inicio, fim=fim)
            
    else:
        historicos = PosicaoEstoque.objects.all().order_by('-data_entrada')[:10]
        form_consulta_estoque = ConsultaEstoque()
        form_mover_estoque = MoverEstoque()
        form_alterar_estoque = AlterarEstoque()
    return render_to_response('frontend/producao/producao-listar-estoques.html', locals(), context_instance=RequestContext(request),)    

# SUB PRODUTOS

class SubProdutoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(SubProdutoForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['slug'].widget.attrs['readonly'] = True
    

    class Meta:
        model = SubProduto
        fields = ('ativo', 'imagem', 'slug', 'nome', 'slug', 'descricao', 'possui_tags', 'tipo_de_teste')


class ImagemSubprodutoForm(forms.ModelForm):
    
    class Meta:
        model = SubProduto
        fields = 'imagem',


class ArquivoAnexoSubProdutoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        subproduto = kwargs.pop('subproduto')
        super(ArquivoAnexoSubProdutoForm, self).__init__(*args, **kwargs)
        self.fields['subproduto'].initial  = subproduto
        self.fields['subproduto'].widget = forms.HiddenInput()
        self.fields['nome'].widget.attrs['class'] = 'input-xxlarge'
    
    
    class Meta:
        model = DocumentoTecnicoSubProduto
        fields = 'arquivo', 'nome', 'subproduto'

class AgregarSubProdutoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        subproduto_principal = kwargs.pop('subproduto_principal')
        super(AgregarSubProdutoForm, self).__init__(*args, **kwargs)
        self.fields['subproduto_principal'].initial  = subproduto_principal
        self.fields['subproduto_principal'].widget = forms.HiddenInput()
        self.fields['subproduto_agregado'].queryset = self.fields['subproduto_agregado'].queryset.exclude(id=subproduto_principal.id).filter(ativo=True)
        self.fields['subproduto_agregado'].widget.attrs['class'] = 'select2'
    
    
    def clean_subproduto_agregado(self):
        cleaned_data = super(AgregarSubProdutoForm, self).clean()
        subproduto_agregado = cleaned_data.get("subproduto_agregado")
        subproduto_principal = cleaned_data.get("subproduto_principal")
        agregados_internos = subproduto_agregado.subprodutos_agregados()
        if int(subproduto_principal.id) in agregados_internos:
            raise forms.ValidationError(u"Impossível: Recursividade! Confira a composição deste produto.")
        return subproduto_agregado
    
    class Meta:
        model = LinhaSubProdutoAgregado

@user_passes_test(possui_perfil_acesso_producao)
def listar_subprodutos(request):
    subprodutos_encontrados = SubProduto.objects.filter(ativo=True).order_by('part_number')
    subprodutos_inativos = SubProduto.objects.filter(ativo=False).order_by('part_number')
    if request.GET:
        q_subproduto = request.GET.get('q_subproduto', None)
        if q_subproduto:
            if q_subproduto == "todos":
                subprodutos_encontrados = SubProduto.objects.filter(ativo=True).order_by('part_number')
                subprodutos_inativos = SubProduto.objects.filter(ativo=False).order_by('part_number')
            else:
                subprodutos_encontrados = subprodutos_encontrados.filter(
                    Q(nome__icontains=q_subproduto) | Q(descricao__icontains=q_subproduto) | Q(slug__icontains=q_subproduto) | Q(part_number__icontains=q_subproduto)
                )
                subprodutos_inativos = subprodutos_inativos.filter(
                    Q(nome__icontains=q_subproduto) | Q(descricao__icontains=q_subproduto) | Q(slug__icontains=q_subproduto) | Q(part_number__icontains=q_subproduto)
                )
    return render_to_response('frontend/producao/producao-listar-subprodutos.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def adicionar_subproduto(request):
    if request.POST:
        form = SubProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            subproduto = form.save()
            messages.success(request, u"SubProduto %s Adicionado com sucesso!" % subproduto )
            return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
    else:
        form = SubProdutoForm()
    return render_to_response('frontend/producao/producao-adicionar-subproduto.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def editar_subproduto(request, subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    if request.POST:
        form = SubProdutoForm(request.POST, request.FILES, instance=subproduto)
        if form.is_valid():
            subproduto = form.save()
        messages.success(request, u"Sucesso! Subproduto Alterado!")
        return redirect(reverse("producao:ver_subproduto", args=[subproduto.id,]))
    else:
        form = SubProdutoForm(instance=subproduto)
    return render_to_response('frontend/producao/producao-editar-subproduto.html', locals(), context_instance=RequestContext(request),)    

class FormEnviarSubProdutoParaTeste(forms.Form):

    def __init__(self, *args, **kwargs):
        quantidade_maxima_permitida = kwargs.pop('quantidade_maxima')
        subproduto = kwargs.pop('subproduto', None)
        super(FormEnviarSubProdutoParaTeste, self).__init__(*args, **kwargs)
        self.fields['quantidade_maxima_permitida'] = forms.IntegerField(initial=quantidade_maxima_permitida)
        self.fields['quantidade_maxima_permitida'].widget = forms.HiddenInput()
        self.fields['quantidade_preenchida'].initial = quantidade_maxima_permitida
        self.fields['quantidade_preenchida'].label = u"Quantidade para enviar para teste"
        self.fields['subproduto'].initial=subproduto
        self.fields['subproduto'].widget = forms.HiddenInput()
        self.fields['funcionario'].label= u"Funcionário"        
        self.fields['data_envio'].widget.attrs['class'] = 'datepicker'

    def clean_quantidade_preenchida(self):
        cleaned_data = super(FormEnviarSubProdutoParaTeste, self).clean()
        quantidade_preenchida = cleaned_data.get("quantidade_preenchida")
        quantidade_permitida = cleaned_data.get("quantidade_maxima_permitida")
        if quantidade_preenchida == 0:
            raise forms.ValidationError("Impossível mover 0 :)")
        if int(quantidade_preenchida) > int(quantidade_permitida):
            raise forms.ValidationError("Quantidade máxima permitida: %s" % quantidade_permitida)
        return quantidade_preenchida
    
    def clean_data_envio(self):
        cleaned_data = super(FormEnviarSubProdutoParaTeste, self).clean()
        data_envio = cleaned_data.get('data_envio')
        if data_envio > datetime.date.today():
            raise forms.ValidationError("Data de Envio não pode ser no futuro.")
        return data_envio


    quantidade_maxima_permitida = forms.IntegerField(required=True)
    quantidade_preenchida = forms.IntegerField(required=True)
    subproduto = forms.ModelChoiceField(queryset=SubProduto.objects.filter(ativo=True), empty_label=None)
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all(), required=True)
    data_envio = forms.DateField(label=u"Data de Envio", required=False, initial=datetime.date.today())


@user_passes_test(possui_perfil_acesso_producao)
def inativar_subproduto(request, subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    pode = True
    if subproduto.total_montado or subproduto.total_testando or subproduto.total_funcional or subproduto.total_participacao():
        pode = False
    if request.GET.get('confirmar'):
        subproduto.ativo = False
        subproduto.save()
        messages.success(request, "Sucesso! Sub Produto Inativado!")
        return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
    # verifica se possui no estoque
    return render_to_response('frontend/producao/producao-inativar-subproduto.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def ativar_subproduto(request, subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    if request.GET.get('confirmar'):
        subproduto.ativo = True
        subproduto.save()
        messages.success(request, "Sucesso! Sub Produto Ativado!")
        return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
    # verifica se possui no estoque
    return render_to_response('frontend/producao/producao-ativar-subproduto.html', locals(), context_instance=RequestContext(request),)    

class FormMovimentoSubProduto(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        subproduto = kwargs.pop('subproduto')
        operacao = kwargs.pop('operacao')
        situacao = kwargs.pop('situacao')
        super(FormMovimentoSubProduto, self).__init__(*args, **kwargs)
        self.fields['subproduto'].initial = subproduto
        self.fields['subproduto'].widget = forms.HiddenInput()
        self.fields['quantidade_movimentada'].label = "Quantidade"
        self.fields['operacao'].widget = forms.HiddenInput()
        self.fields['operacao'].initial = operacao
        self.fields['situacao'].widget = forms.HiddenInput()
        self.fields['situacao'].initial = situacao
    
    class Meta:
        model = MovimentoEstoqueSubProduto
        fields = 'quantidade_movimentada', 'justificativa', 'operacao', 'subproduto', 'situacao'


class FormFiltraLinhaDeComponentes(forms.Form):
    
    def __init__(self, *args, **kwargs):
        componentes_possiveis = kwargs.pop('componentes_possiveis', None)
        taggeavel = kwargs.pop('taggeavel', None)
        super(FormFiltraLinhaDeComponentes, self).__init__(*args, **kwargs)
        self.fields['componente'].widget.attrs['class'] = 'select2 input-small'
        self.fields['componente'].choices = componentes_possiveis
        self.fields['componente'].choices.insert(0, ('','Todos os Componentes' ) )
        if not taggeavel:
            del self.fields['tag']
    
    componente = forms.ChoiceField(choices=(), label="Componente", required=False)
    tag = forms.CharField(required=False)

@user_passes_test(possui_perfil_acesso_producao)
def ver_subproduto(request, subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    participacao_subprodutos = LinhaSubProdutoAgregado.objects.filter(subproduto_agregado=subproduto)
    agregado_em_produto = LinhaSubProdutodoProduto.objects.filter(subproduto=subproduto)
    linha_componentes_padrao = OpcaoLinhaSubProduto.objects.filter(linha__subproduto=subproduto, padrao=True)
    # instancia formularios
    form_anexos = ArquivoAnexoSubProdutoForm(subproduto=subproduto)
    form_imagem = ImagemSubprodutoForm(instance=subproduto)
    form_agregar_subproduto = AgregarSubProdutoForm(subproduto_principal=subproduto)
    form_enviar_para_teste = FormEnviarSubProdutoParaTeste(quantidade_maxima=subproduto.total_montado, subproduto=subproduto, prefix="enviar_para_teste")
    form_enviar_para_funcional = FormEnviarSubProdutoParaTeste(quantidade_maxima=subproduto.total_testando, subproduto=subproduto, prefix="enviar_para_funcional")
    # forms de movimentos
    # montado
    form_adiciona_montado = FormMovimentoSubProduto(subproduto=subproduto, operacao='adiciona', situacao=0)
    form_remove_montado = FormMovimentoSubProduto(subproduto=subproduto, operacao='remove', situacao=0)
    # em testes
    form_adiciona_em_testes = FormMovimentoSubProduto(subproduto=subproduto, operacao='adiciona', situacao=1)
    form_remove_em_testes = FormMovimentoSubProduto(subproduto=subproduto, operacao='remove', situacao=1)
    # em funcional
    form_adiciona_funcional = FormMovimentoSubProduto(subproduto=subproduto, operacao='adiciona', situacao=2)
    form_remove_funcional = FormMovimentoSubProduto(subproduto=subproduto, operacao='remove', situacao=2)
    # form de filtro de componente
    c = linha_componentes_padrao.values_list('componente_id', 'componente__part_number', 'componente__descricao')
    componentes_possiveis_choices = [(i[0], "%s - %s" % (i[1], i[2])) for i in c]
    c = set(c)
    form_filtrar_linhas = FormFiltraLinhaDeComponentes(componentes_possiveis=componentes_possiveis_choices, taggeavel=subproduto.possui_tags)
    if request.POST:
        if request.POST.get('filtrar-linhas-componentes', None):            
            form_filtrar_linhas = FormFiltraLinhaDeComponentes(request.POST, componentes_possiveis=componentes_possiveis_choices, taggeavel=subproduto.possui_tags)
            if form_filtrar_linhas.is_valid():
                if form_filtrar_linhas.cleaned_data['componente']:
                    linha_componentes_padrao = linha_componentes_padrao.filter(componente=form_filtrar_linhas.cleaned_data['componente'])
                if subproduto.possui_tags:
                    if form_filtrar_linhas.cleaned_data['tag']:
                        linha_componentes_padrao = linha_componentes_padrao.filter(linha__tag__icontains=form_filtrar_linhas.cleaned_data['tag'])
        if request.POST.get('anexar-documento', None):
            form_anexos = ArquivoAnexoSubProdutoForm(request.POST, request.FILES, subproduto=subproduto)
            if form_anexos.is_valid():
                try:
                    anexo = form_anexos.save()
                    messages.success(request, u"Sucesso! Arquivo %s Anexado!" % anexo)
                    return(redirect(reverse('producao:ver_subproduto', args=[anexo.subproduto.id,]) + "#arquivos"))
                except:
                    raise
                    messages.error(request, u"Erro! Arquivo %s NÃO Anexado!" % anexo)
        if request.POST.get('anexar-imagem', None): 
            form_imagem = ImagemSubprodutoForm(request.POST, request.FILES, instance=subproduto)
            if form_imagem.is_valid():
                try:
                    anexo = form_imagem.save()
                    messages.success(request, u"Sucesso! Imagem Alterada!")
                    return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
                except:
                    raise
                    messages.error(request, u"Erro! Imagem NÃO Alterada!")
        if request.POST.get('agregar-subproduto-btn', None):
            form_agregar_subproduto = AgregarSubProdutoForm(request.POST, subproduto_principal=subproduto)
            if form_agregar_subproduto.is_valid():
                linha_sub_agregado = form_agregar_subproduto.save()
                # salva subproduto para atualizar gatilhos
                linha_sub_agregado.subproduto_principal.save()
                messages.success(request, u"Sucesso! Sub Produto %s agregado %s vezes no SubProduto Principal %s" % (linha_sub_agregado.subproduto_agregado, linha_sub_agregado.quantidade, linha_sub_agregado.subproduto_principal))
                return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
        
        if request.POST.get('enviar-subproduto-teste-btn', None):
            form_enviar_para_teste = FormEnviarSubProdutoParaTeste(request.POST, quantidade_maxima=subproduto.total_montado, subproduto=subproduto, prefix="enviar_para_teste")
            if form_enviar_para_teste.is_valid():
                # OK, pode fazer a operacao
                # primeiro, mover as quantidades
                quantidade_preenchida = form_enviar_para_teste.cleaned_data['quantidade_preenchida']
                data_envio = form_enviar_para_teste.cleaned_data['data_envio']
                funcionario = form_enviar_para_teste.cleaned_data['funcionario']
                # remove do montado
                valor_atual_montado = subproduto.total_montado
                valor_alterado_montado = float(valor_atual_montado) - float(quantidade_preenchida)
                subproduto.total_montado = valor_alterado_montado
                messages.info(request, "Removido de Montado: %s - %s = %s" % (valor_atual_montado, float(quantidade_preenchida), valor_alterado_montado))
                # adiciona ao em teste
                valor_atual_teste = subproduto.total_testando
                valor_alterado_testando = float(valor_atual_teste) + float(quantidade_preenchida)
                subproduto.total_testando = valor_alterado_testando
                messages.info(request, "Adicionado em Testando: %s + %s = %s" % (valor_atual_teste, float(quantidade_preenchida), valor_alterado_testando))
                subproduto.save()
                messages.success(request, u"Sucesso! Movido de Montado para Em Teste: %s" % quantidade_preenchida)
                # cria o registro da entrada
                registro = RegistroEnvioDeTesteSubProduto.objects.create(
                    quantidade=quantidade_preenchida,
                    subproduto=subproduto,
                    funcionario=funcionario,
                    criado_por=request.user,
                    data_envio=data_envio
                )
                messages.success(request, u"Sucesso! Criado o Registro de Teste de SubProduto #%s " % registro.id)
                return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
        
        
        if request.POST.get('enviar-subproduto-funcional-btn', None):
            form_enviar_para_funcional = FormEnviarSubProdutoParaTeste(request.POST, quantidade_maxima=subproduto.total_montado, subproduto=subproduto, prefix="enviar_para_funcional")
            if form_enviar_para_funcional.is_valid():
                quantidade_preenchida = form_enviar_para_funcional.cleaned_data['quantidade_preenchida']
                data_envio = form_enviar_para_funcional.cleaned_data['data_envio']
                funcionario = form_enviar_para_funcional.cleaned_data['funcionario']
                # remove do testando
                valor_atual_testando = subproduto.total_testando
                valor_alterado_testando = float(valor_atual_testando) - float(quantidade_preenchida)
                subproduto.total_testando = valor_alterado_testando
                messages.info(request, "Removido de Testando: %s - %s = %s" % (valor_atual_testando, float(quantidade_preenchida), valor_alterado_testando))
                # adiciona ao em funcional
                valor_atual_funcional = subproduto.total_funcional
                valor_alterado_funcional = float(valor_atual_funcional) + float(quantidade_preenchida)
                subproduto.total_funcional = valor_alterado_funcional
                messages.info(request, "Adicionado em Funcional: %s + %s = %s" % (valor_atual_funcional, float(quantidade_preenchida), valor_alterado_funcional))
                subproduto.save()
                messages.success(request, u"Sucesso! Movido de Testando para Funcional: %s" % quantidade_preenchida)
                # cria o registro de saida de teste
                registro = RegistroSaidaDeTesteSubProduto.objects.create(
                    quantidade=quantidade_preenchida,
                    subproduto=subproduto,
                    funcionario=funcionario,
                    criado_por=request.user,
                    data_envio=data_envio,
                )
                messages.success(request, u"Sucesso! Criado o Registro Saída de Teste de SubProduto #%s " % registro.id)
                return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
            
            
        # movimento de produtos - montado
        if request.POST.get('adiciona-subproduto-montado-btn', None):
            form_adiciona_montado = FormMovimentoSubProduto(request.POST, subproduto=subproduto, operacao='adiciona', situacao=0)
            if form_adiciona_montado.is_valid():
                # registra a alteração de subproduto montado e altera o valor
                movimento = form_adiciona_montado.save(commit=False)
                # for positivo, movimenta
                if movimento.quantidade_movimentada > 0:
                    movimento.quantidade_anterior = subproduto.total_montado
                    movimento.quantidade_nova = subproduto.total_montado + movimento.quantidade_movimentada
                    subproduto.total_montado = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    subproduto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Adicionado %s Sub Produtos %s como Montados" % (movimento.quantidade_movimentada, movimento.subproduto))
                else:
                    messages.error(request, u"Erro! Somente números positivos")
                    
        if request.POST.get('remove-subproduto-montado-btn', None):
            form_remove_montado = FormMovimentoSubProduto(request.POST, subproduto=subproduto, operacao='remove', situacao=0)
            if form_remove_montado.is_valid():
                # registra a alteradacao de produco e altera o valor
                movimento = form_remove_montado.save(commit=False)
                if subproduto.total_montado > movimento.quantidade_movimentada:
                    # possui mais do que quer remover
                    movimento.quantidade_anterior = subproduto.total_montado
                    movimento.quantidade_nova = int(subproduto.total_montado) - int(movimento.quantidade_movimentada)
                    subproduto.total_montado = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    subproduto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Removido %s Sub Produtos %s como Montados" % (movimento.quantidade_movimentada, movimento.subproduto))

                else:
                    messages.warning(request, u"Erro. Este Sub produto possui somente %s Montados" % subproduto.total_montado)
                    
        
        # movimento de produtos - em testes
        if request.POST.get('adiciona-subproduto-testes-btn', None):
            form_adiciona_testes = FormMovimentoSubProduto(request.POST, subproduto=subproduto, operacao='adiciona', situacao=1)
            if form_adiciona_testes.is_valid():
                # registra a alteração de subproduto montado e altera o valor
                movimento = form_adiciona_testes.save(commit=False)
                # for positivo, movimenta
                if movimento.quantidade_movimentada > 0:
                    movimento.quantidade_anterior = subproduto.total_testando
                    movimento.quantidade_nova = subproduto.total_testando + movimento.quantidade_movimentada
                    subproduto.total_testando = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    subproduto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Adicionado %s Sub Produtos %s como Em Testes" % (movimento.quantidade_movimentada, movimento.subproduto))
                else:
                    messages.error(request, u"Erro! Somente números positivos")
                    
        if request.POST.get('remove-subproduto-testes-btn', None):
            form_remove_testes = FormMovimentoSubProduto(request.POST, subproduto=subproduto, operacao='remove', situacao=1)
            if form_remove_testes.is_valid():
                # registra a alteradacao de produco e altera o valor
                movimento = form_remove_testes.save(commit=False)
                if subproduto.total_testando > movimento.quantidade_movimentada:
                    # possui mais do que quer remover
                    movimento.quantidade_anterior = subproduto.total_testando
                    movimento.quantidade_nova = int(subproduto.total_testando) - int(movimento.quantidade_movimentada)
                    subproduto.total_testando = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    subproduto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Removido %s Sub Produtos %s como Testando" % (movimento.quantidade_movimentada, movimento.subproduto))

                else:
                    messages.warning(request, u"Erro. Este Sub produto possui somente %s unidades Testando" % subproduto.total_montado)
                    
        
        

        # movimento de produtos - funcional
        if request.POST.get('adiciona-subproduto-funcional-btn', None):
            form_adiciona_funcional = FormMovimentoSubProduto(request.POST, subproduto=subproduto, operacao='adiciona', situacao=2)
            if form_adiciona_funcional.is_valid():
                # registra a alteração de subproduto montado e altera o valor
                movimento = form_adiciona_funcional.save(commit=False)
                # for positivo, movimenta
                if movimento.quantidade_movimentada > 0:
                    movimento.quantidade_anterior = subproduto.total_funcional
                    movimento.quantidade_nova = subproduto.total_funcional + movimento.quantidade_movimentada
                    subproduto.total_funcional = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    subproduto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Adicionado %s Sub Produtos %s como Funcional" % (movimento.quantidade_movimentada, movimento.subproduto))
                else:
                    messages.error(request, u"Erro! Somente números positivos")
                    
        if request.POST.get('remove-subproduto-funcional-btn', None):
            form_remove_funcional = FormMovimentoSubProduto(request.POST, subproduto=subproduto, operacao='remove', situacao=2)
            if form_remove_funcional.is_valid():
                # registra a alteradacao de produco e altera o valor
                movimento = form_remove_funcional.save(commit=False)
                if subproduto.total_funcional > movimento.quantidade_movimentada:
                    # possui mais do que quer remover
                    movimento.quantidade_anterior = subproduto.total_funcional
                    movimento.quantidade_nova = int(subproduto.total_funcional) - int(movimento.quantidade_movimentada)
                    subproduto.total_funcional = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    subproduto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Removido %s Sub Produtos %s como Funcional" % (movimento.quantidade_movimentada, movimento.subproduto))

                else:
                    messages.warning(request, u"Erro. Este Sub produto possui somente %s unidades Funcionais" % subproduto.total_funcional)
                    

    # definir o total do somatório de componentes
    total_linha_componentes = linha_componentes_padrao.aggregate(Sum('linha__valor_custo_da_linha'))['linha__valor_custo_da_linha__sum']
    return render_to_response('frontend/producao/producao-ver-subproduto.html', locals(), context_instance=RequestContext(request),)    



@user_passes_test(possui_perfil_acesso_producao)
def ver_subproduto_apagar_anexo(request, subproduto_id, anexo_id):
    anexo = get_object_or_404(DocumentoTecnicoSubProduto, subproduto__id=subproduto_id, pk=anexo_id)
    try:
        anexo.delete()
        messages.success(request, u"Sucesso! Anexo %s Apagado!" % anexo)
    except:
        messages.error(request, u"Erro! Anexo %s não Apagado!" % anexo)
    return(redirect(reverse('producao:ver_subproduto', args=[anexo.subproduto.id,]) + "#arquivos"))
    

class LinhaSubProdutoForm(forms.ModelForm):
    
    class Meta:
        model = LinhaSubProduto
        fields = 'tag',

class AdicionarLinhaSubProdutoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        subproduto = kwargs.pop('subproduto')
        super(AdicionarLinhaSubProdutoForm, self).__init__(*args, **kwargs)
        self.fields['subproduto'].initial  = subproduto
        self.fields['subproduto'].widget = forms.HiddenInput()
    
    
    class Meta:
        model = LinhaSubProduto
        fields = 'tag', 'subproduto'

@user_passes_test(possui_perfil_acesso_producao)
def apagar_linha_subproduto(request, subproduto_id, linha_subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    linha = get_object_or_404(LinhaSubProduto, subproduto=subproduto, pk=linha_subproduto_id)
    try:
        linha.delete()
        messages.success(request, "Sucesso! Linha Apagada.")
        # dispalha gatilhos do subproduto
        subproduto.save()
    except:
        messages.error(request, "Erro! Linha não Apagada.")
    return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]) + "#linhas-componente")

@user_passes_test(possui_perfil_acesso_producao)
def editar_linha_subproduto(request, subproduto_id, linha_subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    linha = get_object_or_404(LinhaSubProduto, subproduto=subproduto, pk=linha_subproduto_id)
    if request.POST:
        if request.POST.get('alterar-linha'):
            form = LinhaSubProdutoForm(request.POST, instance=linha)
            if form.is_valid():
                linha = form.save()
                messages.success(request, u"Sucesso! Linha alterada.")
                return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]) + "#linhas-componente")
        elif request.POST.get('alterar-quantidade'):
            try:
                quantidade = request.POST.get('quantidade')
            except:
                quantidade = 0

            opcao_alterada = OpcaoLinhaSubProduto.objects.get(pk=request.POST.get('linha_id'))
            opcao_alterada.quantidade = request.POST.get('quantidade')
            opcao_alterada.save()
            messages.success(request, "Sucesso! Quantidade da Opção alterada.")
            
    else:
        form = LinhaSubProdutoForm(instance=linha)
    return render_to_response('frontend/producao/producao-editar-linha-subproduto.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def adicionar_linha_subproduto(request, subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    if subproduto.possui_tags:
        if request.POST:
            form = AdicionarLinhaSubProdutoForm(request.POST, subproduto=subproduto)
            if form.is_valid():
                linha = form.save()
                messages.success(request, u"Sucesso! Linha Adicionada.")
                return redirect(reverse("producao:editar_linha_subproduto_adicionar_opcao", args=[subproduto.id, linha.id]) + "#linhas-componente")
        else:
            form = AdicionarLinhaSubProdutoForm(subproduto=subproduto)
    else:
        linha = LinhaSubProduto.objects.create(subproduto=subproduto)
        messages.success(request, u"Sucesso! Linha Criada.")
        messages.info(request, u"Defina agora a composição de opções.")
        return redirect(reverse("producao:editar_linha_subproduto_adicionar_opcao", args=[subproduto.id, linha.id]) + "#linhas-componente")
    return render_to_response('frontend/producao/producao-adicionar-linha-subproduto.html', locals(), context_instance=RequestContext(request),)    
    
    

class OpcaoLinhaSubProdutoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        linha = kwargs.pop('linha')
        super(OpcaoLinhaSubProdutoForm, self).__init__(*args, **kwargs)
        self.fields['linha'].initial  = linha
        self.fields['linha'].widget = forms.HiddenInput()
        self.fields['componente'].widget.attrs['class'] = 'select2'
        self.fields['componente'].queryset = Componente.objects.filter(ativo=True)
    
    class Meta:
        model = OpcaoLinhaSubProduto
        fields = 'componente', 'quantidade', 'linha'


@user_passes_test(possui_perfil_acesso_producao)
def editar_linha_subproduto_adicionar_opcao(request, subproduto_id, linha_subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    linha = get_object_or_404(LinhaSubProduto, subproduto=subproduto, pk=linha_subproduto_id)
    if request.POST:
        form = OpcaoLinhaSubProdutoForm(request.POST, linha=linha)
        if form.is_valid():
            
            if linha.opcaolinhasubproduto_set.count() == 0:
                # nao existe nenhuma opcao, esta e a padrao
                opcao = form.save()
                opcao.padrao = True
            else:
                opcao = form.save()
                opcao.padrao = None

            opcao.save()
            # atualiza calculo da linha
            opcao.linha.valor_custo_da_linha = linha.custo()
            opcao.linha.save()
            
            # dispara gatilhos de atualizacao do subproduto
            opcao.linha.subproduto.save()
            
            messages.success(request, u"Sucesso! Opção adiconada com sucesso em %s" % linha)
            return redirect(reverse("producao:editar_linha_subproduto", args=[subproduto.id, linha.id]))
    else:
        form = OpcaoLinhaSubProdutoForm(linha=linha)
    return render_to_response('frontend/producao/producao-editar-linha-subproduto-adicionar-opcao.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def tornar_padrao_opcao_linha_subproduto(request, subproduto_id, linha_subproduto_id, opcao_linha_subproduto_id):
    linha = get_object_or_404(LinhaSubProduto, subproduto__id=subproduto_id, pk=linha_subproduto_id)
    opcao = get_object_or_404(OpcaoLinhaSubProduto, linha=linha, pk=opcao_linha_subproduto_id)
    # verifica se pode:
    # só poderá tornar padrão se ainda não houver componente padrao em alguma das linhas
    inedito = True
    linhas = linha.subproduto.linhasubproduto_set.all()
    for l in linhas:
        if l.opcao_padrao():
            if opcao.componente.id == l.opcao_padrao().componente.id:
                inedito = False
                messages.error(request, u"Impossível tornar esta opção como Padrão: Componente %s já identificado como padrão na Linha #%s" % (opcao.componente.part_number, linha.id))
                return redirect(reverse("producao:editar_linha_subproduto", args=[linha.subproduto.id, linha.id]))
    
    # transforma todas as opcoes da linha em nao padrao
    linha.opcaolinhasubproduto_set.all().update(padrao=None)
    # define a opcao escolhida como padrao
    opcao.padrao = True
    opcao.save()
    # dispara gatilhos de atualizacao do subproduto
    opcao.linha.subproduto.save()
    # atualiza o custo da linha
    opcao.linha.valor_custo_da_linha = linha.custo() or 0
    opcao.linha.save()
    # retorna a exibição da linha
    messages.success(request, u"Sucesso! Nova opção padrão definida!")
    
    return redirect(reverse("producao:editar_linha_subproduto", args=[linha.subproduto.id, linha.id]))

def apagar_opcao_linha_subproduto(request, subproduto_id, linha_subproduto_id, opcao_linha_subproduto_id):
    opcao = get_object_or_404(OpcaoLinhaSubProduto, pk=opcao_linha_subproduto_id, linha__pk=linha_subproduto_id, linha__subproduto__pk=subproduto_id)
    if not opcao.padrao:
        try:
            opcao.delete()
            # dispara gatilhos de atualizacao do subproduto
            opcao.linha.subproduto.save()
            messages.success(request, u"Sucesso! Opção Removida!")
        except:
            messages.error(request, u"Erro ao remover Opção.")
    return redirect(reverse("producao:editar_linha_subproduto", args=[opcao.linha.subproduto.id, opcao.linha.id]))

def subproduto_apagar_linha_subproduto_agregado(request, subproduto_id, linha_subproduto_agregado_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    linha_agregada = get_object_or_404(LinhaSubProdutoAgregado, subproduto_principal=subproduto, pk=linha_subproduto_agregado_id)
    linha_agregada.delete()
    # dispara gatilhos de atualizacao do subproduto
    linha_agregada.subproduto_principal.save()
    messages.success(request, u"Sucesso! Linha de SubProduto Agregado ao Produto Principal %s Apagado!" % subproduto)
    return(redirect(reverse('producao:ver_subproduto', args=[subproduto.id,]) + "#sub-produtos-agregados"))


@user_passes_test(possui_perfil_acesso_producao)
def ver_subproduto_relatorios_composicao(request, subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    subprodutos_abaixo = []
    # subprodutos internos de cada subproduto agregado
    subprodutos_abaixo = subproduto.subprodutos_agregados(lista=subprodutos_abaixo, retorna_objeto=True)
    # os subprodutos deste produto
    subprodutos_abaixo = set(subprodutos_abaixo)
    return render_to_response('frontend/producao/producao-ver-subproduto-relatorios-composicao.html', locals(), context_instance=RequestContext(request),)    


#
# PRODUTO
#


## FORMS

class ProdutoFinalForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ProdutoFinalForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['slug'].widget.attrs['readonly'] = True
    
    
    class Meta:
        model = ProdutoFinal
        fields = ('imagem', 'nome', 'slug', 'descricao', 'quantidade_estimada_producao_semanal', 'quantidade_maxima_estocavel')

class AdicionarLinhaSubProdutoAoProdutoFinalForm(forms.ModelForm):
    
    
    def __init__(self, *args, **kwargs):
        produto = kwargs.pop('produto', None)
        super(AdicionarLinhaSubProdutoAoProdutoFinalForm, self).__init__(*args, **kwargs)
        if produto:
            self.fields['produto'].initial = produto
            self.fields['produto'].widget = forms.HiddenInput()    
            self.fields['subproduto'].widget.attrs['class'] = 'select2'                  
    
    class Meta:
        model = LinhaSubProdutodoProduto


class AdicionarLinhaComponenteAvulsoAoProdutoFinalForm(forms.ModelForm):
    
    
    def __init__(self, *args, **kwargs):
        produto = kwargs.pop('produto', None)
        super(AdicionarLinhaComponenteAvulsoAoProdutoFinalForm, self).__init__(*args, **kwargs)
        if produto:
            self.fields['produto'].initial = produto
            self.fields['produto'].widget = forms.HiddenInput()  
            self.fields['componente'].widget.attrs['class'] = 'select2'          
            self.fields['componente'].queryset = Componente.objects.filter(ativo=True)
    
    class Meta:
        model = LinhaComponenteAvulsodoProduto

class AlterarImagemProduto(forms.ModelForm):
    
    class Meta:
        model = ProdutoFinal
        fields = 'imagem',

class ArquivoAnexoProdutoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        produto = kwargs.pop('produto')
        super(ArquivoAnexoProdutoForm, self).__init__(*args, **kwargs)
        self.fields['produto'].initial  = produto
        self.fields['produto'].widget = forms.HiddenInput()
        self.fields['nome'].widget.attrs['class'] = 'input-xxlarge'


    class Meta:
        model = DocumentoTecnicoProduto
        fields = 'arquivo', 'nome', 'produto'
    
    

## VIEWS
##

@user_passes_test(possui_perfil_acesso_producao)
def ver_produto_apagar_anexo(request, produto_id, anexo_id):
    anexo = get_object_or_404(DocumentoTecnicoProduto, produto__pk=produto_id, pk=anexo_id)
    try:
        anexo.delete()
        messages.success(request, u"Sucesso! Anexo %s Apagado!" % anexo)
    except:
        messages.error(request, u"Erro! Anexo %s não Apagado!" % anexo)
    return(redirect(reverse('producao:ver_produto', args=[anexo.produto.id,]) + "#arquivos"))

@user_passes_test(possui_perfil_acesso_producao)
def listar_produtos(request):
    produtos_encontrados = ProdutoFinal.objects.filter(ativo=True).order_by('part_number')
    produtos_inativos = ProdutoFinal.objects.filter(ativo=False).order_by('part_number')
    if request.GET:
        q_produto = request.GET.get('q_produto', True)
        if q_produto:
            if q_produto == "todos":
                produtos_encontrados = ProdutoFinal.objects.filter(ativo=True)
            else:
                produtos_encontrados = produtos_encontrados.filter(
                    Q(nome__icontains=q_produto) | Q(descricao__icontains=q_produto)
                )
                produtos_inativos = produtos_inativos.filter(
                    Q(nome__icontains=q_produto) | Q(descricao__icontains=q_produto)
                )
                
    return render_to_response('frontend/producao/producao-listar-produtos.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def adicionar_produto(request):
    if request.POST:
        form = ProdutoFinalForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save()
            messages.success(request, u"Sucesso! Produto adicionado.")
            return redirect(reverse("producao:ver_produto", args=[produto.id],))
    else:
        form = ProdutoFinalForm()
    return render_to_response('frontend/producao/producao-adicionar-produto.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def inativar_produto(request, produto_id):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    if request.GET.get('confirmar', None):
        produto.ativo = False
        produto.save()
        messages.success(request, u"Sucesso! Produto Inativado!")
        return redirect(reverse("producao:ver_produto", args=[produto.id]))
    return render_to_response('frontend/producao/producao-inativar-produto.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def ativar_produto(request, produto_id):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    if request.GET.get('confirmar', None):
        produto.ativo = True
        produto.save()
        messages.success(request, u"Sucesso! Produto Ativado!")
        return redirect(reverse("producao:ver_produto", args=[produto.id]))
    return render_to_response('frontend/producao/producao-ativar-produto.html', locals(), context_instance=RequestContext(request),)    



@user_passes_test(possui_perfil_acesso_producao)
def editar_produto(request, produto_id):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    if request.POST:
        form = ProdutoFinalForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            produto = form.save()
            messages.success(request, u"Sucesso! Produto %s editado." % produto)
            return redirect(reverse("producao:ver_produto", args=[produto.id],))
    else:
        form = ProdutoFinalForm(instance=produto)
    return render_to_response('frontend/producao/producao-adicionar-produto.html', locals(), context_instance=RequestContext(request),)    


class FormMovimentoProduto(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        produto = kwargs.pop('produto')
        operacao = kwargs.pop('operacao')
        super(FormMovimentoProduto, self).__init__(*args, **kwargs)
        self.fields['produto'].initial = produto
        self.fields['produto'].widget = forms.HiddenInput()
        self.fields['quantidade_movimentada'].label = "Quantidade"
        self.fields['operacao'].widget = forms.HiddenInput()
        self.fields['operacao'].initial = operacao
    
    class Meta:
        model = MovimentoEstoqueProduto
        fields = 'quantidade_movimentada', 'justificativa', 'operacao', 'produto',


@user_passes_test(possui_perfil_acesso_producao)
def ver_produto(request, produto_id):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    form_adicionar_linha_subproduto = AdicionarLinhaSubProdutoAoProdutoFinalForm(produto=produto)
    form_adicionar_linha_componentes_avulsos = AdicionarLinhaComponenteAvulsoAoProdutoFinalForm(produto=produto)
    form_imagem = AlterarImagemProduto(instance=produto)
    form_anexos = ArquivoAnexoProdutoForm(produto=produto)
    form_adiciona_produzido = FormMovimentoProduto(produto=produto, operacao='adiciona')
    form_remove_produzido = FormMovimentoProduto(produto=produto, operacao='remove')
    linhas_componente_produto = produto.linhacomponenteavulsodoproduto_set.all()
    # quantidade de lancamentos disponíveis:
    lancamentos_disponiveis = produto.ordemproducaoproduto_set.filter(lancamentoprodproduto__vendido=False, lancamentoprodproduto__apagado=False)
    # filtros de componentes do produto
    c = produto.linhacomponenteavulsodoproduto_set.values_list('componente_id', 'componente__part_number', 'componente__descricao')
    c = set(c)
    componentes_possiveis_choices = [(i[0], "%s - %s" % (i[1], i[2])) for i in c]
    form_filtrar_linhas = FormFiltraLinhaDeComponentes(componentes_possiveis=componentes_possiveis_choices, taggeavel=False)
    if request.POST:
        if request.POST.get('filtrar-componentes-do-produto', None):
            form_filtrar_linhas = FormFiltraLinhaDeComponentes(request.POST, componentes_possiveis=componentes_possiveis_choices, taggeavel=False)
            if form_filtrar_linhas.is_valid():
                if form_filtrar_linhas.cleaned_data['componente']:
                    linhas_componente_produto = linhas_componente_produto.filter(componente=form_filtrar_linhas.cleaned_data['componente'])
        if request.POST.get('btn-adicionar-linha-subproduto', None):
            form_adicionar_linha_subproduto = AdicionarLinhaSubProdutoAoProdutoFinalForm(request.POST, produto=produto)
            form_adicionar_linha_componentes_avulsos = AdicionarLinhaComponenteAvulsoAoProdutoFinalForm(produto=produto)
            form_imagem = AlterarImagemProduto(instance=produto)
            form_anexos = ArquivoAnexoProdutoForm(produto=produto)
            if form_adicionar_linha_subproduto.is_valid():
                linha_nova = form_adicionar_linha_subproduto.save()
                messages.success(request, u"Sucesso! Linha Adicionada: %s Unidade(s) de Subproduto %s" % (linha_nova.quantidade, linha_nova.subproduto))
                return redirect(reverse("producao:ver_produto", args=[produto.id],) + "#linhas-subprodutos")
        if request.POST.get('btn-adicionar-componentes-avulsos', None):
            form_adicionar_linha_componentes_avulsos = AdicionarLinhaComponenteAvulsoAoProdutoFinalForm(request.POST, produto=produto)
            form_adicionar_linha_subproduto = AdicionarLinhaSubProdutoAoProdutoFinalForm(produto=produto)
            form_imagem = AlterarImagemProduto(instance=produto)
            form_anexos = ArquivoAnexoProdutoForm(produto=produto)
            if form_adicionar_linha_componentes_avulsos.is_valid():
                linha_nova =  form_adicionar_linha_componentes_avulsos.save()
                messages.success(request, u"Sucesso! Linha Adicionada: %s Unidade(s) de Componente %s" % (linha_nova.quantidade, linha_nova.componente))
                return redirect(reverse("producao:ver_produto", args=[produto.id],) + "#componentes-avulsos")
        if request.POST.get('anexar-imagem', None): 
            form_imagem = AlterarImagemProduto(request.POST, request.FILES, instance=produto)
            if form_imagem.is_valid():
                try:
                    anexo = form_imagem.save()
                    messages.success(request, u"Sucesso! Imagem Alterada!")
                except:
                    raise
                    messages.error(request, u"Erro! Imagem NÃO Alterada!")
        if request.POST.get('anexar-documento', None):
            form_anexos = ArquivoAnexoProdutoForm(request.POST, request.FILES, produto=produto)
            if form_anexos.is_valid():
                try:
                    anexo = form_anexos.save()
                    messages.success(request, u"Sucesso! Arquivo %s Anexado!" % anexo)
                    return(redirect(reverse('producao:ver_produto', args=[anexo.produto.id,]) + "#arquivos"))
                except:
                    raise
                    messages.error(request, u"Erro! Arquivo %s NÃO Anexado!" % anexo)
        
                
        if request.POST.get('adiciona-produto-produzido-btn', None):
            form_adiciona_produzido = FormMovimentoProduto(request.POST, produto=produto, operacao='adiciona')
            if form_adiciona_produzido.is_valid():
                # registra a alteração de subproduto montado e altera o valor
                movimento = form_adiciona_produzido.save(commit=False)
                # for positivo, movimenta
                if movimento.quantidade_movimentada > 0:
                    movimento.quantidade_anterior = produto.total_produzido
                    movimento.quantidade_nova = produto.total_produzido + movimento.quantidade_movimentada
                    produto.total_produzido = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    produto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Adicionado %s Produtos %s como Produzido" % (movimento.quantidade_movimentada, movimento.produto))
                else:
                    messages.error(request, u"Erro! Somente números positivos")
                    
        if request.POST.get('remove-produto-produzido-btn', None):
            form_remove_produzido = FormMovimentoProduto(request.POST, produto=produto, operacao='remove')
            if form_remove_produzido.is_valid():
                # registra a alteradacao de produco e altera o valor
                movimento = form_remove_produzido.save(commit=False)
                if produto.total_produzido > movimento.quantidade_movimentada:
                    # possui mais do que quer remover
                    movimento.quantidade_anterior = produto.total_produzido
                    movimento.quantidade_nova = int(produto.total_produzido) - int(movimento.quantidade_movimentada)
                    produto.total_produzido = movimento.quantidade_nova
                    movimento.criado_por = request.user
                    produto.save()
                    movimento.save()
                    messages.success(request, u"Sucesso! Removido %s Produtos %s como Produzido" % (movimento.quantidade_movimentada, movimento.produto))

                else:
                    messages.warning(request, u"Erro. Este Sub produto possui somente %s unidades Produzidas" % produto.total_produzido)
    
    # calcula total de linhas de compoenntes exibido
    total_componentes_valores = linhas_componente_produto.values_list('quantidade', 'componente__preco_medio_unitario')
    total_linha_produtos_avulsos = 0
    for t in total_componentes_valores:
        total_linha_produtos_avulsos += t[0] * t[1]
    
        

    return render_to_response('frontend/producao/producao-ver-produto.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)    
def apagar_linha_subproduto_de_produto(request, produto_id, linha_id):
    linha = get_object_or_404(LinhaSubProdutodoProduto, pk=linha_id, produto__pk=produto_id)
    produto = linha.produto
    if request.user.perfilacessoproducao.gerente:
        linha.delete()
        messages.success(request, u"Linha de Sub Produto do Produto %s apagada." % produto)
    else:
        messages.error(request, u"Somente gerente pode apagar")
    return redirect(reverse("producao:ver_produto", args=[produto.id])+ "#linhas-subprodutos")

@user_passes_test(possui_perfil_acesso_producao)    
def apagar_linha_componente_avulso_de_produto(request, produto_id, linha_id):
    linha = get_object_or_404(LinhaComponenteAvulsodoProduto, pk=linha_id, produto__pk=produto_id)
    produto = linha.produto
    if request.user.perfilacessoproducao.gerente:
        linha.delete()
        messages.success(request, u"Linha de Sub Produto do Produto %s apagada." % produto)
    else:
        messages.error(request, u"Somente gerente pode apagar")
    return redirect(reverse("producao:ver_produto", args=[produto.id])+ "#componentes-avulsos")
 
@user_passes_test(possui_perfil_acesso_producao)
def ver_produto_relatorios_composicao(request, produto_id):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    subprodutos_abaixo = []
    # subprodutos internos de cada subproduto agregado
    for linha in produto.linhasubprodutodoproduto_set.all():
        subprodutos_abaixo = linha.subproduto.subprodutos_agregados(lista=subprodutos_abaixo, retorna_objeto=True)
    # os subprodutos deste produto
    subprodutos_abaixo = produto.subprodutos_agregados(lista=subprodutos_abaixo, retorna_objeto=True)
    subprodutos_abaixo = set(subprodutos_abaixo)
    return render_to_response('frontend/producao/producao-ver-produto-relatorios-composicao.html', locals(), context_instance=RequestContext(request),)    
 
 #
 # ORDEM DE PRODUCAO
 #
 
class SelecionarSubProdutoForm(forms.Form):
    
    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade', None)
        if quantidade <= 0:
            raise ValidationError(u"Erro. Quantidade deve ser maior e diferente de 0")
        return quantidade
        
    quantidade = forms.IntegerField(required=True)
    subproduto = forms.ModelChoiceField(queryset=SubProduto.objects.exclude(tipo_de_teste=0), empty_label="Escolha um Sub Produto", label="Sub Produto")
    subproduto.widget.attrs['class'] = 'select2'
    quantidade.widget.attrs['class'] = 'input-mini'

class SelecionarProdutoForm(forms.Form):
    
    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade', None)
        if quantidade <= 0:
            raise ValidationError(u"Erro. Quantidade deve ser maior e diferente de 0")
        return quantidade
    
    quantidade = forms.IntegerField(required=True)
    produto = forms.ModelChoiceField(queryset=ProdutoFinal.objects.filter(ativo=True), empty_label="Escolha um Produto")
    produto.widget.attrs['class'] = 'select2'
    quantidade.widget.attrs['class'] = 'input-mini'
 
 
class FormConverterSubProduto(forms.Form):
     
    def clean(self):
        data = super(FormConverterSubProduto, self).clean()
        if data.get('subproduto_original') == data.get('subproduto_destino'):
            raise ValidationError(u"Erro. Sub Produtos igualmente selecionados.")
        return data

    subproduto_original = forms.ModelChoiceField(queryset=SubProduto.objects.filter(ativo=True).exclude(tipo_de_teste=0), label="Sub Produto Original")
    subproduto_destino = forms.ModelChoiceField(queryset=SubProduto.objects.filter(ativo=True).exclude(tipo_de_teste=0), label="Sub Produto Destino")
    subproduto_original.widget.attrs['class'] = 'select2'
    subproduto_destino.widget.attrs['class'] = 'select2'
    quantidade = forms.IntegerField(required=True)

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao(request):
    form_subproduto = SelecionarSubProdutoForm()
    form_produto = SelecionarProdutoForm()
    form_converter_subproduto = FormConverterSubProduto()
    if request.POST.get('bt-form-subproduto', None):
        form_subproduto = SelecionarSubProdutoForm(request.POST)
        if form_subproduto.is_valid():
            subproduto = get_object_or_404(SubProduto.objects.select_related(), pk=form_subproduto.cleaned_data['subproduto'].id)
            quantidade = form_subproduto.cleaned_data['quantidade']
            return redirect(reverse("producao:ordem_de_producao_subproduto", args=[subproduto.id, quantidade]))
    if request.POST.get('bt-form-produto', None):
        form_produto = SelecionarProdutoForm(request.POST)
        if form_produto.is_valid():
            produto = get_object_or_404(ProdutoFinal.objects.select_related(), pk=form_produto.cleaned_data['produto'].id)
            quantidade = form_produto.cleaned_data['quantidade']
            return redirect(reverse("producao:ordem_de_producao_produto", args=[produto.id, quantidade]))

    if request.POST.get('bt-form-converter', None):
        form_converter_subproduto = FormConverterSubProduto(request.POST)
        if form_converter_subproduto.is_valid():
            data = form_converter_subproduto.cleaned_data
            return redirect(
                reverse(
                    "producao:ordem_de_producao_subproduto_converter",
                    args=[
                        data['quantidade'],
                        data['subproduto_original'].id,
                        data['subproduto_destino'].id,
                        ]
                )
            )
            
        
    return render_to_response('frontend/producao/producao-ordem-de-producao.html', locals(), context_instance=RequestContext(request),)    

class FormConfiguradorSubProduto(forms.Form):
    
    def __init__(self, *args, **kwargs):
        subproduto = kwargs.pop('subproduto', None)
        super(FormConfiguradorSubProduto, self).__init__(*args, **kwargs)
        if subproduto:
            for linha in subproduto.linhasubproduto_set.all():            
                opcao_padrao = linha.opcao_padrao()
                if opcao_padrao:
                    opcao_id = opcao_padrao.id
                else:
                    opcao_id = None
                self.fields['linha-%s' % linha.id] = forms.ModelChoiceField(queryset=linha.opcaolinhasubproduto_set.all(), required=False, initial=opcao_id, label="Linha #%s" % linha.id)
                self.fields['linha-%s' % linha.id].widget.attrs['class'] = 'select2'
                self.fields['linha-%s' % linha.id].required = True
                self.fields['linha-%s' % linha.id].empty_label = None
                if linha.opcaolinhasubproduto_set.all().count() == 1:
                    self.fields['linha-%s' % linha.id].widget = forms.HiddenInput()
                    
    
@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao_subproduto_confirmar(request, subproduto_id, quantidade_solicitada):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    form_configurador_producao_subproduto = FormConfiguradorProducaoSubProduto(request.POST)
    slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
    estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
    #extra configuracao
    if request.POST.get('configuracao', None):
        configuracao = request.POST.get('configuracao', None)
        # interpreta o string para dict
        import ast
        conf = ast.literal_eval(configuracao)
        componentes = subproduto.get_componentes(conf=conf, multiplicador=float(quantidade_solicitada))
        # pega as informacoes da producao
        if form_configurador_producao_subproduto.is_valid():
            data_producao = form_configurador_producao_subproduto.cleaned_data['data_producao']
            funcionario_produtor = form_configurador_producao_subproduto.cleaned_data['funcionario']
            data_producao = form_configurador_producao_subproduto.cleaned_data['data_producao']
            if data_producao > datetime.date.today():
                data_producao = datetime.date.today()
                messages.info(request, u"Atenção: Data de Produção no Futuro. Alterado para Hoje.")

        # registra a ordem de producao
        ordem_producao_subproduto = OrdemProducaoSubProduto.objects.create(
            subproduto=subproduto,
            quantidade=quantidade_solicitada,
            string_producao=componentes,
            criado_por=request.user, 
            funcionario_produtor=funcionario_produtor,
            data_producao=data_producao,
        )
        messages.success(request, "Ordem de Produção criada: %s" % ordem_producao_subproduto)
        # dar baixa em todos os items do componentes
        for item in componentes.items():
            # longo ou inteiro, é componente
            if type(item[0]) == long or type(item[0]) == int:
                #descobre posicao atual do componente no estoque produtor
                posicao_atual = estoque_produtor.posicao_componente(item[0])
                # remove da posicao atual
                nova_quantidade = float(posicao_atual) - float(item[1])
                nova_posicao = PosicaoEstoque.objects.create(
                    componente_id=int(item[0]),
                    estoque=estoque_produtor,
                    quantidade=nova_quantidade,
                    criado_por=request.user,
                    justificativa='Ordem #%s de Produção de Subproduto' % ordem_producao_subproduto.id,
                    quantidade_alterada="-%s (%s)" % (float(item[1]), componentes),
                    ordem_producao_subproduto_referencia=ordem_producao_subproduto
                )
                messages.success(request, u"Nova posição em Estoque de Produção para %s: %s - %s = %s" % (nova_posicao.componente, posicao_atual, float(item[1]), nova_posicao.quantidade))
            elif type(item[0]) == str:
                # descobre o subproduto
                id_subproduto = item[0].split('-')[1]
                subproduto_remover = SubProduto.objects.get(id=id_subproduto)
                posicao_atual = subproduto_remover.total_funcional
                nova_posicao = posicao_atual - float(float(item[1]))
                # remove a quantidade de subproduto funcional
                subproduto_remover.total_funcional = nova_posicao 
                subproduto_remover.save()
                messages.success(request, u"Removido do Total Funcional do Subproduto %s: %s - %s = %s" % (subproduto_remover, posicao_atual, float(item[1]), nova_posicao))
        # incrementa o subproduto como funcional ou montado
        if subproduto.tipo_de_teste == 1:
            # tipo de teste simples, vai direto pro funcional
            total_anterior = subproduto.total_funcional
            novo_total = total_anterior + int(quantidade_solicitada)
            subproduto.total_funcional = novo_total
            messages.success(request, u"Novo Valor de SubProduto %s em Total Funcional: %s + %s = %s" % (subproduto, total_anterior, int(quantidade_solicitada), novo_total))
            situacao=2
        elif subproduto.tipo_de_teste == 2:
            # tipo de teste composto, vai pra seção de montados pra depois testar
            total_anterior = subproduto.total_montado
            novo_total = total_anterior + int(quantidade_solicitada)
            subproduto.total_montado = novo_total
            messages.success(request, u"Novo Valor de SubProduto %s em Total Montado: %s + %s = %s" % (subproduto, total_anterior, int(quantidade_solicitada), novo_total))
            situacao=0
        subproduto.save()
        # registra o movimento
        movimento = MovimentoEstoqueSubProduto.objects.create(
            subproduto = subproduto,
            situacao = situacao,
            operacao = 'adiciona',
            quantidade_movimentada = int(quantidade_solicitada),
            quantidade_anterior = total_anterior,
            quantidade_nova = novo_total,
            justificativa = "Ordem de Produção de Sub Produto #%s" % ordem_producao_subproduto,
            ordem_de_producao = ordem_producao_subproduto,
            criado_manualmente=False,
            criado_por=request.user,
        )
        messages.info(request, u"Registrado o Movimento de Produção de Sub Produto.")
        url_retorno = "%s%s" % (reverse("producao:ordem_de_producao"), "#produzir")
        return redirect(url_retorno)

    return render_to_response('frontend/producao/producao-ordem-de-producao-confirmado.html', locals(), context_instance=RequestContext(request),)


@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao_subproduto_converter(request, quantidade, subproduto_original_id, subproduto_destino_id):
    subproduto_original = SubProduto.objects.get(pk=subproduto_original_id)
    subproduto_destino = SubProduto.objects.get(pk=subproduto_destino_id)
    pode_converter = True
    alerta_movimento = False
    # verifica se possui quantidade a se converter
    if subproduto_original.total_funcional < int(quantidade):
        pode_converter = False
        messages.error(request, u"Impossível Converter. Quantidade de Sub Produto Funcional: %s. MENOR que a quantidade a converter: %s" % (subproduto_original.total_funcional, quantidade))
    # pega todos os componentes dos dois subprodutos em questão
    componentes_original = subproduto_original.get_componentes(multiplicador=quantidade, agrega_subproduto_sem_teste=False)
    componentes_destino = subproduto_destino.get_componentes(multiplicador=quantidade, agrega_subproduto_sem_teste=False)
    # verifica se todos os componentes do sub-produto A
    # estão no subproduto B e com pelo menos a mesma quantidade.
    for item in componentes_original.items():
        componente = Componente.objects.get(pk=item[0])
        try:
            quantidade_no_destino = componentes_destino[item[0]]
            quantidade_na_origem = item[1]
            if quantidade_na_origem > quantidade_no_destino:
                messages.error(request, u"Impossível Converter. Componente %s (ID:%s) Quantidade na Origem: %s, Quantidade no Destino: %s" % (componente.part_number, componente.id, quantidade_na_origem, quantidade_no_destino))
                pode_converter = False
        except KeyError:
            pode_converter = False
            messages.error(request, u"Impossível Converter. Não existe o Componente %s (ID:%s) em produto de Destino" % (componente.part_number, componente.id))
    # agora calcula todas as diferenças
    relatorio = []
    for item in componentes_destino.items():
        componente = Componente.objects.get(pk=item[0])
        try:
            quantidade_na_origem = componentes_original[item[0]]
            quantidade_no_destino = item[1]
            valor = float(quantidade_no_destino) - float(quantidade_na_origem)
        except KeyError:
            # nao existe na origem, contabilizar valor total do destino
            valor = float(item[1])
        total_estoque = componente.total_em_estoques()
        slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
        estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
        posicao_em_estoque_produtor = estoque_produtor.posicao_componente(componente)
        diferenca_estoque_produtor = float(posicao_em_estoque_produtor) - float(valor) 
        # possui no estoque produtor
        if posicao_em_estoque_produtor >= valor:
            linha_no_estoque = True
            tem_estoque = True
            alerta_linha = False
            pode_converter_linha = True
        else:
            if total_estoque >= valor:                    
                linha_no_estoque = True
                alerta_movimento = True
                alerta_linha = True
                tem_estoque = True
                pode_converter_linha = True
                #messages.warning(request, u"Impossível Converter. É preciso mover mais pelo menos %s %s de %s para o Estoque Produtor" % (diferenca, componente.medida, componente.part_number))
            else:
                linha_no_estoque = False
                alerta_linha = False
                tem_estoque = False
                pode_converter = False
                pode_converter_linha = False
                #messages.error(request, u"Impossível Converter. No Estoque Total só possui %s %s de %s, quando o necessário é %s %s" % (total_estoque, componente.medida, componente.part_number, valor, componente.medida))
        if valor < 0:
            linha_no_estoque = False
            valor = 0
        if diferenca_estoque_produtor > 0:
            diferenca_estoque_produtor = 0
            
        relatorio.append((componente, valor, total_estoque, posicao_em_estoque_produtor, linha_no_estoque, alerta_linha, diferenca_estoque_produtor))

    if request.GET.get('confirmado', None):
        confirmado = True
        # processa o relatorio
        for item in relatorio:
            # cria a entrada de referencia
            ordem_producao_conversao_subproduto = OrdemConversaoSubProduto.objects.create(
                subproduto_original=subproduto_original,
                subproduto_destino=subproduto_destino,
                quantidade=quantidade,
                string_producao="A:%s -> B:%s" % (componentes_original, componentes_destino),
                criado_por=request.user, 
            )
            posicao_atual = estoque_produtor.posicao_componente(item[0])
            # remove da posicao atual
            nova_quantidade = float(posicao_atual) - float(item[1])
            nova_posicao = PosicaoEstoque.objects.create(
                componente_id=int(item[0].id),
                estoque=estoque_produtor,
                quantidade=nova_quantidade,
                criado_por=request.user,
                justificativa='Ordem #%s de Conversão de Sub Produto' % ordem_producao_conversao_subproduto.id,
                quantidade_alterada="-%s (A:%s -> B:%s)" % (float(item[1]), componentes_original, componentes_destino),
                ordem_producao_conversao_subproduto_referencia=ordem_producao_conversao_subproduto
            )
            messages.success(request, u"Nova posição em Estoque de Produção para %s: %s - %s = %s" % (nova_posicao.componente, posicao_atual, float(item[1]), nova_posicao.quantidade))
            return redirect(reverse("producao:ordem_de_producao"))
            
        
        
    return render_to_response('frontend/producao/producao-ordem-de-producao-converter-subproduto.html', locals(), context_instance=RequestContext(request),)


class FormConfiguradorProducaoSubProduto(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FormConfiguradorProducaoSubProduto, self).__init__(*args, **kwargs)
        self.fields['data_producao'].widget.attrs['class'] = 'datepicker'
    
    data_producao = forms.DateField(label=u"Data de Produção", required=False, initial=datetime.date.today())
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all(), required=True, label=u"Funcionário Produtor", empty_label=None)

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao_subproduto(request, subproduto_id, quantidade_solicitada):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    if request.POST:
        linhas = []
        form_configurador_subproduto = FormConfiguradorSubProduto(request.POST, subproduto=subproduto)
        form_configurador_producao_subproduto = FormConfiguradorProducaoSubProduto()
        if form_configurador_subproduto.is_valid():
            subproduto_produzivel = subproduto.produzivel(quantidade=quantidade_solicitada)
            # pega estoque de producao
            slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
            estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
            # calcular
            # cria dicionario de configuracao das linhas deste subproduto
            conf = {}
            for linha_field in form_configurador_subproduto.fields:
                opcao = form_configurador_subproduto.cleaned_data[linha_field]
                try:
                    valor = conf[linha.id]
                except:
                    valor = 0
                conf[opcao.linha.id] = opcao.id
            
            # passa a configuracao para gerar o dicionario de componentes
            # deste subproduto
            get_componentes = subproduto.get_componentes(conf=conf, multiplicador=float(quantidade_solicitada))
            get_componentes_nao_agrupados = subproduto.get_componentes(conf=conf, multiplicador=float(quantidade_solicitada), agrega_subproduto_sem_teste=False)
            # aplicar multiplicador de quantidade_solicitada
            
            # assume producao liberada
            producao_liberada = True
            # verifica se no total, possui estoque para fazer todos os produtos
            # presentes em get_componentes
            
            for item in get_componentes.items():    
                if type(item[0]) == long or type(item[0]) == int:
                    # verifica se possui a quantidade total deste componente em estoque
                    qtd_componente = item[1]
                    posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                    # quantidade no estoque insuficiente
                    if qtd_componente > posicao_em_estoque_produtor:
                        faltou = float(qtd_componente) - float(posicao_em_estoque_produtor)
                        producao_liberada = False
                        componente = Componente.objects.get(pk=int(item[0]))
                        messages.error(request, "Quantidade Indisponível (Faltou %s) de Componente ID %s" % (faltou, componente))
                elif type(item[0]) == str:
                    subproduto_id = item[0].split("-")[1]
                    subproduto_usado = SubProduto.objects.get(id=subproduto_id)
                    qtd_subproduto = item[1]
                    quantidade_disponivel = subproduto_usado.total_funcional
                    # quantidade de subprodutos funcionais é menor, esta indisponível
                    if qtd_subproduto > quantidade_disponivel: 
                        producao_liberada = False
                        faltou = float(qtd_subproduto) - float(quantidade_disponivel)
                        messages.error(request, "Quantidade Indisponível (FALTOU: %s) de Sub Produto %s" % (faltou, item[0]))
                    
            
            calculado = True
            quantidades_componente = {}
            quantidades_configuradas = {}
            for linha_field in form_configurador_subproduto.fields:
                linha = form_configurador_subproduto.cleaned_data[linha_field]
                try:
                    quantidade_usada = quantidades_componente[linha.componente.id][1]
                except:
                    quantidade_usada = 0
                # calcula a quantidade de componentes na linha
                quantidade_usada += float(linha.quantidade) * float(quantidade_solicitada)
                # puxa a posicao no estoque
                posicao_em_estoque_produtor = estoque_produtor.posicao_componente(linha.componente)
                # marca se é possível produzir, conforme estoque produtor
                if quantidade_usada > posicao_em_estoque_produtor:
                    pode = False
                    producao_liberada = False
                else:
                    pode = True
                quantidades_componente[linha.componente.id] = (linha, quantidade_usada, posicao_em_estoque_produtor, pode)

            # calcula os subprodutos agregados
            quantidades_agregados = []
            for linha in subproduto.linhasubprodutos_agregados.all():
                total_disponivel = linha.subproduto_agregado.total_disponivel()
                quantidade_usada = float(linha.quantidade) * float(quantidade_solicitada)
                if quantidade_usada > total_disponivel:
                    pode = False
                    producao_liberada = False
                    faltou = float(quantidade_usada) - float(linha.subproduto_agregado.total_disponivel())
                else:
                    pode = True
                quantidades_agregados.append((linha, quantidade_usada, linha.subproduto_agregado.total_disponivel(), pode))

            if producao_liberada:
                for field in form_configurador_subproduto.fields:
                    form_configurador_subproduto[field].widget = forms.HiddenInput()

    else:
        form_configurador_subproduto = FormConfiguradorSubProduto(subproduto=subproduto)
        linhas_sem_alternativo = []
        for linha in subproduto.linhasubproduto_set.all():
            if linha.opcaolinhasubproduto_set.all().count() == 1:
                linhas_sem_alternativo.append(linha)

    return render_to_response('frontend/producao/producao-ordem-de-producao-subproduto.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao_produto_confirmar(request, produto_id, quantidade_solicitada):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    get_componentes = produto.get_componentes_produto(multiplicador=quantidade_solicitada)
    # pega o estoque produto padrao
    slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
    estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
    # cria a ordem de producao
    ordem_producao_produto = OrdemProducaoProduto.objects.create(
        produto=produto,
        quantidade=quantidade_solicitada,
        string_producao=get_componentes,
        criado_por=request.user, 
    )
    
    for item in get_componentes.items():
        # para cada item, verificar tipo (se componente ou subproduto)
        # dar baixa no estoque (para componente) ou total funcional (para subproduto)
        # e incremental o total_produzido do produto com a quantidade solicitada
        # longo ou inteiro, é componente
        # registra a ordem de producao do Produto
        if type(item[0]) == long or type(item[0]) == int:
            #descobre posicao atual do componente no estoque produtor
            posicao_atual = estoque_produtor.posicao_componente(item[0])
            # remove da posicao atual
            nova_quantidade = float(posicao_atual) - float(item[1])
            nova_posicao = PosicaoEstoque.objects.create(
                componente_id=int(item[0]),
                estoque=estoque_produtor,
                quantidade=nova_quantidade,
                criado_por=request.user,
                justificativa='Ordem #%s de Produção de Produto' % ordem_producao_produto.id,
                quantidade_alterada="-%s (%s)" % (float(item[1]), get_componentes),
                ordem_producao_produto_referencia=ordem_producao_produto
            )
            messages.success(request, u"Nova posição em Estoque de Produção para %s: %s - %s = %s" % (nova_posicao.componente, posicao_atual, float(item[1]), nova_posicao.quantidade))
        elif type(item[0]) == str:
            # descobre o subproduto
            id_subproduto = item[0].split('-')[1]
            subproduto_remover = SubProduto.objects.get(id=id_subproduto)
            posicao_atual = subproduto_remover.total_funcional
            nova_posicao = posicao_atual - float(float(item[1]))
            # remove a quantidade de subproduto funcional
            subproduto_remover.total_funcional = nova_posicao 
            subproduto_remover.save()
            messages.success(request, u"Removido do Total Funcional do Sub Produto %s: %s - %s = %s" % (subproduto_remover, posicao_atual, float(item[1]), nova_posicao))

    # incrementa o produto em seu total_produzido
    produto_total_produzido = produto.total_produzido
    novo_valor = int(produto_total_produzido) + int(quantidade_solicitada)
    produto.total_produzido = novo_valor
    produto.save()
    messages.success(request, u"Novo Valor para Total Produzido do Produto %s: %s -> %s" % (produto.part_number, produto_total_produzido, novo_valor))
    # registra o incremento no movimento de producao
    movimento = MovimentoEstoqueProduto.objects.create(
        produto = produto,
        quantidade_movimentada = int(quantidade_solicitada),
        quantidade_anterior = produto_total_produzido,
        quantidade_nova = novo_valor,
        justificativa = "Ordem de Produção de Produto #%s " % ordem_producao_produto.id,
        ordem_de_producao = ordem_producao_produto,
        criado_manualmente=False,
        criado_por=request.user,
    )
    messages.info(request, u"Movimento de Estoque de Produto Registrado: #%s" % movimento.id)
    # adiciona a entidade LancamentoDeProducaoDeProduto
    # tantas vezes quantos produtos produzidos
    for i in range(int(quantidade_solicitada)):
        # para cada um solicitado, criar entrada de lancamento
        lancamento = LancamentoProdProduto.objects.create(
            ordem_de_producao = ordem_producao_produto,
            produto=produto,
            adicionado_manualmente=False,
        )
        # para cada subproduto testável deste produto, criar uma linha de testes
        for subproduto_testavel in ordem_producao_produto.produto.subprodutos_testaveis.all():
            linha = LinhaTesteLancamentoProdProduto.objects.create(
                lancamento_de_producao=lancamento,
                subproduto_testavel=subproduto_testavel
            )
            messages.info(request, u"Linha de Teste #%s de Lançamento %s criado para Sub Produto %s " % (linha.id, lancamento, linha.subproduto_testavel))
        messages.success(request, u"Sucesso! Criado novo Lançamento de Produção: #%s" % lancamento.id)
    return redirect(reverse("producao:ordem_de_producao"))

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao_produto(request, produto_id, quantidade_solicitada):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    get_componentes = produto.get_componentes_produto(multiplicador=quantidade_solicitada)
    if request.POST:
        if request.POST.get('verificar-producao', None):
            producao_liberada = True
            slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
            estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
            #verifica toda a produção conforme a notação de componentes
            for item in get_componentes.items():
                if type(item[0]) == long or type(item[0]) == int:
                    # verifica se possui a quantidade total deste componente em estoque
                    qtd_componente = item[1]
                    posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                    # quantidade no estoque insuficiente
                    if qtd_componente > posicao_em_estoque_produtor:
                        faltou = float(qtd_componente) - float(posicao_em_estoque_produtor)
                        producao_liberada = False
                        componente = Componente.objects.get(pk=int(item[0]))
                        messages.error(request, "Quantidade Indisponível (Faltou %s) de Componente ID %s" % (faltou, componente))
                elif type(item[0]) == str:
                    subproduto_id = item[0].split("-")[1]
                    subproduto_usado = SubProduto.objects.get(id=subproduto_id)
                    qtd_subproduto = item[1]
                    # aqui eh quantidade funcional, pois o subproduto sem teste vem como
                    # inteiro acima, junto aos compontentes.
                    quantidade_disponivel = subproduto_usado.total_funcional
                    # quantidade de subprodutos funcionais é menor, esta indisponível
                    if qtd_subproduto > quantidade_disponivel:
                        producao_liberada = False
                        faltou = float(qtd_subproduto) - float(quantidade_disponivel)
                        messages.error(request, "Quantidade Indisponível (FALTOU: %s) de SubProduto %s" % (faltou, item[0]))

            # verifica individualmente, cada componente
            quantidades_componente = {}
            for linha in produto.linhacomponenteavulsodoproduto_set.all():
                try:
                    quantidade_usada = quantidades_componente[linha.componente.id][1]
                except:
                    quantidade_usada = 0
                # calcula a quantidade de componentes na linha
                quantidade_usada += float(linha.quantidade) * float(quantidade_solicitada)
                # puxa a posicao no estoque
                posicao_em_estoque_produtor = estoque_produtor.posicao_componente(linha.componente)
                # marca se é possível produzir, conforme estoque produtor
                if quantidade_usada > posicao_em_estoque_produtor:
                    pode = False
                    producao_liberada = False
                else:
                    pode = True
                quantidades_componente[linha.componente.id] = (linha, quantidade_usada, posicao_em_estoque_produtor, pode)
            
            # calcula os subprodutos agregados
            quantidades_agregados = []
            for linha in produto.linhasubprodutodoproduto_set.all():
                total_disponivel = linha.subproduto.total_disponivel()
                quantidade_usada = float(linha.quantidade) * float(quantidade_solicitada)
                if quantidade_usada > total_disponivel:
                    pode = False
                    producao_liberada = False
                    faltou = float(quantidade_usada) - float(linha.subproduto.total_disponivel())
                else:
                    pode = True
                quantidades_agregados.append((linha, quantidade_usada, linha.subproduto.total_disponivel(), pode))
            
            calculado = True
    # contabilizar todos os componentes deste produto
    return render_to_response('frontend/producao/producao-ordem-de-producao-produto.html', locals(), context_instance=RequestContext(request),)

class SelecionarProdutoUnicoForm(forms.Form):
    produto = forms.ModelChoiceField(queryset=ProdutoFinal.objects.filter(ativo=True), empty_label=None)
    produto.widget.attrs['class'] = 'select2'


@user_passes_test(possui_perfil_acesso_producao)
def arvore_de_produto(request):
    seleciona_produto = SelecionarProdutoUnicoForm()
    if request.GET:
        filtro = True
        seleciona_produto = SelecionarProdutoUnicoForm(request.GET)
        if seleciona_produto.is_valid():
            produtos = ProdutoFinal.objects.filter(pk=seleciona_produto.cleaned_data['produto'].id)
    else:
        produtos = ProdutoFinal.objects.filter(ativo=True)
    return render_to_response('frontend/producao/producao-arvore-de-produto.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def arvore_de_produto_ajax_subproduto(request, subproduto_id, parente):
    parent = request.GET.get('parent')
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    return render_to_response('frontend/producao/producao-arvore-de-produto-ajax-subproduto.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def registro_de_testes(request):
    return render_to_response('frontend/producao/producao-registro-de-testes.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def totalizador_de_producao(request):
    produtos = ProdutoFinal.objects.filter(ativo=True).order_by('part_number')
    subprodutos = SubProduto.objects.filter(ativo=True).order_by('part_number')
    return render_to_response('frontend/producao/producao-ordem-de-producao-ajax-totalizador-producao.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def producao_combinada(request):
    produtos = ProdutoFinal.objects.filter(ativo=True).order_by('-total_produzido')
    subprodutos = SubProduto.objects.filter(ativo=True).order_by('-total_funcional')
    return render_to_response('frontend/producao/producao-ordem-de-producao-producao-combinada.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def producao_combinada_calcular(request):
    agora = datetime.datetime.now()
    if request.POST:
        teste = []
        producao_liberada = True
        dic = {}
        # para cada um, descobrir se produto ou subproduto
        quantidade_analisada = []
        for key, value in request.POST.iteritems():
            try:
                considerar_subprodutos = request.POST.get('conseridar_subprodutos_funcionais', False)
                considerar_produtos = request.POST.get('conseridar_produtos_produzidos', False)
                if key != "csrfmiddlewaretoken" and value != "on" and value.isdigit():
                    tipo = key.split("-")[0]
                    tipo_id = key.split("-")[1]
                    if tipo in ['produto', 'subproduto']:
                        # analise do produto
                        if tipo == 'produto':
                            produto = ProdutoFinal.objects.get(pk=tipo_id)
                            # se for pra considerar os produtos já produzidos,
                            # reduzir
                            if considerar_produtos == "on":
                                valor_multiplicador = int(value) - produto.total_produzido
                            else:
                                valor_multiplicador = value
                            if valor_multiplicador > 0:
                                dic = produto.get_componentes_produto(dic=dic, multiplicador=valor_multiplicador)
                            # gera link do produto
                            link = reverse("producao:ver_produto", args=[produto.id])
                            quantidade_analisada.append((produto, value, link))
                        # analise do subproduto
                        if tipo == 'subproduto':
                            subproduto = SubProduto.objects.get(pk=tipo_id)
                            if considerar_subprodutos == "on":
                                valor_multiplicador = int(value) - subproduto.total_funcional
                            else:
                                valor_multiplicador = value
                            # se valor encontrado for maior que 0, calcular
                            # se for menor, significa que a quantidade em estoque / funcional é superior ao planejado de produção, nem precisa calcular
                            if valor_multiplicador > 0:
                                dic = subproduto.get_componentes(dic=dic, multiplicador=valor_multiplicador)
                            # gera link do subproduto
                            link = reverse("producao:ver_subproduto", args=[subproduto.id])
                            quantidade_analisada.append((subproduto, value, link))
                            
            except:
                raise
        # verificar cada uma dessas quantidades
        #verifica toda a produção conforme a notação de componentes
        get_componentes = dic
        relatorio_producao = []
        import decimal
        valor_total_compra = 0
        for item in get_componentes.items():
            if type(item[0]) == long or type(item[0]) == int:
                # verifica se possui a quantidade total deste componente em estoque
                qtd_componente = item[1]
                componente = Componente.objects.get(pk=int(item[0]))
                posicao_em_estoque = componente.total_em_estoques()
                
                # assume-se que pode produzir com estoque, e que não faltaram componentes
                pode = True
                faltou = None
                if float(qtd_componente) > float(posicao_em_estoque):
                    # quantidade menor
                    faltou = float(posicao_em_estoque) - float(qtd_componente)
                    producao_liberada = False
                    pode = False
                    # item de producao, #quantidade_atual, #posicao_estoque, #faltante 
                    qtd_componente = decimal.Decimal(qtd_componente)
                    faltou = decimal.Decimal(faltou)
                    # total da compra
                    valor_item = faltou * componente.preco_medio_unitario * -1
                    valor_total_compra += valor_item
                    link = reverse("producao:ver_componente", args=[componente.id])
                    relatorio_producao.append((componente, componente.descricao, qtd_componente, posicao_em_estoque, faltou, pode, valor_item, link))
            elif type(item[0]) == str:
                subproduto_id = item[0].split("-")[1]
                subproduto = SubProduto.objects.get(pk=subproduto_id)
                subproduto_usado = SubProduto.objects.get(id=subproduto_id)
                qtd_subproduto = item[1]
                # aqui eh quantidade funcional, pois o subproduto sem teste vem como
                # inteiro acima, junto aos compontentes.
                quantidade_disponivel = subproduto_usado.total_funcional
                # quantidade de subprodutos funcionais é menor, esta indisponível
                pode = True
                faltou = None
                if int(qtd_subproduto) > int(quantidade_disponivel):
                    producao_liberada = False
                    faltou =  float(quantidade_disponivel) - float(qtd_subproduto)
                    pode = False
                    qtd_subproduto = decimal.Decimal(qtd_subproduto)
                    faltou = decimal.Decimal(faltou)
                    # total da compra
                    valor_item = faltou * subproduto.custo() * -1
                    valor_total_compra += valor_item
                    link = reverse("producao:ver_subproduto", args=[subproduto_id])
                    relatorio_producao.append((subproduto_usado, subproduto_usado.descricao, qtd_subproduto, quantidade_disponivel, faltou, pode, valor_item, link))
             
    return render_to_response('frontend/producao/producao-ordem-de-producao-producao-combinada-calcular.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def relatorio_compras_automatico(request):
    '''
    Contabilizar a quantidade de componentes de todos os produtos com o
    multiplicador sendo o QEPS. Para cada subproduto com teste encontrado,
    dimunir sua quantidade de total_funcional se faltar, contabilizar os
    componentes do subproduto faltante, considerando o multiplicador o valor
    faltado.
    Depois de descobrir a quantidade  total para cumprir o QEPS de TODOS os
    produtos cadastrados e ativos, multiplicar essa quantidade pelo valor de
    lead time, encontrando a quantidade mínima de esotque do componente,
    que deve ser armazenado no componente, juntamente com a hora do calculo.
    Após o calculo, exibir uma tabela, com componente, quantidade mínima
    para QEPS, quantidade em estoque produtor, e diferença desses dois
    ultimos valores
    '''
    margem_fornecida = request.GET.get('margem', None)
    dic = {}
    slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
    estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
    for produto in ProdutoFinal.objects.filter(ativo=True):
        # para cada produto
        if produto.quantidade_estimada_producao_semanal:
            dic = produto.get_componentes_produto(
                multiplicador=produto.quantidade_estimada_producao_semanal,
                dic=dic,
            )
    # dic ficou com todas as quantidades necessarias para QEPS do produto
    for item in dic.items():
        # verificar subprodutos já produzidos
        if type(item[0]) == str:
            subproduto_id = item[0].split("-")[1]
            subproduto_usado = SubProduto.objects.get(id=subproduto_id)
            print "SUBPRODUTO USADO", subproduto_usado
            qtd_disponivel = subproduto_usado.total_funcional
            qtd_subproduto = item[1]
            # remove o subproduto
            print "SUBPRODUTO %s REMOVIDO DA NOTAÇÃO" % subproduto_usado
            del dic[item[0]]
            # qtd faltante = qtd_usado = qtd_disponivel
            quantidade_faltante = qtd_disponivel - qtd_subproduto
            if quantidade_faltante < 0:
                # ex: 20 - 30 = -10, faltou 10
                # faltou componente, é preciso calcular a quantidade de componentes
                #necessarios para fabricar faltantes
                quantidade_faltante = -quantidade_faltante
                dic = subproduto_usado.get_componentes(multiplicador=quantidade_faltante, agrega_subproduto_sem_teste=False, dic=dic)
    
    # calcula a tabelas de leadtime
    tabela_items = []
    valor_total_compra = 0
    
    for item in dic.items():
        valor_item = 0
        if type(item[0]) == long or type(item[0]) == int:
            qtd_componente = item[1]
            posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
            componente = Componente.objects.get(pk=int(item[0]))
            quantidade_lead_time = item[1] * componente.lead_time
            if margem_fornecida:
                margem = float(quantidade_lead_time) * float(margem_fornecida) / float(100)
                quantidade_lead_time = float(quantidade_lead_time) + float(margem)
            diferenca = float(componente.total_em_estoques()) - float(quantidade_lead_time)
            if diferenca > 0:
                ok = True
            else:
                ok = False
                valor_item = float(diferenca) * float(componente.preco_medio_unitario) * -1
                valor_total_compra += valor_item
            link = reverse("producao:ver_componente", args=[componente.id])
            
            tabela_items.append((componente, posicao_em_estoque_produtor, quantidade_lead_time, diferenca, ok, link, valor_item))
            
    return render_to_response('frontend/producao/producao-relatorio-compras-automatico.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def relatorio_compras(request):
    nome_empresa = getattr(settings, 'NOME_EMPRESA', 'Mestria')
    produtos = ProdutoFinal.objects.filter(ativo=True).order_by('-total_produzido')
    subprodutos = SubProduto.objects.filter(ativo=True).order_by('-total_funcional')
    return render_to_response('frontend/producao/producao-ordem-de-producao-relatorio-de-compras.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def relatorio_compras_calcular(request):
    agora = datetime.datetime.now()
    if request.POST:
        teste = []
        producao_liberada = True
        dic = {}
        desconsidera_estoque = request.POST.get('desconsidera-subprodutos-estoque', None)
        # para cada um, descobrir se produto ou subproduto
        quantidade_analisada = []
        for key, value in request.POST.iteritems():
            try:
                if key != "csrfmiddlewaretoken" and value != "on" and value.isdigit():
                    if key == 'margem_componentes':
                        margem_fornecida = value
                    else:
                        tipo = key.split("-")[0]
                        tipo_id = key.split("-")[1]
                        if tipo in ['produto', 'subproduto']:
                            # analise do produto
                            if tipo == 'produto':
                                produto = ProdutoFinal.objects.get(pk=tipo_id)
                                valor_multiplicador = value
                                dic = produto.get_componentes_produto(dic=dic, multiplicador=valor_multiplicador, agrega_subproduto_sem_teste=False)
                                # gera link do produto
                                link = reverse("producao:ver_produto", args=[produto.id])
                                quantidade_analisada.append((produto, value, link))
                            # analise do subproduto
                            if tipo == 'subproduto':
                                subproduto = SubProduto.objects.get(pk=tipo_id)
                                valor_multiplicador = value
                                # se valor encontrado for maior que 0, calcular
                                # se for menor, significa que a quantidade em estoque / funcional é superior ao planejado de produção, nem precisa calcular
                                dic = subproduto.get_componentes(dic=dic, multiplicador=valor_multiplicador, agrega_subproduto_sem_teste=False)
                                # gera link do subproduto
                                link = reverse("producao:ver_subproduto", args=[subproduto.id])
                                quantidade_analisada.append((subproduto, value, link))
                            
            except:
                raise
        # verificar cada uma dessas quantidades
        #verifica toda a produção conforme a notação de componentes
        get_componentes = dic
        relatorio_producao = []
        import decimal
        valor_total_compra = 0
        for item in get_componentes.items():
            if type(item[0]) == long or type(item[0]) == int:
                # verifica se possui a quantidade total deste componente em estoque
                qtd_componente = item[1]
                # aplica a margem de seguranca
                if margem_fornecida:
                    margem = float(qtd_componente) * float(margem_fornecida) / float(100)
                    qtd_componente = float(qtd_componente) + float(margem)
                componente = Componente.objects.get(pk=int(item[0]))
                posicao_em_estoque = componente.total_em_estoques()
                
                # assume-se que pode produzir com estoque, e que não faltaram componentes
                pode = True
                faltou = None
                qtd_componente = decimal.Decimal(qtd_componente)
                valor_item = 0
                if float(qtd_componente) > float(posicao_em_estoque) and not desconsidera_estoque:
                    # quantidade menor
                    faltou = float(posicao_em_estoque) - float(qtd_componente)
                    producao_liberada = False
                    pode = False
                    # item de producao, #quantidade_atual, #posicao_estoque, #faltante 
                    
                    faltou = decimal.Decimal(faltou)
                    # total da compra
                    valor_item = faltou * componente.preco_medio_unitario * -1
                    valor_total_compra += valor_item
                    link = reverse("producao:ver_componente", args=[componente.id])
                    relatorio_producao.append((componente, componente.descricao, qtd_componente, posicao_em_estoque, faltou, pode, valor_item, link))
                if desconsidera_estoque:
                    valor_item = qtd_componente * componente.preco_medio_unitario
                    valor_total_compra += valor_item
                    relatorio_producao.append((componente, componente.descricao, qtd_componente, posicao_em_estoque, 0, 0, valor_item, link))

             
    return render_to_response('frontend/producao/producao-ordem-de-producao-relatorio-de-compras-calcular.html', locals(), context_instance=RequestContext(request),)



class FormOrdemDeCompraFiltro(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FormOrdemDeCompraFiltro, self).__init__(*args, **kwargs)
        self.fields['data_inicio_abertura'].widget.attrs['class'] = 'datepicker'
        self.fields['data_fim_abertura'].widget.attrs['class'] = 'datepicker'
        self.fields['data_inicio_fechamento'].widget.attrs['class'] = 'datepicker'
        self.fields['data_fim_fechamento'].widget.attrs['class'] = 'datepicker'
        self.fields['fornecedor'].widget.attrs['class'] = 'select2'
        self.fields['funcionario'].widget.attrs['class'] = 'select2'
    
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all(), required=False, label=u"Funcionário")
    fornecedor = forms.ModelChoiceField(queryset=FabricanteFornecedor.objects.all(), required=False)
    mostrar_somente_abertos = forms.BooleanField(initial=True, required=False)
    mostrar_somente_fechados = forms.BooleanField(initial=False, required=False)
    mostrar_somente_atrasados = forms.BooleanField(initial=False, required=False)
    criticidade = forms.ChoiceField(choices=ORDEM_DE_COMPRA_CRITICIDADE_CHOICES_VAZIO, required=False)
    data_inicio_abertura = forms.DateField(label=u"Data Início Abertura", required=False)
    data_fim_abertura = forms.DateField(label=u"Data Fim Abertura", required=False)
    data_inicio_fechamento = forms.DateField(label=u"Data Início Fechamento", required=False)
    data_fim_fechamento = forms.DateField(label=u"Data Fim Fechamento", required=False)
    

class FormAdicionarOrdemDeCompra(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormAdicionarOrdemDeCompra, self).__init__(*args, **kwargs)
        self.fields['data_aberto'].initial  = datetime.date.today()
        self.fields['data_aberto'].widget = forms.HiddenInput()
        self.fields['valor'].localize=True
        self.fields['valor'].widget.is_localized = True
        self.fields['valor'].widget.attrs['class'] = 'nopoint'
        self.fields['fornecedor'].widget.attrs['class'] = 'select2'
        
    
    class Meta:
        model = OrdemDeCompra
        fields = ('data_aberto', 'valor', 'descricao', 'fornecedor', 'notafiscal', 'criticidade')

class FormAdicionarOrdemDeCompraFull(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormAdicionarOrdemDeCompraFull, self).__init__(*args, **kwargs)
        self.fields['data_aberto'].initial  = datetime.date.today()
        self.fields['data_aberto'].widget = forms.HiddenInput()
        self.fields['data_fechado'].widget.attrs['class'] = 'datepicker'
        self.fields['valor'].localize=True
        self.fields['valor'].widget.is_localized = True
        self.fields['valor'].widget.attrs['class'] = 'nopoint'
        self.fields['funcionario'].widget.attrs['class'] = 'select2'
        self.fields['fornecedor'].widget.attrs['class'] = 'select2'
        
    class Meta:
        model = OrdemDeCompra


class FormReagendarAtividadeDeCompra(forms.ModelForm):
    
    def clean_data(self):
        data = self.cleaned_data.get('data', None)
        if data < datetime.datetime.now():
            raise ValidationError(u"Erro. Data não pode ser menor que a data e hora atual")
        return data
    
    
    def __init__(self, *args, **kwargs):
        super(FormReagendarAtividadeDeCompra, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs['class'] = 'datetimepicker'
    
    class Meta:
        model = AtividadeDeOrdemDeCompra
        fields = 'data',
    
@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra_atividade_reagendar(request, ordem_de_compra_id, atividade_id):
    atividade = get_object_or_404(AtividadeDeOrdemDeCompra, pk=atividade_id, ordem_de_compra__pk=ordem_de_compra_id)
    # formulario
    if request.POST:
        form = FormReagendarAtividadeDeCompra(request.POST, instance=atividade)
        if form.is_valid():
            atividade = form.save()
            messages.success(request, "Sucesso! Atividade Reagendada!")
        else:
            return render_to_response('frontend/producao/producao-reagendar-atividade-ordem-producao-ajax.html', locals(), context_instance=RequestContext(request),)
    else:
        form = FormReagendarAtividadeDeCompra(instance=atividade)
        return render_to_response('frontend/producao/producao-reagendar-atividade-ordem-producao-ajax.html', locals(), context_instance=RequestContext(request),)
        
    return redirect(reverse('producao:ordem_de_compra_editar', args=[atividade.ordem_de_compra.id]))
        

class FormAddAtividadeOrdemDeCompra(forms.ModelForm):
    
    def clean_data(self):
        data = self.cleaned_data.get('data', None)
        if data < datetime.datetime.now():
            raise ValidationError(u"Erro. Data não pode ser menor que a data e hora atual")
        return data
    
    def __init__(self, *args, **kwargs):
        ordem_de_compra = kwargs.pop('ordem_de_compra')
        super(FormAddAtividadeOrdemDeCompra, self).__init__(*args, **kwargs)
        self.fields['ordem_de_compra'].initial  = ordem_de_compra
        self.fields['ordem_de_compra'].widget = forms.HiddenInput()
        self.fields['data'].widget.attrs['class'] = 'datetimepicker'

    
    class Meta:
        model = AtividadeDeOrdemDeCompra
        fields = 'data', 'descricao', 'ordem_de_compra'

class FormAddComponentesDaOrdemDeCompra(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        ordem_de_compra = kwargs.pop('ordem_de_compra')
        super(FormAddComponentesDaOrdemDeCompra, self).__init__(*args, **kwargs)
        self.fields['ordem_de_compra'].initial  = ordem_de_compra
        self.fields['ordem_de_compra'].widget = forms.HiddenInput()
        self.fields['quantidade_comprada'].widget.attrs['class'] = 'nopoint'
        self.fields['componente_comprado'].widget.attrs['class'] = 'select2'
        self.fields['valor'].widget.attrs['class'] = 'nopoint'
        self.fields['valor'].localize=True
        self.fields['valor'].widget.is_localized = True
        
        
        
    class Meta:
        model = ComponentesDaOrdemDeCompra

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra(request):
    ordens = OrdemDeCompra.objects.filter(data_fechado=None)
    if request.POST:
        if request.POST.get("form-adicionar-ordem-de-compra", None):
            form_adicionar_ordem_de_compra = FormAdicionarOrdemDeCompra(request.POST)
            if form_adicionar_ordem_de_compra.is_valid():
                ordem_de_compra = form_adicionar_ordem_de_compra.save(commit=False)
                ordem_de_compra.funcionario = request.user.funcionario
                ordem_de_compra.save()
                return redirect(reverse('producao:ordem_de_compra_editar', args=[ordem_de_compra.id]))
        if request.POST.get("form-filtrar-ordem-de-compra", None):
            filtro = True
            form_adicionar_ordem_de_compra = FormAdicionarOrdemDeCompra()
            form_filtro = FormOrdemDeCompraFiltro(request.POST)
            if form_filtro.is_valid():
                # define o filtro
                ordens = OrdemDeCompra.objects.all()
                if form_filtro.cleaned_data['data_inicio_abertura'] and form_filtro.cleaned_data['data_fim_abertura']:
                    ordens = OrdemDeCompra.objects.filter(data_aberto__range=(form_filtro.cleaned_data['data_inicio_abertura'], form_filtro.cleaned_data['data_fim_abertura'])).order_by('data_aberto')
                if form_filtro.cleaned_data['data_inicio_fechamento'] and form_filtro.cleaned_data['data_fim_fechamento']:
                    ordens = OrdemDeCompra.objects.filter(data_fechado__range=(form_filtro.cleaned_data['data_inicio_fechamento'], form_filtro.cleaned_data['data_fim_fechamento'])).order_by('data_aberto')
                
                if form_filtro.cleaned_data['mostrar_somente_atrasados']:
                    mostrar_somente_atrasados = True
                else:
                    mostrar_somente_atrasados = False
                if form_filtro.cleaned_data['mostrar_somente_abertos']:
                    ordens = ordens.filter(data_fechado=None)
                if form_filtro.cleaned_data['mostrar_somente_fechados']:
                    ordens = ordens.exclude(data_fechado=None)
                if form_filtro.cleaned_data['funcionario']:
                    ordens = ordens.filter(funcionario=form_filtro.cleaned_data['funcionario'])
                if form_filtro.cleaned_data['fornecedor']:
                    ordens = ordens.filter(fornecedor=form_filtro.cleaned_data['fornecedor'])
                if form_filtro.cleaned_data['criticidade']:
                    ordens = ordens.filter(criticidade=form_filtro.cleaned_data['criticidade'])

    else:
        form_filtro = FormOrdemDeCompraFiltro()
        form_adicionar_ordem_de_compra = FormAdicionarOrdemDeCompra()
    
    return render_to_response('frontend/producao/producao-ordem-de-compra.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra_editar(request, ordem_de_compra_id):
    ordem = get_object_or_404(OrdemDeCompra, pk=ordem_de_compra_id)
    if request.POST:
        if request.POST.get('editar-ordem', None):
            form_add_atividade = FormAddAtividadeOrdemDeCompra(ordem_de_compra=ordem)
            form_add_componentes = FormAddComponentesDaOrdemDeCompra(ordem_de_compra=ordem)
            form_editar_ordem = FormAdicionarOrdemDeCompraFull(request.POST, instance=ordem)
            if form_editar_ordem.is_valid():
                atividade = form_editar_ordem.save()
                messages.success(request, u"Ordem de Compra %s alterada" % ordem)
                return redirect(reverse('producao:ordem_de_compra_editar', args=[ordem.id]))
        if request.POST.get('adicionar-atividade', None):
            form_editar_ordem = FormAdicionarOrdemDeCompraFull(instance=ordem)
            form_add_componentes = FormAddComponentesDaOrdemDeCompra(ordem_de_compra=ordem)
            form_add_atividade = FormAddAtividadeOrdemDeCompra(request.POST, ordem_de_compra=ordem)
            if form_add_atividade.is_valid():
                atividade = form_add_atividade.save()
                messages.success(request, u"Atividade #%s Adicionada à Ordem de Compra %s" % (atividade, ordem))
                return redirect(reverse('producao:ordem_de_compra_editar', args=[ordem.id]))
        if request.POST.get('vincular_componentes', None):
            form_add_componentes = FormAddComponentesDaOrdemDeCompra(request.POST, ordem_de_compra=ordem)
            form_editar_ordem = FormAdicionarOrdemDeCompraFull(instance=ordem)
            form_add_atividade = FormAddAtividadeOrdemDeCompra(ordem_de_compra=ordem)
            if form_add_componentes.is_valid():
                vinculacao = form_add_componentes.save()
                messages.success(request, u"Componente %s com Quantidade %s vinculado à ordem de Compra %s" % (vinculacao.componente_comprado, vinculacao.quantidade_comprada, vinculacao.ordem_de_compra))
                return redirect(reverse('producao:ordem_de_compra_editar', args=[ordem.id]))
            
    else:
        form_editar_ordem = FormAdicionarOrdemDeCompraFull(instance=ordem)
        form_add_atividade = FormAddAtividadeOrdemDeCompra(ordem_de_compra=ordem)
        form_add_componentes = FormAddComponentesDaOrdemDeCompra(ordem_de_compra=ordem)
    return render_to_response('frontend/producao/producao-ordem-de-compra-editar-ordem.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra_fechar(request, ordem_de_compra_id):
    ordem = get_object_or_404(OrdemDeCompra, pk=ordem_de_compra_id)
    atividades_abertas = ordem.atividadedeordemdecompra_set.filter(data_fechado=None).count()
    if atividades_abertas:
        messages.error(request, u"Erro! Existem %s Atividades abertas nesta ordem. É preciso fechar essas atividades antes de fechar a Ordem" % atividades_abertas)
        return redirect(reverse('producao:ordem_de_compra_editar', args=[ordem.id]))
    else:
        ordem.data_fechado = datetime.datetime.now()
        ordem.save()
        messages.success(request, u"Sucesso! Ordem de Compra #%s Fechada!" % ordem.id)
        return redirect(reverse('producao:ordem_de_compra'))

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra_atividade_fechar(request, ordem_de_compra_id, atividade_id):
    atividade = get_object_or_404(AtividadeDeOrdemDeCompra, pk=atividade_id, ordem_de_compra__pk=ordem_de_compra_id)
    atividade.data_fechado = datetime.datetime.now()
    atividade.fechado_por = request.user
    atividade.save()
    messages.success(request, u"Sucesso! Atividade (%s) da Ordem de Compra #%s Fechada!" % (atividade.descricao, atividade.ordem_de_compra.id))
    return redirect(reverse('producao:ordem_de_compra_editar', args=[atividade.ordem_de_compra.id]))

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra_atividade_remover(request, ordem_de_compra_id, atividade_id):
    atividade = get_object_or_404(AtividadeDeOrdemDeCompra, pk=atividade_id, ordem_de_compra__pk=ordem_de_compra_id)
    atividade.delete()
    messages.success(request, u"Sucesso! Atividade (%s) da Ordem de Compra #%s APAGADO!" % (atividade.descricao, atividade.ordem_de_compra.id))
    return redirect(reverse('producao:ordem_de_compra_editar', args=[atividade.ordem_de_compra.id]))


@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra_componente_comprado_remover(request, ordem_de_compra_id, vinculacao_id):
    vinculo = get_object_or_404(ComponentesDaOrdemDeCompra, pk=vinculacao_id, ordem_de_compra__pk=ordem_de_compra_id)
    vinculo.delete()
    messages.success(request, u"Sucesso! Vínculação de Componente %s e Quantidade %s removido da %s" % (vinculo.componente_comprado, vinculo.quantidade_comprada, vinculo.ordem_de_compra))
    return redirect(reverse('producao:ordem_de_compra_editar', args=[vinculo.ordem_de_compra.id]))

class AddRequisicaoDeCompra(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        solicitante = kwargs.pop('solicitante')
        super(AddRequisicaoDeCompra, self).__init__(*args, **kwargs)
        self.fields['solicitante'].initial  = solicitante
        self.fields['solicitante'].widget = forms.HiddenInput()
        self.fields['solicitado'].widget.attrs['class'] = 'select2'
        self.fields['data_solicitado'].widget.attrs['class'] = 'datepicker'
    
    class Meta:
        model = RequisicaoDeCompra
        fields = 'solicitante', 'solicitado', 'data_solicitado', 'descricao', 'criticidade'

@user_passes_test(possui_perfil_acesso_producao)
def requisicao_de_compra(request):
    abertos = RequisicaoDeCompra.objects.filter(atendido=False)
    fechados = RequisicaoDeCompra.objects.filter(atendido=True).order_by('-atendido_em')
    if request.GET.get('criticidade', None):
            abertos = abertos.filter(criticidade=request.GET.get('criticidade', None))
    
    if request.POST:
        form_add_requisicao_de_compra = AddRequisicaoDeCompra(request.POST, solicitante=request.user.funcionario)
        if form_add_requisicao_de_compra.is_valid():
            requisicao_compra = form_add_requisicao_de_compra.save()
            # reinicia formulário
            form_add_requisicao_de_compra = AddRequisicaoDeCompra(solicitante=request.user.funcionario)
            messages.success(request, u"Sucesso! Requisição de Compra #%s criada." % requisicao_compra.id)
            # envia email
            template = loader.get_template('template_de_email/nova-requisicao-de-compra.html')
            d = locals()
            c = Context(d)
            content = template.render(c)
            gerentes = PerfilAcessoProducao.objects.filter(gerente=True)
            dest = []
            for gerente in gerentes:
                if gerente.user.email:
                    dest.append(gerente.user.email)
                if gerente.user.funcionario.email:
                    dest.append(gerente.user.funcionario.email)
                    
            email = EmailMessage(
                    'Requisição de Compra: #%s' % requisicao_compra.id, 
                    content,
                    'Sistema MicroERP',
                    dest,
                )
            try:
                email.send(fail_silently=False)
                messages.info(request, u"Email enviado para os gerentes.")
            except:
                messages.error(request, u"Erro! Email não enviado.")
            
            
    else:
        form_add_requisicao_de_compra = AddRequisicaoDeCompra(solicitante=request.user.funcionario)
    return render_to_response('frontend/producao/producao-requisicao-de-compra.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def requisicao_de_compra_atendido(request, requisicao_id):
    requisicao = get_object_or_404(RequisicaoDeCompra, pk=requisicao_id)
    requisicao.atendido = True
    requisicao.atendido_em = datetime.datetime.now()
    requisicao.save()
    return redirect(reverse('producao:requisicao_de_compra'))


REGISTROS_CHOICE_FIELD = (
    (100, '100'),
    (200, '200'),
    (300, '300'),
    (500, '500'),
    ('todos', 'Todos'),
)

class FormFiltraMovimento(forms.Form):
    
    inicio = forms.DateField(label=u"Início", required=False)
    fim = forms.DateField(label=u"Fim", required=False)
    funcionario = forms.ModelChoiceField(label=u"Funcionário", queryset=Funcionario.objects.all(), required=False, empty_label="Todos os Funcionários")
    registros = forms.ChoiceField(choices=REGISTROS_CHOICE_FIELD, initial=100, required=True)
    subproduto = forms.ModelChoiceField(label=u"Sub Produto", queryset=SubProduto.objects.all(), required=False, empty_label="Todos os Sub Produtos")
    produto = forms.ModelChoiceField(label=u"Produto", queryset=ProdutoFinal.objects.all(), required=False, empty_label="Todos os Produtos")
    
    def __init__(self, *args, **kwargs):
        super(FormFiltraMovimento, self).__init__(*args, **kwargs)
        self.fields['inicio'].widget.attrs.update({'class' : 'datepicker input-small'})
        self.fields['fim'].widget.attrs.update({'class' : 'datepicker input-small'})
        self.fields['funcionario'].widget.attrs['class'] = 'select2 input-small'
        self.fields['registros'].widget.attrs['class'] = 'select2 input-mini'
        self.fields['subproduto'].widget.attrs['class'] = 'select2 input-small'
        self.fields['produto'].widget.attrs['class'] = 'select2 input-small'

        
@user_passes_test(possui_perfil_acesso_producao)
def movimento_de_producao(request):
    registros_envio_de_teste = RegistroEnvioDeTesteSubProduto.objects.all()[0:100]
    registros_saida_de_teste = RegistroSaidaDeTesteSubProduto.objects.all()[0:100]
    registros_saida_de_teste = RegistroSaidaDeTesteSubProduto.objects.all()[0:100]
    movimento_estoque_subproduto = MovimentoEstoqueSubProduto.objects.filter(criado_manualmente=False)[0:100]
    movimento_estoque_produto = MovimentoEstoqueProduto.objects.filter(criado_manualmente=False)[0:100]
    ordens_conversao_subproduto = OrdemConversaoSubProduto.objects.all()[0:100]
    ordens_de_producao_produto = OrdemProducaoProduto.objects.all()[0:100]
    ordens_de_producao_subproduto = OrdemProducaoSubProduto.objects.all()[0:100]
    form_filtro_movimento = FormFiltraMovimento()
    if request.POST:
        form_filtro_movimento = FormFiltraMovimento(request.POST)
        # resgata ordens de producao subproduto por padrao
        if form_filtro_movimento.is_valid():
            inicio = form_filtro_movimento.cleaned_data['inicio']
            fim = form_filtro_movimento.cleaned_data['fim']
            # define fim como fim do dia, para acertar a busca por campos com hora
            if fim:
                fim = datetime.datetime(fim.year, fim.month, fim.day, 23, 59)
            funcionario = form_filtro_movimento.cleaned_data['funcionario']
            subproduto = form_filtro_movimento.cleaned_data['subproduto']
            produto = form_filtro_movimento.cleaned_data['produto']
            registros = form_filtro_movimento.cleaned_data['registros']
        if not request.POST.get('clear', None):
            # valores preenchidos resgatados, filtrar
            # primeiro, ordens de producao
            # somente preencheu a data de incio
            registros_envio_de_teste = RegistroEnvioDeTesteSubProduto.objects.all()
            registros_saida_de_teste = RegistroSaidaDeTesteSubProduto.objects.all()
            registros_saida_de_teste = RegistroSaidaDeTesteSubProduto.objects.all()
            movimento_estoque_subproduto = MovimentoEstoqueSubProduto.objects.filter(criado_manualmente=False)
            movimento_estoque_produto = MovimentoEstoqueProduto.objects.filter(criado_manualmente=False)
            ordens_conversao_subproduto = OrdemConversaoSubProduto.objects.all()
            ordens_de_producao_produto = OrdemProducaoProduto.objects.all()
            ordens_de_producao_subproduto = OrdemProducaoSubProduto.objects.all()            
            if inicio and not fim:
                ordens_de_producao_subproduto = ordens_de_producao_subproduto.filter(data_producao__gte=inicio)
                ordens_de_producao_produto = ordens_de_producao_produto.filter(criado__gte=inicio)
                registros_envio_de_teste = registros_envio_de_teste.filter(data_envio__gte=inicio)
                registros_saida_de_teste = registros_saida_de_teste.filter(data_envio__gte=inicio)
                movimento_estoque_subproduto = movimento_estoque_subproduto.filter(criado__gte=inicio)
                movimento_estoque_produto = movimento_estoque_produto.filter(criado__gte=inicio)
                ordens_conversao_subproduto = ordens_conversao_subproduto.filter(criado__gte=inicio)
            # somente preencheu a data de fim
            if fim and not inicio:
                ordens_de_producao_subproduto = ordens_de_producao_subproduto.filter(data_producao__lte=fim)
                ordens_de_producao_produto = ordens_de_producao_produto.filter(criado__lte=fim)
                registros_envio_de_teste = registros_envio_de_teste.filter(data_envio__lte=fim)
                registros_saida_de_teste = registros_saida_de_teste.filter(data_envio__lte=fim)
                movimento_estoque_subproduto = movimento_estoque_subproduto.filter(criado__lte=fim)
                movimento_estoque_produto = movimento_estoque_produto.filter(criado__lte=fim)
                ordens_conversao_subproduto = ordens_conversao_subproduto.filter(criado__lte=fim)
            # ambos os campos data de inicio e fim
            if fim and inicio:
                ordens_de_producao_subproduto = ordens_de_producao_subproduto.filter(data_producao__range=(inicio,fim))
                ordens_de_producao_produto = ordens_de_producao_produto.filter(criado__range=(inicio,fim))
                registros_envio_de_teste = registros_envio_de_teste.filter(data_envio__range=(inicio,fim))
                registros_saida_de_teste = registros_saida_de_teste.filter(data_envio__range=(inicio,fim))
                movimento_estoque_subproduto = movimento_estoque_subproduto.filter(criado__range=(inicio,fim))
                movimento_estoque_produto = movimento_estoque_produto.filter(criado__range=(inicio,fim))
                ordens_conversao_subproduto = ordens_conversao_subproduto.filter(criado__range=(inicio,fim))
            # filtra por funcionario
            if funcionario:
                ordens_de_producao_subproduto = ordens_de_producao_subproduto.filter(funcionario_produtor=funcionario)
                ordens_de_producao_produto = ordens_de_producao_produto.filter(criado_por=funcionario.user)
                registros_envio_de_teste = registros_envio_de_teste.filter(funcionario=funcionario)
                registros_saida_de_teste = registros_saida_de_teste.filter(funcionario=funcionario)
                movimento_estoque_subproduto = movimento_estoque_subproduto.filter(criado_por=funcionario.user)
                movimento_estoque_produto = movimento_estoque_produto.filter(criado_por=funcionario.user)
                ordens_conversao_subproduto = ordens_conversao_subproduto.filter(criado_por=funcionario.user)
            # filtra por produto
            if produto:
                movimento_estoque_produto = movimento_estoque_produto.filter(produto=produto)
                ordens_de_producao_produto = ordens_de_producao_produto.filter(produto=produto)
            if subproduto:
                ordens_de_producao_subproduto = ordens_de_producao_subproduto.filter(subproduto=subproduto)
                registros_envio_de_teste = registros_envio_de_teste.filter(subproduto=subproduto)
                registros_saida_de_teste = registros_saida_de_teste.filter(subproduto=subproduto)
                movimento_estoque_subproduto = movimento_estoque_subproduto.filter(subproduto=subproduto)
                ordens_conversao_subproduto = ordens_conversao_subproduto.filter(subproduto_original=subproduto)
            if registros != 'todos':
                ordens_de_producao_subproduto = ordens_de_producao_subproduto.all()[0:registros]
                ordens_de_producao_produto = ordens_de_producao_produto.all()[0:registros]
                registros_envio_de_teste = registros_envio_de_teste.all()[0:registros]
                registros_saida_de_teste = registros_saida_de_teste.all()[0:registros]
                movimento_estoque_subproduto = movimento_estoque_subproduto.all()[0:registros]
                movimento_estoque_produto = movimento_estoque_produto.all()[0:registros]
                ordens_conversao_subproduto = ordens_conversao_subproduto.all()[0:registros]
                
        else:
            form_filtro_movimento = FormFiltraMovimento()
    # calcula totais dos sets
    total_ordem_producao = ordens_de_producao_subproduto.aggregate(Sum('quantidade'))
    total_ordem_producao_produto = ordens_de_producao_produto.aggregate(Sum('quantidade'))
    total_ordem_producao_sub_produto = ordens_de_producao_subproduto.aggregate(Sum('quantidade'))
    total_registro_envio_de_testes = registros_envio_de_teste.aggregate(Sum('quantidade'))
    total_registro_saida_de_testes = registros_saida_de_teste.aggregate(Sum('quantidade'))
    total_movimento_estoque_subproduto = movimento_estoque_subproduto.aggregate(Sum('quantidade_movimentada'))
    total_movimento_estoque_produto = movimento_estoque_produto.aggregate(Sum('quantidade_movimentada'))
    total_ordem_conversao_subproduto = ordens_conversao_subproduto.aggregate(Sum('quantidade'))
    
    return render_to_response('frontend/producao/producao-movimento-de-producao.html', locals(), context_instance=RequestContext(request),)

class FormRemoverLancamentoProdProduto(forms.Form):
    id_lancamentos = forms.CharField(required=True, help_text="Formato: 12,34,56,67,..", label="ID Lançamentos")
    justificativa = forms.CharField(widget=forms.Textarea, required=True)

class FormFiltraLancamentosApagados(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FormFiltraLancamentosApagados, self).__init__(*args, **kwargs)
        self.fields['serial_number'].widget.attrs['class'] = 'input-medium'
        self.fields['nota_fiscal'].widget.attrs['class'] = 'input-medium'
        self.fields['cliente'].widget.attrs['class'] = 'input-small'
        self.fields['data_de_apagado_inicio'].widget.attrs['class'] = 'input-small datepicker'
        self.fields['data_de_apagado_fim'].widget.attrs['class'] = 'input-small datepicker'
        
    serial_number = forms.CharField(label="Serial Number %s" % getattr(settings, 'NOME_EMPRESA', 'Mestria'), required=False)
    nota_fiscal = forms.CharField(label="Nota Fiscal %s" % getattr(settings, 'NOME_EMPRESA', 'Mestria'), required=False)
    cliente = forms.CharField(required=False)
    data_de_apagado_inicio = forms.DateField(label=u"Apagado: Início", required=False)
    data_de_apagado_fim = forms.DateField(label=u"Apagado: Fim", required=False)
    

class FormFiltraLancamentosVendidos(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FormFiltraLancamentosVendidos, self).__init__(*args, **kwargs)
        self.fields['serial_number'].widget.attrs['class'] = 'input-medium'
        self.fields['nota_fiscal'].widget.attrs['class'] = 'input-medium'
        self.fields['cliente'].widget.attrs['class'] = 'input-small'
        self.fields['data_de_venda_inicio'].widget.attrs['class'] = 'input-small datepicker'
        self.fields['data_de_venda_fim'].widget.attrs['class'] = 'input-small datepicker'
    
    serial_number = forms.CharField(label="Serial Number %s" % getattr(settings, 'NOME_EMPRESA', 'Mestria'), required=False)
    nota_fiscal = forms.CharField(label="Nota Fiscal %s" % getattr(settings, 'NOME_EMPRESA', 'Mestria'), required=False)
    cliente = forms.CharField(required=False)
    data_de_venda_inicio = forms.DateField(label=u"Venda: Início", required=False)
    data_de_venda_fim = forms.DateField(label=u"Venda: Fim", required=False)
    
@user_passes_test(possui_perfil_acesso_producao)
def rastreabilidade_de_producao(request):
    nome_empresa = getattr(settings, 'NOME_EMPRESA', 'Mestria')
    form_remover_lancamentos = FormRemoverLancamentoProdProduto()
    # descobre os ranges para 9 meses antes
    d_atras = datetime.date.today() - relativedelta(months=9)
    inicio_range = datetime.date(d_atras.year, d_atras.month, 1)
    ultimo_dia = calendar.monthrange(datetime.date.today().year,datetime.date.today().month)[1]
    fim_range = datetime.date(datetime.date.today().year, datetime.date.today().month, ultimo_dia)
    form_filtrar_lancamentos_vendidos = FormFiltraLancamentosVendidos({'data_de_venda_inicio': inicio_range, 'data_de_venda_fim': fim_range})
    form_filtrar_lancamentos_apagados = FormFiltraLancamentosApagados({'data_de_apagado_inicio': inicio_range, 'data_de_apagado_fim': fim_range})
    if request.POST.get('apagar-lancamentos-btn', None):
        form_remover_lancamentos = FormRemoverLancamentoProdProduto(request.POST)
        if form_remover_lancamentos.is_valid():
            ids = form_remover_lancamentos.cleaned_data['id_lancamentos'].split(",")
            for id_lancamento in ids:
                if id_lancamento.isdigit():
                    try:
                        lancamento = LancamentoProdProduto.objects.get(pk=int(id_lancamento))
                        lancamento.apagado = True
                        lancamento.justificativa_apagado = form_remover_lancamentos.cleaned_data['justificativa']
                        lancamento.funcionario_apagou = request.user.funcionario
                        lancamento.data_apagado = datetime.datetime.now()
                        lancamento.save()
                        messages.success(request, u'Lançamento #%s Marcado como REMOVIDO.' % id_lancamento)
                    except LancamentoProdProduto.DoesNotExist:
                        messages.warning(request, u'Lançamento #%s não encontrado.' % id_lancamento)
                else:
                    messages.warning(request, u'Lançamento #%s não encontrado.' % id_lancamento)
                    

                
        
    produtos_ativos = ProdutoFinal.objects.filter(ativo=True)
    nao_apagados = LancamentoProdProduto.objects.filter(apagado=False)
    lancamentos_associar = nao_apagados.filter(vendido=False, serial_number=None).order_by('produto__part_number', '-criado')
    lancamentos_associar_valores = lancamentos_associar.values(
        'id',
        'adicionado_manualmente',
        'funcionario_adicionou__nome',
        'criado',
        'justificativa_adicionado',
        'ordem_de_producao__id',
        'produto__id',
        'produto__part_number',
        'produto__nome',

        'linhatestelancamentoprodproduto__lancamento_de_producao__id'
        ).annotate(
            Count('linhatestelancamentoprodproduto__lancamento_de_producao__id')
        )
    lancamentos_disponiveis = LancamentoProdProduto.objects.filter(apagado=False, vendido=False).exclude(serial_number=None).order_by('produto__part_number', 'serial_number')
    lancamentos_disponiveis_valores = lancamentos_disponiveis.values(
        'id',
        'adicionado_manualmente',
        'funcionario_adicionou__nome',
        'criado',
        'justificativa_adicionado',
        'ordem_de_producao__id',
        'produto__id',
        'produto__part_number',
        'produto__nome',
        'serial_number',
        )
    lancamentos_vendidos = nao_apagados.filter(vendido=True)
    # filtra os vendidos
    if request.POST and request.POST.get('filtra-lancamentos-vendidos-btn', None):
        form_filtrar_lancamentos_vendidos = form_filtrar_lancamentos_vendidos = FormFiltraLancamentosVendidos(request.POST)
        if form_filtrar_lancamentos_vendidos.is_valid():
            vendidos_filtro = True
            serial_number_q = form_filtrar_lancamentos_vendidos.cleaned_data['serial_number']
            cliente_q = form_filtrar_lancamentos_vendidos.cleaned_data['cliente']
            nota_fiscal_q = form_filtrar_lancamentos_vendidos.cleaned_data['nota_fiscal']
            data_de_venda_inicio = form_filtrar_lancamentos_vendidos.cleaned_data['data_de_venda_inicio']
            data_de_venda_fim = form_filtrar_lancamentos_vendidos.cleaned_data['data_de_venda_fim']

            lancamentos_vendidos = LancamentoProdProduto.objects.filter(apagado=False, vendido=True)            
            if serial_number_q:
                lancamentos_vendidos = lancamentos_vendidos.filter(serial_number__icontains=serial_number_q)
            if cliente_q:
                lancamentos_vendidos = lancamentos_vendidos.filter(cliente_associado__icontains=cliente_q)
            if nota_fiscal_q:
                lancamentos_vendidos = lancamentos_vendidos.filter(nota_fiscal__notafiscal__icontains=nota_fiscal_q)
            if data_de_venda_inicio and data_de_venda_fim:
                lancamentos_vendidos = lancamentos_vendidos.filter(data_vendido__range=(data_de_venda_inicio, data_de_venda_fim))
    else:
        lancamentos_vendidos = lancamentos_vendidos.filter(data_vendido__range=(inicio_range, fim_range))

    lancamentos_vendidos_valores = lancamentos_vendidos.values(
    'id',
    'data_vendido',
    'funcionario_vendeu__nome',
    'criado',
    'cliente_associado',
    'ordem_de_producao__id',
    'produto__id',
    'produto__part_number',
    'produto__nome',
    'serial_number',
    'justificativa_adicionado',
    'observacoes',
    'nota_fiscal__notafiscal',
    ).order_by('produto__part_number', '-data_vendido')
    # apagados
    
    lancamentos_apagados = LancamentoProdProduto.objects.filter(apagado=True)
    if request.POST and request.POST.get('filtra-lancamentos-apagados-btn', None):
        form_filtrar_lancamentos_apagados = FormFiltraLancamentosApagados(request.POST)
        if form_filtrar_lancamentos_apagados.is_valid():
            apagados_filtro = True
            serial_number_q = form_filtrar_lancamentos_apagados.cleaned_data['serial_number']
            cliente_q = form_filtrar_lancamentos_apagados.cleaned_data['cliente']
            nota_fiscal_q = form_filtrar_lancamentos_apagados.cleaned_data['nota_fiscal']
            data_de_apagado_inicio = form_filtrar_lancamentos_apagados.cleaned_data['data_de_apagado_inicio']
            data_de_apagado_fim = form_filtrar_lancamentos_apagados.cleaned_data['data_de_apagado_fim']
            # filtra
            if serial_number_q:
                lancamentos_apagados = lancamentos_apagados.filter(serial_number__icontains=serial_number_q)
            if cliente_q:
                lancamentos_apagados = lancamentos_apagados.filter(cliente_associado__icontains=cliente_q)
            if nota_fiscal_q:
                lancamentos_apagados = lancamentos_apagados.filter(nota_fiscal__notafiscal__icontains=nota_fiscal_q)
            if data_de_apagado_inicio and data_de_apagado_fim:
                lancamentos_apagados = lancamentos_apagados.filter(data_apagado__range=(data_de_apagado_inicio, data_de_apagado_fim))

    else:
        lancamentos_apagados = lancamentos_apagados.filter(data_apagado__range=(inicio_range, fim_range))
        

    lancamentos_apagados_valores = lancamentos_apagados.values(
        'id',
        'serial_number',
        'funcionario_vendeu__nome',
        'data_vendido',
        'funcionario_apagou__nome',
        'data_apagado',
        'criado',
        'justificativa_apagado',
        'cliente_associado',
        'ordem_de_producao__id',
        'produto__id',
        'produto__part_number',
        'produto__nome',
        'nota_fiscal__notafiscal',   
        'observacoes',     
        ).order_by('produto__part_number', '-data_apagado')
    return render_to_response('frontend/producao/producao-rastreabilidade-de-producao.html', locals(), context_instance=RequestContext(request),)

class FormConfigurarSubProdutosTestaveisDoProduto(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormConfigurarSubProdutosTestaveisDoProduto, self).__init__(*args, **kwargs)
        self.fields['subprodutos_testaveis'].widget.attrs['class'] = 'select2'
        self.fields['subprodutos_testaveis'].help_text = None
        self.fields['subprodutos_testaveis'].label = u"Sub Produtos Testáveis"
        if self.instance:
            # filtra somente os que participam do subproduto
            subprodutos = self.instance.linhasubprodutodoproduto_set.all()
            subprodutos = [(s.id, "%s - %s" % (s.subproduto.part_number, s.subproduto.nome)) for s in subprodutos]
            self.fields['subprodutos_testaveis'].choices = subprodutos
    
    class Meta:
        model = ProdutoFinal
        fields = 'subprodutos_testaveis',
        
@user_passes_test(possui_perfil_acesso_producao)
def rastreabilidade_de_producao_configurar(request, produto_id):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    if request.POST:
        form_configurar = FormConfigurarSubProdutosTestaveisDoProduto(request.POST, instance=produto)
        if form_configurar.is_valid():
            produto = form_configurar.save()
            messages.success(request, u"Produto %s Configurado" % produto)
            return redirect(reverse("producao:rastreabilidade_de_producao") + "#configurar")
    else:
        form_configurar = FormConfigurarSubProdutosTestaveisDoProduto(instance=produto)
    return render_to_response('frontend/producao/producao-rastreabilidade-de-producao-configurar.html', locals(), context_instance=RequestContext(request),)


class FormAssociarLancamentoProdProduto(forms.ModelForm):
    
    required_css_class = 'required'
    
    def __init__(self, *args, **kwargs):
        super(FormAssociarLancamentoProdProduto, self).__init__(*args, **kwargs)
        self.fields['funcionario_que_montou'].widget.attrs['class'] = 'select2'
        self.fields['funcionario_inicio_teste'].widget.attrs['class'] = 'select2'
        self.fields['funcionario_relalizou_teste'].widget.attrs['class'] = 'select2'
        self.fields['funcionario_finalizou_teste'].widget.attrs['class'] = 'select2'
        self.fields['funcionario_finalizou_teste'].required = True
        self.fields['data_montagem'].widget.attrs.update({'class' : 'datepicker'})
        self.fields['data_montagem'].required = True
        self.fields['inicio_teste'].widget.attrs.update({'class' : 'datepicker'})
        self.fields['inicio_teste'].label = u"Data de Início"
        self.fields['realizacao_procedimento_de_teste'].widget.attrs.update({'class' : 'datepicker'})
        self.fields['realizacao_procedimento_de_teste'].label = u"Data de Realização"
        self.fields['fim_teste'].widget.attrs.update({'class' : 'datepicker'})
        self.fields['fim_teste'].required = True
        self.fields['fim_teste'].label = u"Data de Término"
        self.fields['serial_number'].required = True
        self.fields['serial_number'].label = "Serial Number %s" % getattr(settings, 'NOME_EMPRESA', 'Mestria')
        self.fields['funcionario_que_montou'].required = True
        self.fields['funcionario_inicio_teste'].required = True
        self.fields['inicio_teste'].required = True
        self.fields['funcionario_relalizou_teste'].required = True
        self.fields['realizacao_procedimento_de_teste'].required = True
        if self.instance.vendido or self.instance.serial_number:
            self.fields['serial_number'].widget = forms.HiddenInput()
            self.fields['serial_number'].initial = self.instance.serial_number
    
    def clean_serial_number(self):
        serial_number = self.cleaned_data['serial_number']
        if LancamentoProdProduto.objects.filter(serial_number=serial_number).exclude(id=self.instance.id).exists():
            raise ValidationError(u'Erro! Serial Number Já existe!')
        return serial_number
        
    class Meta:
        model = LancamentoProdProduto
        fields = 'serial_number', 'funcionario_que_montou', 'data_montagem', 'funcionario_inicio_teste', 'inicio_teste', 'funcionario_relalizou_teste', 'realizacao_procedimento_de_teste', 'funcionario_finalizou_teste', 'fim_teste', 'observacoes'
            

class FormLinhaTesteLancamentoProdProduto(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormLinhaTesteLancamentoProdProduto, self).__init__(*args, **kwargs)
        self.fields['funcionario_que_montou'].widget.attrs.update({'class' : 'herda_montou select2'})
        self.fields['funcionario_que_testou'].widget.attrs.update({'class' : 'herda_testou select2'})
        self.fields['funcionario_que_testou'].required=True
        self.fields['funcionario_que_montou'].required=True
        self.fields['versao_firmware'].required=True
        self.fields['versao_firmware'].widget.attrs.update({'class' : 'input-mini'})
    
    class Meta:
        model = LinhaTesteLancamentoProdProduto
        fields = 'funcionario_que_montou', 'funcionario_que_testou', 'versao_firmware'
            
@user_passes_test(possui_perfil_acesso_producao)
def rastreabilidade_de_producao_associar_lancamento(request, lancamento_id):
    lancamento = get_object_or_404(LancamentoProdProduto, pk=lancamento_id)
    lancamento_associa_form = FormAssociarLancamentoProdProduto(instance=lancamento)
    LancamentoFormSet = forms.models.inlineformset_factory(LancamentoProdProduto, LinhaTesteLancamentoProdProduto, extra=0, can_delete=False, form=FormLinhaTesteLancamentoProdProduto)
    testes_de_lancamento_form = LancamentoFormSet(instance=lancamento)
    if request.POST:
        lancamento_associa_form = FormAssociarLancamentoProdProduto(request.POST, instance=lancamento)
        testes_de_lancamento_form = LancamentoFormSet(request.POST, instance=lancamento)
        if lancamento_associa_form.is_valid() and testes_de_lancamento_form.is_valid():
            lancamento = lancamento_associa_form.save()
            testes = testes_de_lancamento_form.save()
            messages.success(request, u"Sucesso! Lançamento de Produção #%s Associado a Serial %s" % (lancamento.id, lancamento.serial_number))
            return redirect(reverse("producao:rastreabilidade_de_producao"))
        else:
            messages.error(request, u"Erro! Formulário Inválido.")

    return render_to_response('frontend/producao/producao-rastreabilidade-de-producao-associar.html', locals(), context_instance=RequestContext(request),)
    
class FormAdicionarLancamentoProdProduto(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormAdicionarLancamentoProdProduto, self).__init__(*args, **kwargs)
        self.fields['produto'].widget.attrs['class'] = 'select2'
        self.fields['produto'].queryset = ProdutoFinal.objects.filter(ativo=True)
        self.fields['justificativa_adicionado'].label = u"Justificativa para a adição"
        self.fields['justificativa_adicionado'].required = True

    class Meta:
        model = LancamentoProdProduto
        fields = 'produto', 'justificativa_adicionado'
        
@user_passes_test(possui_perfil_acesso_producao)
def rastreabilidade_de_producao_adicionar(request):
    if request.POST:
        form_adicionar_lancamento = FormAdicionarLancamentoProdProduto(request.POST)
        if form_adicionar_lancamento.is_valid():
            lancamento = form_adicionar_lancamento.save()
            lancamento.funcionario_adicionou = request.user.funcionario
            lancamento.save()
            messages.success(request, u"Lançamento #%s adicionado com sucesso!" % lancamento.id)
            # lancando linhas de teste de subprodutos
            # para cada subproduto testável deste produto, criar uma linha de testes
            for subproduto_testavel in lancamento.produto.subprodutos_testaveis.all():
                linha = LinhaTesteLancamentoProdProduto.objects.create(
                    lancamento_de_producao=lancamento,
                    subproduto_testavel=subproduto_testavel
                )
                messages.info(request, u"Linha de Teste #%s do Lançamento #%s (%s) criado para Sub Produto %s " % (linha.id, lancamento.id, lancamento.produto.part_number, linha.subproduto_testavel))
            
            return redirect(reverse("producao:rastreabilidade_de_producao"))
    else:
        form_adicionar_lancamento = FormAdicionarLancamentoProdProduto()
    return render_to_response('frontend/producao/producao-rastreabilidade-de-producao-adicionar.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def rastreabilidade_de_producao_checar_quantitativos(request):
    tabela_produtos = []
    for produto in ProdutoFinal.objects.filter(ativo=True):
        #lancamentos = LancamentoProdProduto.objects.filter(produto=produto, vendido=False, apagado=False)
        lancamentos = produto.lancamentoprodproduto_set.filter(vendido=False, apagado=False).exclude(serial_number=None).exclude(serial_number='')
        tabela_produtos.append((produto, lancamentos.count()))
    return render_to_response('frontend/producao/producao-rastreabilidade-de-producao-checar-quantitativos.html', locals(), context_instance=RequestContext(request),)


class FormFiltrarFalhas(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FormFiltrarFalhas, self).__init__(*args, **kwargs)
        self.fields['subproduto'].widget.attrs['class'] = 'select2'
        self.fields['funcionario'].widget.attrs['class'] = 'select2'
        self.fields['inicio'].widget.attrs['class'] = 'datepicker input-small'
        self.fields['fim'].widget.attrs['class'] = 'datepicker input-small'
    
    inicio = forms.DateField(label=u"Início", required=True)
    fim = forms.DateField(label=u"Fim", required=True)
    subproduto = forms.ModelChoiceField(queryset=SubProduto.objects.filter(ativo=True, tipo_de_teste=2), empty_label='Todos os Sub Produtos Compostos', required=False, label="Sub Produto Compostos")
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all(), empty_label='Todos os Funcionários', required=False, label=u"Funcionário Testador")

@user_passes_test(possui_perfil_acesso_producao)
def controle_de_testes_producao(request):
    # inicio e fim dos lancamentos
    try:
        inicio_lancamentos = LancamentoDeFalhaDeTeste.objects.all().order_by('criado')[0].criado
        fim_lancamentos = LancamentoDeFalhaDeTeste.objects.all().order_by('-criado')[0].criado
    except:
        inicio_lancamentos = None
        fim_lancamentos = None
    if inicio_lancamentos:
        form_initial = {'inicio': inicio_lancamentos, 'fim': fim_lancamentos}
    else:
        form_initial = None
    form_filtrar_falha = FormFiltrarFalhas(form_initial)
    lancamentos_falha = LancamentoDeFalhaDeTeste.objects.all()[0:200]
    testes_perda = FalhaDeTeste.objects.filter(tipo='perda')
    testes_reparo = FalhaDeTeste.objects.filter(tipo='reparo')
    # filtra falhas por subproduto
    if request.POST.get('filtrar-indicadores-btn', None):
        form_filtrar_falha = FormFiltrarFalhas(request.POST)
        if form_filtrar_falha.is_valid():
            filtro = True
            inicio = form_filtrar_falha.cleaned_data['inicio']
            fim = form_filtrar_falha.cleaned_data['fim']
            subprodutos_analisar = form_filtrar_falha.cleaned_data['subproduto']
            funcionario = form_filtrar_falha.cleaned_data['funcionario']
            lista_dicionario_retorno = []
            if subprodutos_analisar:
                # escolhido somente um subproduto. loop único
                subprodutos = [subprodutos_analisar]
            else:
                # escolhido todos os subprodutos. loop somente nos ativos e compostos
                subprodutos = SubProduto.objects.filter(ativo=True, tipo_de_teste=2)
            for subproduto in subprodutos:
                falhas = LinhaLancamentoFalhaDeTeste.objects.all()
                lancamentos = LancamentoDeFalhaDeTeste.objects.all()
                if subproduto.lancamentodefalhadeteste_set.count():
                    if inicio and fim:
                        falhas = falhas.filter(
                            lancamento_teste__data_lancamento__range=(inicio,fim)
                        )
                        lancamentos = lancamentos.filter(
                            data_lancamento__range=(inicio,fim)
                        )
                    if subproduto:
                        falhas = falhas.filter(
                            lancamento_teste__subproduto=subproduto
                        )
                        lancamentos = lancamentos.filter(
                            subproduto=subproduto
                        )
                    if funcionario:
                        falhas = falhas.filter(
                            lancamento_teste__funcionario_testador=funcionario
                        )
                        lancamentos = lancamentos.filter(
                            funcionario_testador=funcionario
                        )
                    if lancamentos:
                        total_por_falha_perda = falhas.filter(falha__tipo='perda').values('falha__codigo', 'falha__descricao').order_by('falha__codigo').annotate(total=Sum('quantidade'))
                        total_por_falha_reparo = falhas.filter(falha__tipo='reparo').values('falha__codigo', 'falha__descricao').order_by('falha__codigo').annotate(total=Sum('quantidade'))
                        # total por tipo de falha
                        total_por_tipo_perda = falhas.filter(falha__tipo='perda').aggregate(total=Sum('quantidade'))
                        total_por_tipo_reparo = falhas.filter(falha__tipo='reparo').aggregate(total=Sum('quantidade'))
                        # total funcional direto do lancamento
                        total_testado = lancamentos.aggregate(total=Sum('quantidade_total_testada'))
                        total_funcional_direto = lancamentos.aggregate(total=Sum('quantidade_funcional_direta'))
                        total_funcional_reparado = lancamentos.aggregate(total=Sum('quantidade_reparada_funcional'))
                        # total funcional (funcional direto + reparados)
                        total_geral_funcional = total_funcional_direto['total'] + total_funcional_reparado['total']
                        # indicadores
                        if total_testado['total']:

                            if total_geral_funcional:
                                indicador_funcional_geral = total_geral_funcional / float(total_testado['total']) * 100
                            else:
                                indicador_funcional_geral = 0

                            if total_funcional_direto['total']:
                                indicador_funcional_direto = total_funcional_direto['total'] / float(total_geral_funcional)  * 100
                            else:
                                indicador_funcional_direto = 0

                            if total_por_tipo_perda['total']:
                                indicador_perda = total_por_tipo_perda['total']  / float(total_testado['total']) * 100
                            else:
                                indicador_perda = 0

                            if total_por_tipo_reparo['total']:
                                indicador_reparo = total_por_tipo_reparo['total'] / float(total_geral_funcional) * 100
                            else:
                                indicador_reparo = 0
                            
                            dicionario = {
                                    'subproduto': subproduto,
                                    'total_testado': total_testado,
                                    'total_funcional_direto': total_funcional_direto,
                                    'total_geral_funcional': total_geral_funcional,
                                    'indicador_funcional_geral': indicador_funcional_geral,
                                    'indicador_funcional_direto': indicador_funcional_direto,
                                    'total_por_falha_perda': total_por_falha_perda,
                                    'total_por_falha_reparo': total_por_falha_reparo,
                                    'total_por_tipo_perda': total_por_tipo_perda,
                                    'indicador_perda': indicador_perda,
                                    'total_por_tipo_reparo': total_por_tipo_reparo,
                                    'indicador_reparo': indicador_reparo,
                                }
                        lista_dicionario_retorno.append(dicionario)
    return render_to_response('frontend/producao/producao-controle-de-testes-producao.html', locals(), context_instance=RequestContext(request),)

class FormLancaFalhaDeTeste(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FormLancaFalhaDeTeste, self).__init__(*args, **kwargs)
        self.fields['subproduto'].widget.attrs['class'] = 'select2'
        self.fields['subproduto'].queryset = SubProduto.objects.filter(tipo_de_teste=2)
        self.fields['funcionario_testador'].widget.attrs['class'] = 'select2'
        self.fields['data_lancamento'].widget.attrs['class'] = 'datepicker'
        self.fields['quantidade_perdida'].widget = forms.HiddenInput()
        self.fields['quantidade_funcional_direta'].widget = forms.HiddenInput()
        self.fields['quantidade_total_testada'].required = True
    
    def clean(self):
        cleaned_data = self.cleaned_data
        quantidade_total_testada = cleaned_data.get('quantidade_total_testada')
        quantidade_funcional_direta = cleaned_data.get('quantidade_funcional_direta')
        quantidade_funcional = cleaned_data.get('quantidade_funcional')
        quantidade_perdida = cleaned_data.get('quantidade_perdida')
        quantidade_reparada_funcional = cleaned_data.get('quantidade_reparada_funcional')
        
        if quantidade_total_testada == 0:
            self._errors["quantidade_total_testada"] = self.error_class(['Não é possível Lançar 0 testes ;)'])
        if quantidade_total_testada < 0:
            self._errors["quantidade_total_testada"] = self.error_class(['Não pode ser MENOR que 0'])
        if quantidade_funcional < 0:
            self._errors["quantidade_funcional"] = self.error_class(['Não pode ser MENOR que 0'])
        if quantidade_funcional > quantidade_total_testada:
            self._errors["quantidade_funcional"] = self.error_class(['Não pode ser MAIOR do que Quantidade Total Testada (%s)' % quantidade_total_testada])
        if quantidade_perdida < 0:
            self._errors["quantidade_perdida"] = self.error_class(['Não pode ser MENOR que 0'])
        if quantidade_reparada_funcional < 0:
            self._errors["quantidade_reparada_funcional"] = self.error_class(['Não pode ser MENOR que 0'])
        if quantidade_reparada_funcional > quantidade_funcional:
            self._errors["quantidade_reparada_funcional"] = self.error_class(['Não pode ser MAIOR que Quantidade Funcional (%s)' % quantidade_funcional])
        if quantidade_funcional_direta < 0:
            self._errors["quantidade_funcional_direta"] = self.error_class(['Não pode ser MENOR que 0'])
        return cleaned_data


    class Meta:
        model = LancamentoDeFalhaDeTeste
 
class LinhaLancamentoFalhaDeTesteFormReparo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LinhaLancamentoFalhaDeTesteFormReparo, self).__init__(*args, **kwargs)
        self.fields['quantidade'].required=True
        self.fields['quantidade'].widget.attrs['class'] = 'input-mini checa_quantidade_reparo'
        self.fields['falha'].required = True
        self.fields['falha'].widget.attrs['class'] = 'select2'
        self.fields['falha'].queryset = FalhaDeTeste.objects.filter(tipo="reparo")
    
    class Meta:
        model = LinhaLancamentoFalhaDeTeste

class LinhaLancamentoFalhaDeTesteFormPerda(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LinhaLancamentoFalhaDeTesteFormPerda, self).__init__(*args, **kwargs)
        self.fields['quantidade'].required=True
        self.fields['quantidade'].widget.attrs['class'] = 'input-mini checa_quantidade_perda'
        self.fields['falha'].widget.attrs['class'] = 'select2'
        self.fields['falha'].queryset = FalhaDeTeste.objects.filter(tipo="perda")
        self.fields['falha'].required = True

    class Meta:
        model = LinhaLancamentoFalhaDeTeste

@user_passes_test(possui_perfil_acesso_producao)
def controle_de_testes_producao_lancar_falha(request):
    '''Lança falhas e seus quantitativos, totais funcionais, etc'''
    lancamento_teste_form = FormLancaFalhaDeTeste()
    LancamentoFormSetReparo = forms.models.inlineformset_factory(LancamentoDeFalhaDeTeste, LinhaLancamentoFalhaDeTeste, extra=1, can_delete=False, form=LinhaLancamentoFalhaDeTesteFormReparo)
    LancamentoFormSetPerda = forms.models.inlineformset_factory(LancamentoDeFalhaDeTeste, LinhaLancamentoFalhaDeTeste, extra=1, can_delete=False, form=LinhaLancamentoFalhaDeTesteFormPerda)
    lancamentos_falhas_reparo_form = LancamentoFormSetReparo(prefix="reparo")
    lancamentos_falhas_perda_form = LancamentoFormSetPerda(prefix="perda")
    if request.POST:
        if 'adicionar_falha_reparo' in request.POST:
            cp = request.POST.copy()
            cp['reparo-TOTAL_FORMS'] = int(cp['reparo-TOTAL_FORMS'])+ 1
            lancamentos_falhas_reparo_form = LancamentoFormSetReparo(cp,prefix='reparo')
            lancamentos_falhas_perda_form = LancamentoFormSetPerda(cp, prefix="perda")
            lancamento_teste_form = FormLancaFalhaDeTeste(cp)
        elif 'adicionar_falha_perda' in request.POST:
            cp = request.POST.copy()
            cp['perda-TOTAL_FORMS'] = int(cp['perda-TOTAL_FORMS'])+ 1
            lancamentos_falhas_reparo_form = LancamentoFormSetReparo(cp,prefix='reparo')
            lancamentos_falhas_perda_form = LancamentoFormSetPerda(cp, prefix="perda")
            lancamento_teste_form = FormLancaFalhaDeTeste(cp)
        elif 'lancar_testes' in request.POST:
            lancamento_teste_form = FormLancaFalhaDeTeste(request.POST)
            lancamentos_falhas_reparo_form = LancamentoFormSetReparo(request.POST, prefix='reparo')
            lancamentos_falhas_perda_form = LancamentoFormSetPerda(request.POST, prefix='perda')
            if lancamento_teste_form.is_valid() and lancamentos_falhas_reparo_form.is_valid() and lancamentos_falhas_perda_form.is_valid():
                lancamento_teste = lancamento_teste_form.save(commit=False)
                lancamento_teste.criado_por = request.user
                lancamento_teste_form.save()
                messages.success(request, u"Informações do Teste Registrado com Sucesso!")
                if lancamentos_falhas_reparo_form.is_valid():
                    try:
                        for form in lancamentos_falhas_reparo_form: 
                            falha = form.save(commit=False)
                            falha.lancamento_teste = lancamento_teste
                            if falha.quantidade and falha.falha:
                                falha.save()
                        messages.info(request, u"Informações de Falha de Reparo Registrado com Sucesso!")
                    except:
                        messages.error(request, u"Erro ao Salvar as falhas de reparo.")
                        raise
                if lancamentos_falhas_perda_form.is_valid():
                    try:
                        for form in lancamentos_falhas_perda_form: 
                            falha = form.save(commit=False)
                            falha.lancamento_teste = lancamento_teste
                            if falha.quantidade and falha.falha:
                                falha.save()
                        messages.info(request, u"Informações de Falha de Perda Registrado com Sucesso!")
                    except:
                        messages.error(request, u"Erro ao Salvar as falhas de perda.")
                        raise
                
                
                return redirect(reverse("producao:controle_de_testes_producao"))
    return render_to_response('frontend/producao/producao-controle-de-testes-lancar-falha.html', locals(), context_instance=RequestContext(request),)

class FormAdicionaFalhaDeTeste(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        tipo = kwargs.pop('tipo', None)
        super(FormAdicionaFalhaDeTeste, self).__init__(*args, **kwargs)
        self.fields['descricao'].required = True
        self.fields['tipo'].initial = tipo
    
    class Meta:
        model = FalhaDeTeste
        fields = 'tipo', 'codigo', 'descricao'

@user_passes_test(possui_perfil_acesso_producao)
def controle_de_testes_producao_adicionar_falha(request):
    '''Adiciona item à tabela de testes, com código, etc'''
    form_adiciona_falha = FormAdicionaFalhaDeTeste(tipo=request.GET.get('tipo', 'perda'))
    if request.POST:
        form_adiciona_falha = FormAdicionaFalhaDeTeste(request.POST)
        if form_adiciona_falha.is_valid():
            falha = form_adiciona_falha.save()
            falha.criado_por = request.user
            messages.success(request, u"Sucesso! Falha adicionada.")
            return redirect(reverse('producao:controle_de_testes_producao')+ "#falha-tipo-%s" % falha.tipo)
    return render_to_response('frontend/producao/producao-controle-de-testes-adicionar-falha.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def registrar_nota_fiscal_emitida(request):
    notas_registradas = NotaFiscalLancamentosProducao.objects.all()
    nome_empresa = getattr(settings, 'NOME_EMPRESA', 'Mestria')
    lancamentos_de_producao_values = LancamentoProdProduto.objects.values(
        'nota_fiscal__notafiscal',
        'nota_fiscal__data_saida',
        'nota_fiscal__cliente_associado',
        'serial_number',
        'produto__part_number',
        'produto__nome',
    ).order_by('-nota_fiscal__notafiscal')

    return render_to_response('frontend/producao/producao-registrar-nota-fiscal-emitida.html', locals(), context_instance=RequestContext(request),)

class FormAdicionarNotaFiscalLancamentosProducao(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        lancamentos_selecionados = kwargs.pop('lancamentos_selecionados', None)
        super(FormAdicionarNotaFiscalLancamentosProducao, self).__init__(*args, **kwargs)
        self.fields['lancamentos_de_producao'].queryset = LancamentoProdProduto.objects.filter(vendido=False, apagado=False).exclude(serial_number=None)
        self.fields['lancamentos_de_producao'].widget.attrs['class'] = 'select2'
        self.fields['data_saida'].widget.attrs['class'] = 'datepicker'
        self.fields['cliente_associado'].widget.attrs['class'] = 'input-xlarge'
        self.fields['criado_por'].widget = forms.HiddenInput()
        if lancamentos_selecionados:
            self.fields['lancamentos_de_producao'].initial = lancamentos_selecionados
    
    class Meta:
        model = NotaFiscalLancamentosProducao

@user_passes_test(possui_perfil_acesso_producao)
def registrar_nota_fiscal_emitida_adicionar(request):
    nome_empresa = getattr(settings, 'NOME_EMPRESA', 'Mestria')
    nao_apagados = LancamentoProdProduto.objects.filter(apagado=False)
    lancamentos_disponiveis = nao_apagados.filter(vendido=False).exclude(serial_number=None).order_by('produto__part_number')
    lancamentos_disponiveis_valores = lancamentos_disponiveis.values(
        'id',
        'adicionado_manualmente',
        'funcionario_adicionou__nome',
        'criado',
        'justificativa_adicionado',
        'ordem_de_producao__id',
        'produto__id',
        'produto__part_number',
        'produto__nome',
        'serial_number'
        )
    if request.GET:
        # possui lancamentos selecionados
        lancamentos_selecionados = request.GET.getlist('lancamento', None)
        produtos_quantidades = LancamentoProdProduto.objects.filter(id__in=lancamentos_selecionados).values('produto__id').annotate(Count("produto__id"))
        # para cada produto, conferir
        estoques_consistentes = True
        quantidades_possiveis = True
        for produto_referencia in produtos_quantidades:
            # conferir se estoque está consistente
            produto = ProdutoFinal.objects.get(pk=produto_referencia['produto__id'])
            if produto.total_produzido == produto.lancamentos_disponiveis_venda().count():
                if  produto_referencia['produto__id__count'] > produto.total_produzido:
                    quantidades_possiveis = False
                    messages.error(request, u"Erro! Quantidades Impossíveis para Produto %s: Total Produzido: %s, Disponível para venda: %s, Quantidade Solicitada de Venda: %s" % \
                        (produto, produto.total_produzido, produto.lancamentos_disponiveis_venda().count(), produto_referencia['produto__id__count']))
            else:
                estoques_consistentes = False
                messages.error(
                        request, u"Erro! Estoque inconsistente para Produto %s: Total Produzido: %s, Disponível para venda: %s" % \
                        (produto, produto.total_produzido, produto.lancamentos_disponiveis_venda().count())
                    )
        form_adiciona_nota = FormAdicionarNotaFiscalLancamentosProducao(lancamentos_selecionados=lancamentos_selecionados)
        if estoques_consistentes and quantidades_possiveis:
            checagem = 'ok'
            messages.success(request, u"Sucesso! Checagens de estoque e quantidades estão consistentes!")
    if request.POST:
        form_adiciona_nota = FormAdicionarNotaFiscalLancamentosProducao(request.POST, lancamentos_selecionados=lancamentos_selecionados)
        if form_adiciona_nota.is_valid():
            lancamentos_vendidos_obj = form_adiciona_nota.cleaned_data['lancamentos_de_producao']
            # assume estoque OK
            estoque_consistente = True
            # monta o dicionario com valores por produto
            produtos_vendidos = {}
            for lancamento in lancamentos_vendidos_obj:
                try:
                    produtos_vendidos[lancamento.produto.id] += 1
                except:
                    produtos_vendidos[lancamento.produto.id] = 1
            # monta lista de produtos
            produtos_vendidos_obj = ProdutoFinal.objects.filter(id__in=produtos_vendidos.keys())
            # confere se todos os produtos vendidos possuem total_produzido maior que quantidade
            for produto in produtos_vendidos_obj:
                if produtos_vendidos[produto.id] > produto.total_produzido:
                    messages.error(request, u"Impossível continuar: Produto %s possui somente %s Produzidos" % (produto, produto.total_produzido))
                    estoque_consistente = False
                if produto.total_produzido != produto.lancamentos_disponiveis_venda().count():
                    messages.error(request, u"Impossível continuar: Estoque Incosistente para produto %s" % produto)
                    estoque_consistente = False
            # feitas as checagens,
            # registrar o lancamento
            if estoque_consistente:
                registro = form_adiciona_nota.save(commit=False)
                registro.criado_por = request.user
                registro.save()
                registro.lancamentos_de_producao = lancamentos_vendidos_obj
                registro.save()
                messages.success(request, u"Sucesso! Nota %s Registrada!" % registro.notafiscal)
                # atualiza os lancamentos
                for lancamento in lancamentos_vendidos_obj:
                    lancamento.vendido=True
                    lancamento.data_vendido=datetime.datetime.now()
                    lancamento.funcionario_vendeu=request.user.funcionario
                    lancamento.cliente_associado=registro.cliente_associado
                    lancamento.nota_fiscal = registro
                    lancamento.save()
                # realiza e registra o movimento
                for produto in produtos_vendidos_obj:
                    quantidade_movimentada = produtos_vendidos[produto.id]
                    if produto.total_produzido >= quantidade_movimentada:
                    # possui mais do que quer remover
                        quantidade_anterior = produto.total_produzido
                        quantidade_nova = int(produto.total_produzido) - int(quantidade_movimentada)
                        produto.total_produzido = quantidade_nova
                        movimento = MovimentoEstoqueProduto.objects.create(
                            produto = produto,
                            quantidade_movimentada = quantidade_movimentada,
                            quantidade_anterior = quantidade_anterior,
                            quantidade_nova = quantidade_nova,
                            operacao = "remove",
                            criado_por = request.user,
                            registro_de_nota_fiscal = registro,
                            justificativa = "Nota Fiscal Emitida: %s" % registro.notafiscal
                        )
                        produto.save()
                        messages.success(request, u"Sucesso! Removido %s Produtos %s como Produzido" % (movimento.quantidade_movimentada, movimento.produto))
                    
                return redirect(reverse("producao:registrar_nota_fiscal_emitida"))
        
        else:
            messages.warning(request, u"Erro! Estoque Inconsistente. Cheque os Quantitativos em Rastreabilidade de Produção")
            
    return render_to_response('frontend/producao/producao-registrar-nota-fiscal-emitida-adicionar.html', locals(), context_instance=RequestContext(request),)
    
