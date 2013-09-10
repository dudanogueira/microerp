# -*- coding: utf-8 -*-
import datetime, urllib
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

from django.core.mail import EmailMessage

from producao.models import FabricanteFornecedor, FABRICANTE_FORNECEDOR_TIPO_CHOICES
from producao.models import NotaFiscal
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

from rh.models import Funcionario

from django import forms

#
# DECORATORS
#

def possui_perfil_acesso_producao(user, login_url="/"):
    try:
        if user.perfilacessoproducao and user.funcionario.ativo():
            return True
    except:
        return False

@user_passes_test(possui_perfil_acesso_producao)
def home(request):
    componentes_total = Componente.objects.all().count()
    subprodutos_total = SubProduto.objects.all().count()
    produtos_total = ProdutoFinal.objects.all().count()
    fornecedores_total = NotaFiscal.objects.all().values('fabricante_fornecedor').distinct().count()
    notas_total = NotaFiscal.objects.all().count()
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
    

@user_passes_test(possui_perfil_acesso_producao)
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
            lancamento = lancamento_form.save(commit=False)
            lancamento.nota = notafiscal
            lancamento.save()
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
    
    
    class Meta:
        model = ArquivoAnexoComponente
    

## VIEWS

@user_passes_test(possui_perfil_acesso_producao)
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
        part_number = u"%s-%s%s" % (pn_prepend, tipo.slug.upper(), "%05d" % identificador)
        return render_to_response('frontend/producao/producao-adicionar-componentes.html', locals(), context_instance=RequestContext(request),)    
    else:
        # retorna à listagem
        messages.warning(request, u"Nenhuma ação tomada. É preciso escolher o tipo de Componente para adicionar")
        return redirect(reverse('producao:listar_componentes'))
    



@user_passes_test(possui_perfil_acesso_producao)
def ver_componente(request, componente_id):
    componente = get_object_or_404(Componente.objects.select_related(), pk=componente_id)
    lancamentos = LancamentoComponente.objects.filter(componente=componente, nota__status='l').order_by('-nota__data_lancado_estoque')
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
            valor = posicao.quantidade * posicao.componente.preco_liquido_unitario_real
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



@user_passes_test(possui_perfil_acesso_producao)
def ver_fabricantes_fornecedores(request, fabricante_fornecedor_id):
    fabricante_fornecedor = get_object_or_404(FabricanteFornecedor, pk=fabricante_fornecedor_id)
    fornecidos = LancamentoComponente.objects.filter(nota__fabricante_fornecedor=fabricante_fornecedor, nota__status='l').values('componente__part_number', 'componente__id', 'componente__ativo').annotate(total=Sum('quantidade')).order_by('-total')
    fabricados = LancamentoComponente.objects.filter(fabricante=fabricante_fornecedor, nota__status='l').values('componente__part_number', 'componente__medida', 'componente__ativo', 'componente__id').annotate(total=Sum('quantidade')).order_by('-total')
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
    
    componente = forms.ModelChoiceField(queryset=Componente.objects.all(), required=False)
    estoque = forms.ModelChoiceField(queryset=EstoqueFisico.objects.all(), required=False)
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
    componente = forms.ModelChoiceField(queryset=Componente.objects.all(), required=True)
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
    componente = forms.ModelChoiceField(queryset=Componente.objects.all(), required=True)
    estoque = forms.ModelChoiceField(queryset=EstoqueFisico.objects.all(), required=True)
    justificativa = forms.CharField(widget=forms.Textarea, required=True)


@user_passes_test(possui_perfil_acesso_producao)
def listar_estoque(request):
    historicos = PosicaoEstoque.objects.all().order_by('-data_entrada')
    totalizadores = RegistroValorEstoque.objects.all()
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
                    historicos = historicos.filter(estoque=estoque_consultado, componente=componente_consultado)
                    consulta_dupla = True
                    posicaoestoque = componente_consultado.posicao_no_estoque(estoque_consultado)
                    if posicaoestoque and componente_consultado.preco_liquido_unitario_real:
                        valor_no_estoque = posicaoestoque * componente_consultado.preco_liquido_unitario_real
                    else:
                        valor_no_estoque = None
                    # define os forms já sugeridos
                    form_mover_estoque = MoverEstoque(componente_consultado=componente_consultado, estoque_origem=estoque_consultado)
                    form_alterar_estoque = AlterarEstoque(estoque=estoque_consultado, componente=componente_consultado)
                # consulta somente componente
                if componente_consultado and not estoque_consultado:
                    historicos = historicos.filter(componente=componente_consultado)
                    consulta_componente = True
                    posicoes_estoque = []
                    for estoque in EstoqueFisico.objects.all():
                        try:
                            posicao = estoque.posicaoestoque_set.filter(componente=componente_consultado).order_by('-data_entrada')[0]
                        except:
                            posicao = None
                        if posicao and posicao.quantidade:
                            valor = posicao.quantidade * posicao.componente.preco_liquido_unitario_real
                            posicoes_estoque.append((posicao, valor))
                    form_mover_estoque = MoverEstoque(componente_consultado=componente_consultado)
                    form_alterar_estoque = AlterarEstoque(componente=componente_consultado)
                    
                # consulta só estoque
                if not componente_consultado and estoque_consultado:
                    historicos = historicos.filter(estoque=estoque_consultado)
                    consulta_estoque = True
                    posicoes_estoque = []
                    for componente_ver in Componente.objects.all():
                        try:
                            posicao = PosicaoEstoque.objects.filter(componente=componente_ver, estoque=estoque_consultado).order_by('-data_entrada')[0]
                        except:
                            posicao = None
                        if posicao:
                            valor = posicao.quantidade * posicao.componente.preco_liquido_unitario_real
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
                
            
    else:
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
    
    
    class Meta:
        model = DocumentoTecnicoSubProduto
        fields = 'arquivo', 'subproduto'



class AgregarSubProdutoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        subproduto_principal = kwargs.pop('subproduto_principal')
        super(AgregarSubProdutoForm, self).__init__(*args, **kwargs)
        self.fields['subproduto_principal'].initial  = subproduto_principal
        self.fields['subproduto_principal'].widget = forms.HiddenInput()
        self.fields['subproduto_agregado'].queryset = self.fields['subproduto_agregado'].queryset.exclude(id=subproduto_principal.id)
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
    
    if request.GET:
        q_subproduto = request.GET.get('q_subproduto', None)
        if q_subproduto:
            if q_subproduto == "todos":
                subprodutos_encontrados = SubProduto.objects.all()
            else:
                subprodutos_encontrados = SubProduto.objects.filter(
                    Q(nome__icontains=q_subproduto) | Q(descricao__icontains=q_subproduto) | Q(slug__icontains=q_subproduto)
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
        

    def clean_quantidade_preenchida(self):
        cleaned_data = super(FormEnviarSubProdutoParaTeste, self).clean()
        quantidade_preenchida = cleaned_data.get("quantidade_preenchida")
        quantidade_permitida = cleaned_data.get("quantidade_maxima_permitida")
        if quantidade_preenchida == 0:
            raise forms.ValidationError("Impossível mover 0 :)")
        if int(quantidade_preenchida) > int(quantidade_permitida):
            raise forms.ValidationError("Quantidade máxima permitida: %s" % quantidade_permitida)
        return quantidade_preenchida

    quantidade_maxima_permitida = forms.IntegerField(required=True)
    quantidade_preenchida = forms.IntegerField(required=True)
    subproduto = forms.ModelChoiceField(queryset=SubProduto.objects.all(), empty_label=None)
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all(), required=True)


@user_passes_test(possui_perfil_acesso_producao)
def ver_subproduto(request, subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    if request.POST:
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
                messages.success(request, u"Sucesso! Sub Produto %s agregado %s vezes no SubProduto Principal %s" % (linha_sub_agregado.subproduto_agregado, linha_sub_agregado.quantidade, linha_sub_agregado.subproduto_principal))
                return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
        
        if request.POST.get('enviar-subproduto-teste-btn', None):
            form_enviar_para_teste = FormEnviarSubProdutoParaTeste(request.POST, quantidade_maxima=subproduto.total_montado, subproduto=subproduto)
            if form_enviar_para_teste.is_valid():
                # OK, pode fazer a operacao
                # primeiro, mover as quantidades
                quantidade_preenchida = form_enviar_para_teste.cleaned_data['quantidade_preenchida']
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
                )
                messages.success(request, u"Sucesso! Criado o Registro de Teste de SubProduto #%s " % registro.id)
                return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
        
        
                
        
        if request.POST.get('enviar-subproduto-funcional-btn', None):
            form_enviar_para_funcional = FormEnviarSubProdutoParaTeste(request.POST, quantidade_maxima=subproduto.total_montado, subproduto=subproduto)
            if form_enviar_para_funcional.is_valid():
                quantidade_preenchida = form_enviar_para_funcional.cleaned_data['quantidade_preenchida']
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
                )
                messages.success(request, u"Sucesso! Criado o Registro Saída de Teste de SubProduto #%s " % registro.id)
                return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]))
            
            
    else:
        form_anexos = ArquivoAnexoSubProdutoForm(subproduto=subproduto)
        form_imagem = ImagemSubprodutoForm(instance=subproduto)
        form_agregar_subproduto = AgregarSubProdutoForm(subproduto_principal=subproduto)
        form_enviar_para_teste = FormEnviarSubProdutoParaTeste(quantidade_maxima=subproduto.total_montado, subproduto=subproduto)
        form_enviar_para_funcional = FormEnviarSubProdutoParaTeste(quantidade_maxima=subproduto.total_testando, subproduto=subproduto)
        
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
    except:
        messages.error(request, "Erro! Linha não Apagada.")
    return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]) + "#linhas-componente")


@user_passes_test(possui_perfil_acesso_producao)
def editar_linha_subproduto(request, subproduto_id, linha_subproduto_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    linha = get_object_or_404(LinhaSubProduto, subproduto=subproduto, pk=linha_subproduto_id)
    if request.POST:
        form = LinhaSubProdutoForm(request.POST, instance=linha)
        if form.is_valid():
            linha = form.save()
            messages.success(request, u"Sucesso! Linha alterada.")
            return redirect(reverse("producao:ver_subproduto", args=[subproduto.id]) + "#linhas-componente")
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
                opcao = form.save()
                opcao.padrao = True
            else:
                opcao = form.save()
                opcao.padrao = None
            opcao.save()            
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
        if opcao.componente.id == l.opcao_padrao().componente.id:
            inedito = False
            messages.error(request, u"Impossível tornar esta opção como Padrão: Componente %s já identificado como padrão na Linha #%s" % (opcao.componente.part_number, linha.id))
            return redirect(reverse("producao:editar_linha_subproduto", args=[linha.subproduto.id, linha.id]))
    
    # transforma todas as opcoes da linha em nao padrao
    linha.opcaolinhasubproduto_set.all().update(padrao=None)
    # define a opcao escolhida como padrao
    opcao.padrao = True
    opcao.save()
    # retorna a exibição da linha
    messages.success(request, u"Sucesso! Nova opção padrão definida!")
    
    return redirect(reverse("producao:editar_linha_subproduto", args=[linha.subproduto.id, linha.id]))

def apagar_opcao_linha_subproduto(request, subproduto_id, linha_subproduto_id, opcao_linha_subproduto_id):
    opcao = get_object_or_404(OpcaoLinhaSubProduto, pk=opcao_linha_subproduto_id, linha__pk=linha_subproduto_id, linha__subproduto__pk=subproduto_id)
    if not opcao.padrao:
        try:
            opcao.delete()
            messages.success(request, u"Sucesso! Opção Removida!")
        except:
            messages.error(request, u"Erro ao remover Opção.")
    return redirect(reverse("producao:editar_linha_subproduto", args=[opcao.linha.subproduto.id, opcao.linha.id]))

def subproduto_apagar_linha_subproduto_agregado(request, subproduto_id, linha_subproduto_agregado_id):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    linha_agregada = get_object_or_404(LinhaSubProdutoAgregado, subproduto_principal=subproduto, pk=linha_subproduto_agregado_id)
    linha_agregada.delete()
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
        fields = ('imagem', 'nome', 'slug', 'descricao', 'quantidade_estimada_producao_semanal')

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


    class Meta:
        model = DocumentoTecnicoProduto
        fields = 'arquivo', 'produto'
    
    

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
    if request.GET:
        q_produto = request.GET.get('q_produto', True)
        if q_produto:
            if q_produto == "todos":
                produtos_encontrados = ProdutoFinal.objects.all()
            else:
                produtos_encontrados = ProdutoFinal.objects.filter(
                    Q(nome__icontains=q_componente) | Q(descricao__icontains=q_componente) | Q(tipo__nome__icontains=q_componente)
                )
        
    return render_to_response('frontend/producao/producao-listar-produtos.html', locals(), context_instance=RequestContext(request),)    

@user_passes_test(possui_perfil_acesso_producao)
def adicionar_produto(request):
    if request.POST:
        form = ProdutoFinalForm(request.POST, request.FILES)
        produto = form.save()
        messages.success(request, u"Sucesso! Produto adicionado.")
        return redirect(reverse("producao:ver_produto", args=[produto.id],))
    else:
        form = ProdutoFinalForm()
    return render_to_response('frontend/producao/producao-adicionar-produto.html', locals(), context_instance=RequestContext(request),)    

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

@user_passes_test(possui_perfil_acesso_producao)
def ver_produto(request, produto_id):
    produto = get_object_or_404(ProdutoFinal, pk=produto_id)
    if request.POST:
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
        
                
    else:
        form_adicionar_linha_subproduto = AdicionarLinhaSubProdutoAoProdutoFinalForm(produto=produto)
        form_adicionar_linha_componentes_avulsos = AdicionarLinhaComponenteAvulsoAoProdutoFinalForm(produto=produto)
        form_imagem = AlterarImagemProduto(instance=produto)
        form_anexos = ArquivoAnexoProdutoForm(produto=produto)
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
    quantidade = forms.IntegerField(required=True)
    subproduto = forms.ModelChoiceField(queryset=SubProduto.objects.exclude(tipo_de_teste=0), empty_label=None)
    subproduto.widget.attrs['class'] = 'select2'


class SelecionarProdutoForm(forms.Form):
    quantidade = forms.IntegerField(required=True)
    produto = forms.ModelChoiceField(queryset=ProdutoFinal.objects.all(), empty_label=None)
    produto.widget.attrs['class'] = 'select2'
 
@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao(request):
    form_subproduto = SelecionarSubProdutoForm()
    form_produto = SelecionarProdutoForm()
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
    
@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao_subproduto_confirmar(request, subproduto_id, quantidade_solicitada):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
    estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
    #extra configuracao
    if request.POST.get('configuracao', None):
        configuracao = request.POST.get('configuracao', None)
        import ast
        conf = ast.literal_eval(configuracao)
        componentes = subproduto.get_componentes(conf=conf, multiplicador=float(quantidade_solicitada))
        # registra a ordem de producao
        ordem_producao_subproduto = OrdemProducaoSubProduto.objects.create(
            subproduto=subproduto,
            quantidade=quantidade_solicitada,
            string_producao=componentes,
            criado_por=request.user, 
        )
        messages.success(request, "Ordem de Produção criada")
        # dar baixa em todos os items do componentes
        for item in componentes.items():
            # longo ou inteiro, é componente
            if type(item[0]) == long:
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
        elif subproduto.tipo_de_teste == 2:
            # tipo de teste composto, vai pra seção de montados pra depois testar
            total_anterior = subproduto.total_montado
            novo_total = total_anterior + int(quantidade_solicitada)
            subproduto.total_montado = novo_total
            messages.success(request, u"Novo Valor de SubProduto %s em Total Montado: %s + %s = %s" % (subproduto, total_anterior, int(quantidade_solicitada), novo_total))
        subproduto.save()

    return render_to_response('frontend/producao/producao-ordem-de-producao-confirmado.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_producao_subproduto(request, subproduto_id, quantidade_solicitada):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    if request.POST:
        linhas = []
        form_configurador_subproduto = FormConfiguradorSubProduto(request.POST, subproduto=subproduto)
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
                if type(item[0]) == long:
                    # verifica se possui a quantidade total deste componente em estoque
                    qtd_componente = item[1]
                    posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                    # quantiade no estoque insuficiente
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
                        messages.error(request, "Quantidade Indisponível (FALTOU: %s) de SubProduto %s" % (faltou, item[0]))
                    
            
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
        if type(item[0]) == long:
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
            messages.success(request, u"Removido do Total Funcional do Subproduto %s: %s - %s = %s" % (subproduto_remover, posicao_atual, float(item[1]), nova_posicao))

    # incrementa o produto em seu total_produzido
    produto_total_produzido = produto.total_produzido
    novo_valor = int(produto_total_produzido) + int(quantidade_solicitada)
    produto.total_produzido = novo_valor
    produto.save()
    messages.success(request, u"Novo Valor para Total Produzido do Produto %s: %s -> %s" % (produto.part_number(), produto_total_produzido, novo_valor))
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
                if type(item[0]) == long:
                    # verifica se possui a quantidade total deste componente em estoque
                    qtd_componente = item[1]
                    posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                    # quantiade no estoque insuficiente
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

@user_passes_test(possui_perfil_acesso_producao)
def arvore_de_produto(request):
    produtos = ProdutoFinal.objects.all()
    return render_to_response('frontend/producao/producao-arvore-de-produto.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def arvore_de_produto_ajax_subproduto(request, subproduto_id, parente):
    subproduto = get_object_or_404(SubProduto, pk=subproduto_id)
    return render_to_response('frontend/producao/producao-arvore-de-produto-ajax-subproduto.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def registro_de_testes(request):
    return render_to_response('frontend/producao/producao-registro-de-testes.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def totalizador_de_producao(request):
    produtos = ProdutoFinal.objects.all().order_by('-total_produzido')
    subprodutos = SubProduto.objects.all().order_by('-total_funcional')
    return render_to_response('frontend/producao/producao-ordem-de-producao-ajax-totalizador-producao.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def producao_combinada(request):
    produtos = ProdutoFinal.objects.all().order_by('-total_produzido')
    subprodutos = SubProduto.objects.all().order_by('-total_funcional')
    return render_to_response('frontend/producao/producao-ordem-de-producao-producao-combinada.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def producao_combinada_calcular(request):
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
                            quantidade_analisada.append((produto, value))
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
                            quantidade_analisada.append((subproduto, value))
            except:
                raise
        # verificar cada uma dessas quantidades
        #verifica toda a produção conforme a notação de componentes
        get_componentes = dic
        slug_estoque_produtor = getattr(settings, 'ESTOQUE_FISICO_PRODUTOR', 'producao')
        estoque_produtor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_produtor)
        relatorio_producao = []
        for item in get_componentes.items():
            if type(item[0]) == long:
                # verifica se possui a quantidade total deste componente em estoque
                qtd_componente = item[1]
                posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
                componente = Componente.objects.get(pk=int(item[0]))
                # quantiade no estoque insuficiente
                pode = True
                faltou = None
                if float(qtd_componente) > float(posicao_em_estoque_produtor):
                    faltou = float(qtd_componente) - float(posicao_em_estoque_produtor)
                    producao_liberada = False
                    pode = False
                    # item de producao, #quantidade_atual, #posicao_estoque, #faltante 
                    relatorio_producao.append((componente, componente.descricao, qtd_componente, posicao_em_estoque_produtor, faltou, pode))
            elif type(item[0]) == str:
                subproduto_id = item[0].split("-")[1]
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
                    faltou = float(qtd_subproduto) - float(quantidade_disponivel)
                    pode = False
                    relatorio_producao.append((subproduto_usado, subproduto_usado.descricao, qtd_subproduto, quantidade_disponivel, faltou, pode))
             
    return render_to_response('frontend/producao/producao-ordem-de-producao-producao-combinada-calcular.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def qeps_componentes(request):
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
    for item in dic.items():
        if type(item[0]) == long:
            qtd_componente = item[1]
            posicao_em_estoque_produtor = estoque_produtor.posicao_componente(item[0])
            componente = Componente.objects.get(pk=int(item[0]))
            quantidade_lead_time = item[1] * componente.lead_time
            diferenca = float(posicao_em_estoque_produtor) - float(quantidade_lead_time)
            if diferenca > 0:
                ok = True
            else:
                ok = False
            tabela_items.append((componente, posicao_em_estoque_produtor, quantidade_lead_time, diferenca, ok))
            
    return render_to_response('frontend/producao/producao-ordem-de-producao-ajax-qeps-componentes.html', locals(), context_instance=RequestContext(request),)

@user_passes_test(possui_perfil_acesso_producao)
def preparar_producao_semanal(request):
    produtos = ProdutoFinal.objects.all().order_by('-total_produzido')
    subprodutos = SubProduto.objects.all().order_by('-total_funcional')
    return render_to_response('frontend/producao/producao-ordem-de-producao-preparacao-producao.html', locals(), context_instance=RequestContext(request),)

class FormOrdemDeCompraFiltro(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FormOrdemDeCompraFiltro, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs['class'] = 'datepicker'
        self.fields['data_fim'].widget.attrs['class'] = 'datepicker'
    
    funcionario = forms.ModelChoiceField(queryset=Funcionario.objects.all(), required=False)
    fornecedor = forms.ModelChoiceField(queryset=FabricanteFornecedor.objects.all(), required=False)
    mostrar_somente_abertos = forms.BooleanField(initial=True, required=False)
    data_inicio = forms.DateField(label=u"Data Início Abertura", initial=datetime.date.today(), required=True)
    data_fim = forms.DateField(label=u"Data Fim Abertura", initial=datetime.date.today()+datetime.timedelta(days=7), required=True)

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
        
    class Meta:
        model = OrdemDeCompra

class FormAddAtividadeOrdemDeCompra(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        ordem_de_compra = kwargs.pop('ordem_de_compra')
        super(FormAddAtividadeOrdemDeCompra, self).__init__(*args, **kwargs)
        self.fields['ordem_de_compra'].initial  = ordem_de_compra
        self.fields['ordem_de_compra'].widget = forms.HiddenInput()
        self.fields['data'].widget.attrs['class'] = 'datepicker'

    
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
        
        
    class Meta:
        model = ComponentesDaOrdemDeCompra

@user_passes_test(possui_perfil_acesso_producao)
def ordem_de_compra(request):
    ordens = OrdemDeCompra.objects.filter(data_fechado=None).order_by('data_aberto')
    if request.POST:
        if request.POST.get("form-adicionar-ordem-de-compra", None):
            form_adicionar_ordem_de_compra = FormAdicionarOrdemDeCompra(request.POST)
            if form_adicionar_ordem_de_compra.is_valid():
                ordem_de_compra = form_adicionar_ordem_de_compra.save(commit=False)
                ordem_de_compra.funcionario = request.user.funcionario
                ordem_de_compra.save()
                return redirect(reverse('producao:ordem_de_compra_editar', args=[ordem_de_compra.id]))
        if request.POST.get("form-filtrar-ordem-de-compra", None):
            form_adicionar_ordem_de_compra = FormAdicionarOrdemDeCompra()
            form_filtro = FormOrdemDeCompraFiltro(request.POST)
            if form_filtro.is_valid():
                # define o filtro
                ordens = OrdemDeCompra.objects.filter(data_aberto__range=(form_filtro.cleaned_data['data_inicio'], form_filtro.cleaned_data['data_fim'])).order_by('data_aberto')
                if form_filtro.cleaned_data['mostrar_somente_abertos']:
                    ordens = ordens.filter(data_fechado=None)
                if form_filtro.cleaned_data['funcionario']:
                    ordens = ordens.filter(funcionario=form_filtro.cleaned_data['funcionario'])
                if form_filtro.cleaned_data['fornecedor']:
                    ordens = ordens.filter(fornecedor=form_filtro.cleaned_data['fornecedor'])

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
        if request.POST.get('adicionar-atividade', None):
            form_editar_ordem = FormAdicionarOrdemDeCompraFull(instance=ordem)
            form_add_componentes = FormAddComponentesDaOrdemDeCompra(ordem_de_compra=ordem)
            form_add_atividade = FormAddAtividadeOrdemDeCompra(request.POST, ordem_de_compra=ordem)
            if form_add_atividade.is_valid():
                atividade = form_add_atividade.save()
                messages.success(request, u"Atividade #%s Adicionada à Ordem de Compra %s" % (atividade, ordem))
        if request.POST.get('vincular_componentes', None):
            form_add_componentes = FormAddComponentesDaOrdemDeCompra(request.POST, ordem_de_compra=ordem)
            form_editar_ordem = FormAdicionarOrdemDeCompraFull(instance=ordem)
            form_add_atividade = FormAddAtividadeOrdemDeCompra(ordem_de_compra=ordem)
            if form_add_componentes.is_valid():
                vinculacao = form_add_componentes.save()
                messages.success(request, u"Componente %s com Quantidade %s vinculado à ordem de Compra %s" % (vinculacao.componente_comprado, vinculacao.quantidade_comprada, vinculacao.ordem_de_compra))
            
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
    fechados = RequisicaoDeCompra.objects.filter(atendido=True)
    if request.GET.get('criticidade', None):
            abertos = abertos.filter(criticidade=request.GET.get('criticidade', None))
    
    if request.POST:
        form_add_requisicao_de_compra = AddRequisicaoDeCompra(request.POST, solicitante=request.user.funcionario)
        if form_add_requisicao_de_compra.is_valid():
            requisicao_compra = form_add_requisicao_de_compra.save()
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
                messages.success(request, u"Sucesso! Email enviado para os gerentes.")
            except:
                messages.error(request, u"Erro! Email não enviado.")
            
            
    else:
        form_add_requisicao_de_compra = AddRequisicaoDeCompra(solicitante=request.user.funcionario)
    return render_to_response('frontend/producao/producao-requisicao-de-compra.html', locals(), context_instance=RequestContext(request),)

def requisicao_de_compra_atendido(request, requisicao_id):
    requisicao = get_object_or_404(RequisicaoDeCompra, pk=requisicao_id)
    requisicao.atendido = True
    requisicao.atendido_em = datetime.datetime.now()
    requisicao.save()
    return redirect(reverse('producao:requisicao_de_compra'))