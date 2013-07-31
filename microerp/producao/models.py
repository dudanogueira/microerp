# -*- coding: utf-8 -*-
import datetime, os
from django.db import models
from django.conf import settings
from django.db.models import signals

from django.core.exceptions import ValidationError

from django.db.models import Sum, Avg


COMPONENTE_UNIDADE_MEDIDA = (
    ('un', 'Unidade'),
    ('m', 'Metro'),
)

FABRICANTE_FORNECEDOR_TIPO_CHOICES = (
    ('fabricante', 'Fabricante'),
    ('fornecedor', 'Fornecedor'),
    ('fabricantefornecedor', 'Fabricante e Fornecedor'),
)

STATUS_NOTA_FISCAL = (
    ('a', 'Aberta'),
    ('l', 'Lançada'),
)

TIPO_NOTA_FISCAL = (
    ('n', 'Nacional'),
    ('i', 'Internacional'),
)


TIPO_NACIONALIDADE_COMPONENTE = (
    ('n', 'Nacional'),
    ('i', 'Internacional'),
)


class PerfilAcessoProducao(models.Model):
    '''Perfil de Acesso à Produção'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso à Produção"
        verbose_name_plural = u"Perfis de Acesso à Produção"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")


class EstoqueFisico(models.Model):
    
    def __unicode__(self):
        return u"%s (identificador: %s)" % (self.nome, self.identificacao)
    
    '''Estoque fisico onde se armazena componentes'''
    ativo = models.BooleanField(default=True)
    nome = models.CharField(blank=True, max_length=100)
    identificacao = models.SlugField()
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class PosicaoEstoque(models.Model):
    '''Registro histórico de entradas de posicao de componentes em estoque fisico'''
    
    def __unicode__(self):
        return u"Posição do componente %s no dia %s no estoque %s" % (self.componente, self.data_entrada.strftime("%d/%m/%y %H:%M"), self.estoque)
    
    class Meta:
        ordering = ('-criado', '-id')
    
    data_entrada = models.DateTimeField(blank=True, default=datetime.datetime.now)
    nota_referencia = models.ForeignKey('NotaFiscal', blank=True, null=True, on_delete=models.PROTECT)
    componente = models.ForeignKey('Componente')
    estoque = models.ForeignKey('EstoqueFisico')
    quantidade = models.DecimalField(max_digits=15, decimal_places=2)
    quantidade_alterada = models.CharField(blank=True, max_length=100)
    # meta
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    justificativa = models.TextField(blank=True)
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class ComponenteTipo(models.Model):
    '''tipo/categoria de componente'''
    
    def save(self, *args, **kwargs):
            # se não existir part_number, forcar o padrao
            if not self.slug:
                self.slug = self.nome[0:3]
            super(ComponenteTipo, self).save(*args, **kwargs)    
    
    
    def __unicode__(self):
        return "%s - %s" % (self.slug, self.nome)
    
    slug = models.SlugField(u"Abreviação", max_length=3, unique=True)
    nome = models.CharField(u"Descrição", blank=False, null=False, max_length=100, unique=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class LinhaFornecedorFabricanteComponente(models.Model):
    
    def __unicode__(self):
        return u"Linha de conversão em %s: %s <-> %s" % (self.fornecedor, self.part_number_fornecedor, self.componente)
    
    class Meta:
        unique_together = (('componente', 'part_number_fornecedor', 'fornecedor'))
        
    componente = models.ForeignKey('Componente')
    part_number_fornecedor = models.CharField(blank=True, max_length=100)
    fornecedor = models.ForeignKey('FabricanteFornecedor', related_name="fornecedor_componente_set")
    part_number_fabricante = models.CharField(blank=True, null=True, max_length=100, )
    fabricante = models.ForeignKey('FabricanteFornecedor', related_name="fabricante_componente_set", blank=True, null=True)
    

class Componente(models.Model):
    '''Componente de SubProdutos e Produtos
    part_number deve ser formado por:
    self.tipo.nome[0:3]-self.identificador
    sendo este único
    '''
    
    def __unicode__(self):
        if self.part_number:
            return "%s - %s" % (self.part_number, self.descricao)
        else:
            pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
            return u"%s-%s%s %s" % (pn_prepend, self.tipo.slug.upper(), "%05d" % self.identificador, self.descricao)
    
    def save(self, *args, **kwargs):
            pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
            # se não existir part_number, forcar o padrao
            if not self.part_number:
                self.part_number = u"%s-%s%s" % (pn_prepend, self.tipo.slug.upper(), "%05d" % self.identificador)
            super(Componente, self).save(*args, **kwargs)    

    
    class Meta:
        unique_together = (('identificador', 'tipo'))
    
    def posicao_no_estoque(self, estoque):
        try:
            posicao = self.posicaoestoque_set.filter(estoque=estoque).order_by('-data_entrada')[0].quantidade
        except:
            posicao = 0
        return posicao
    
    def registrar_preco_medio(self):
        pm = LancamentoComponente.objects.filter(componente=self).aggregate(avg=Avg('valor_unitario_final'))['avg']
        self.preco_medio_unitario = pm
        self.save()

    def quem_fornece(self):
        pass
        
    
    def componente_local_imagem(instance, filename):
        return os.path.join(
            'componente/', str(instance.part_number), 'imagem', filename
          )
    
    
    # geral
    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to=componente_local_imagem, blank=True, null=True)
    part_number = models.CharField("PART NUMBER", help_text="IDENTIFICADOR GERADO AUTOMÁTICO", blank=True, null=True, max_length=100)
    identificador = models.IntegerField("Identificador único junto a categoria", blank=True, null=True, default=1)
    tipo = models.ForeignKey('ComponenteTipo', blank=False, null=False)    
    descricao = models.TextField("Descrição", blank=True)
    nacionalidade = models.CharField(blank=False, max_length=1, choices=TIPO_NACIONALIDADE_COMPONENTE)
    ncm = models.CharField("NCM", blank=True, max_length=100)
    # lead time
    lead_time = models.IntegerField("Lead Time (Semanas)", blank=False, null=False)
    
    ## preco_liquido_unitario_dolar
    #Obrigatorio se for componente importado, vai ser aramazenado o ultimo preco do lancamento
    preco_liquido_unitario_dolar = models.DecimalField("Preço Líquido Unitário em Dólar", help_text="INSERIDO AUTOMATICAMENTE DA ULTIMA COMPRA", max_digits=10, decimal_places=2, default=0)
    
    # preco_bruto_unitrario_real - calculado no lancamento, onde deve ser preenchido a cotacao
    # do dolar, a incencia de imposto, vai ser calculado conforme a media dos lancamentos passados.
    preco_liquido_unitario_real = models.DecimalField("Preço Líquido Unitário em Real", help_text="INSERIDO AUTOMATICAMENTE DA ULTIMA COMPRA", max_digits=10, decimal_places=2, default=0)
    
    # preco_medio_unitario
    preco_medio_unitario = models.DecimalField("Preço Médio Bruto Unitário", max_digits=10, decimal_places=2, default=0)
    # medida
    medida = models.CharField(blank=True, max_length=100, choices=COMPONENTE_UNIDADE_MEDIDA, default='un')
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class ArquivoAnexoComponente(models.Model):
    
    
    def anexo_componente_local(instance, filename):
        return os.path.join(
            'componente/', str(instance.componente.part_number), 'anexos', filename
          )
    
    
    componente = models.ForeignKey('Componente')
    arquivo = models.FileField(upload_to=anexo_componente_local)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    

class FabricanteFornecedor(models.Model):
    
    def __unicode__(self):
        if self.tipo:
            return u"%s: %s" % (self.get_tipo_display(), self.nome)
        else:
            if self.nome:
                return self.nome
            else:
                return "Nome Não Preenchido"
    
    
    def nome_curto(self):
        return " ".join(self.nome.split()[0:2])
    
    
    tipo = models.CharField(blank=True, max_length=100, choices=FABRICANTE_FORNECEDOR_TIPO_CHOICES)
    ativo = models.BooleanField(default=True)
    nome = models.CharField(u"Razão Social", blank=False, null=False, max_length=100)
    cnpj = models.CharField("CNPJ", blank=True, max_length=400)
    contatos = models.TextField(blank=True)
    rua = models.CharField(blank=True, max_length=100)
    numero = models.CharField(blank=True, max_length=100)
    bairro = models.CharField(blank=True, max_length=100)
    cep = models.CharField("CEP", blank=True, max_length=100)
    cidade = models.CharField(blank=True, max_length=100)
    estado = models.CharField(blank=True, max_length=100)
    telefone = models.CharField(blank=True, max_length=100)
    
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")


class LancamentoComponente(models.Model):
    
    def __unicode__(self):
        return u"Lançamento %s da nota %s Componente: %s" % (self.id, self.nota, self.componente)
        
    class Meta:
        unique_together = (('part_number_fornecedor', 'componente', 'nota'), ('part_number_fornecedor', 'nota'))
        ordering = ('peso', 'nota')
        
    def converter_part_number_fornecedor(self):
        '''Busca o part_number_fornecedor do produto na tabela de conversao e relaciona com o produto'''
        try:
            conversao = LinhaFornecedorFabricanteComponente.objects.get(part_number_fornecedor=self.part_number_fornecedor, fornecedor=self.nota.fabricante_fornecedor)
            self.componente = conversao.componente
            self.save()
        except:
            pass
            
        

    def calcula_totais_lancamento(self):
        if self.nota.status == 'a':
            if self.nota.tipo == 'n':
                # nota nacional, calculo direto, sem conversao, sem imposto
                self.valor_total_sem_imposto = float(self.quantidade) * float(self.valor_unitario)
                # nota nacional, calculo direto, sem conversao, com imposto
                percentual = float(self.valor_unitario) * float(self.impostos) / float(100)
                self.valor_total_com_imposto = (float(self.valor_unitario) + float(percentual)) * float(self.quantidade)
            elif self.nota.tipo == 'i':
                # nota internacional, calculo direto, com conversao de dolar, sem imposto
                self.valor_total_sem_imposto = float(self.quantidade) * float(self.valor_unitario) * float(self.nota.cotacao_dolar)
                # nota internacional, calculo direto, com conversao de dolar, com imposto
                percentual = float(self.valor_unitario * self.nota.cotacao_dolar) * float(self.impostos) / float(100)
                self.valor_total_com_imposto = (float(self.valor_unitario * self.nota.cotacao_dolar) + float(percentual)) * float(self.quantidade)

            
    def save(self, *args, **kwargs):
            self.calcula_totais_lancamento()            
            super(LancamentoComponente, self).save(*args, **kwargs)
    
    def busca_part_number_na_memoria(self):
        # se tiver o part_number_fornecedor, buscar informações
        if self.part_number_fornecedor:
            conversoes = LinhaFornecedorFabricanteComponente.objects.filter(part_number_fornecedor=self.part_number_fornecedor, fornecedor=self.nota.fabricante_fornecedor)
            if conversoes.count() == 1:
                # so encontrou um, assumir como padrao
                self.fabricante = conversoes[0].fabricante
                self.part_number_fabricante = conversoes[0].part_number_fabricante
                self.componente = conversoes[0].componente
                self.save()
        
    

    def clean(self):
        # mecanismo para atualizar a memoria de opcao do lancamento
        if self.aprender and self.part_number_fornecedor and self.componente:
            # aprender a combinacao de PN Fornecedor com PN Mestria, 
            # PN Fabricante e Fabricante para uso posterior
            conversao,created = LinhaFornecedorFabricanteComponente.objects.get_or_create(part_number_fornecedor=self.part_number_fornecedor, fornecedor=self.nota.fabricante_fornecedor, componente=self.componente)
            conversao.componente = self.componente
            conversao.part_number_fornecedor = self.part_number_fornecedor
            conversao.part_number_fabricante = self.part_number_fabricante
            conversao.fabricante = self.fabricante
            conversao.save()
            # reinicia o valor do campo
            self.aprender = False
        

    def identificar_partnumber(self):
        # se tiver o part_number_fornecedor, buscar informações
        if self.part_number_fornecedor:
            conversoes = LinhaFornecedorFabricanteComponente.objects.filter(part_number_fornecedor=self.part_number_fornecedor, fornecedor=self.nota.fabricante_fornecedor)
            if conversoes.count() == 1:
                # so encontrou um, assumir como padrao
                self.fabricante = conversoes[0].fabricante
                self.part_number_fabricante = conversoes[0].part_number_fabricante
                self.componente = conversoes[0].componente
                self.save()
            #if conversoes.count() > 1:
            #    pns = []
            #    for l in conversoes:
            #        pns.append(l.componente)
            #    raise ValidationError(u'Erro! Este Part Number do Fornecedor aponta para mais de um PART NUMBER MESTRIA: %s' % pns)
            #if conversoes.count() == 0:
                # nenhuma conversao encontrada
            #    if self.componente:
                    # part number escolhido, checar se o partnumber já possui um código neste cliente
             #       try:
             #           conversao = LinhaFornecedorFabricanteComponente.objects.get(componente=self.componente, fornecedor=self.nota.fabricante_fornecedor)
            #            raise ValidationError(u'Erro! Este PART NUMBER MESTRIA já existe com o código de %s' % conversao.part_number_fornecedor)                        
            #        except LinhaFornecedorFabricanteComponente.DoesNotExist:
                        # nao possui, aprender se pedido for
            #            raise ValidationError(u'Aprender!')
                
            #    else:
            #        raise ValidationError(u'Erro! Part Number do Fornecedor não encontrado. Escolha o PART NUMBER MESTRIA')
            
                
    
    
    nota = models.ForeignKey('NotaFiscal')
    peso = models.IntegerField(blank=True, null=True)
    # quick create
    part_number_fornecedor = models.CharField("Part Number Fornecedor", blank=True, max_length=100)
    quantidade = models.DecimalField(max_digits=15, decimal_places=2)
    valor_unitario = models.DecimalField("Valor Unitário (R$)", max_digits=10, decimal_places=2, default=0)
    impostos = models.DecimalField("Incidência de Impostos (%)", help_text=u"Incidência total de impostos deste Lançamento em (%)", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    
    #campos automaticamente sugeridos, preenchidos opcionais
    componente = models.ForeignKey('Componente', verbose_name=getattr(settings, 'NOME_PART_NUMBER_INTERNO', 'PART NUMBER'), blank=True, null=True)
    fabricante = models.ForeignKey('FabricanteFornecedor', blank=True, null=True)
    part_number_fabricante = models.CharField("Part Number Fabricante", blank=True, max_length=100)
    
    # ativar o aprender / memorizar opcoes
    aprender = models.BooleanField(default=False)
    
    valor_total_sem_imposto = models.DecimalField("Total do Lançamento sem Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    valor_total_com_imposto = models.DecimalField("Total do Lançamento com Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)    
    valor_taxa_diversa_proporcional = models.DecimalField("Valor proporcional da Taxa Diversa da Nota", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    valor_unitario_final = models.DecimalField("Valor Unitário Bruto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=False, null=False)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    
class NotaFiscal(models.Model):
    
    def __unicode__(self):
        return u"Nota Fiscal Série %s, Número: %s, %s de %s" % (self.numero_de_serie(), self.numero_identificador(), self.get_tipo_display(), self.fabricante_fornecedor)
    
    class Meta:
        unique_together = (('fabricante_fornecedor', 'numero'))
    
    def numero_de_serie(self):
        return self.numero[0:3]
    
    def numero_identificador(self):
        return self.numero[3:]
    
    def lancar_no_estoque(self, user_id=None):
        '''lanca a nota fiscal no estoque configurado como receptor'''
        try:
            if self.status == 'a':
                # nota precisa estar aberta para ser lancada no estoque receptor
                slug_estoque_receptor = getattr(settings, 'ESTOQUE_FISICO_RECEPTOR', 'reserva')
                estoque_receptor,created = EstoqueFisico.objects.get_or_create(identificacao=slug_estoque_receptor)
                # para cada item da nota, lancar
                for item in self.lancamentocomponente_set.all():
                    try:
                        posicao_atual = PosicaoEstoque.objects.filter(estoque=estoque_receptor, componente=item.componente).order_by('-data_entrada')[0].quantidade
                    except:
                        posicao_atual = 0
                    posicao_calculada = posicao_atual + item.quantidade
                    posicao_nova = PosicaoEstoque.objects.create(estoque=estoque_receptor, componente=item.componente, quantidade=posicao_calculada, nota_referencia=self)
                    if user_id:
                        posicao_nova.criado_por_id = user_id
                        posicao_nova.save()
                    # registra o preco medio do compoente
                    item.componente.registrar_preco_medio()
                    if item.nota.tipo == 'i': # nota internacional
                        # registra o preco liquido unitario em dolar no componente, para memoria da proxima conta
                        item.componente.preco_liquido_unitario_dolar = item.valor_unitario
                        # converte de dolar pra real com a cotacao da nota
                        item.componente.preco_liquido_unitario_real = float(item.valor_unitario) * float(self.cotacao_dolar) 
                        # registra o preco liquido unitario em real
                    else:
                        item.componente.preco_liquido_unitario_real = item.valor_unitario
                    item.componente.save()
                        
                        

                self.status = 'l'
                self.save()
                return True
        except:
            raise
            return False
    
    def clean(self):
        if self.tipo == 'i' and not self.cotacao_dolar:
            raise ValidationError(u'Erro! Para Notas Fiscais Internacionais, é obrigatório preencher a cotação do dólar.')
        if self.status == 'l' and self.lancamentocomponente_set.count() == 0:
            raise ValidationError(u'Erro! Esta nota não possui nenhum lançamento!')    
    
    def calcula_totais_nota(self):
        if self.status == 'a':
            # calcula totais dos lancamentos
            # agrega totais dos lancamentos na nota
            totais = self.lancamentocomponente_set.aggregate(sem=Sum('valor_total_sem_imposto'),com=Sum('valor_total_com_imposto')
)
            self.total_sem_imposto = totais['sem']
            self.total_com_imposto = totais['com']
            if self.tipo == 'i':
                self.total_da_nota_em_dolar = self.total_sem_imposto / self.cotacao_dolar
            self.save()
            # distribui as taxas extra proporcionalmente
            for item in self.lancamentocomponente_set.all():
                # descobre qual a porcentagem do total do lancamento em relacao ao total da nota
                porcentagem = 100 * float(item.valor_total_com_imposto) / float(self.total_com_imposto)
                # aplica o percentual encontrado às taxas extra
                # 100 - self.nota.taxas_diversas
                # percentual - x
                # x = percentual * taxas_diversas / 100
                valor_proporconal = porcentagem * float(self.taxas_diversas) / 100
                item.valor_taxa_diversa_proporcional = valor_proporconal
                # calcula valor unitario final:
                #   total do lancamento com impostos dividido por quantidade
                valor_unitario = float(item.valor_total_com_imposto) / float(item.quantidade)
                #   total do valor de taxas extra proporcial dividido por quantidade
                valor_taxas_extra_unitario = item.valor_taxa_diversa_proporcional / float(item.quantidade)
                # ambos somados, sao o numero final do valor unitario, para fins de calculo do preco medio
                item.valor_unitario_final = float(valor_taxas_extra_unitario) + float(valor_unitario)   
                item.save()
    
    #arquivo = models.FileField(upload_to=arquivo)
    numero = models.CharField("Número", max_length=100, blank=False, null=False)
    tipo = models.CharField(blank=False, max_length=1, choices=TIPO_NOTA_FISCAL)
    taxas_diversas = models.DecimalField("Valores Diversos (R$)", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    cotacao_dolar = models.DecimalField("Cotação do Dolar em Relação ao Real (R$)", help_text="utilizado somente em notas Internacionais", max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(blank=True, max_length=100, choices=STATUS_NOTA_FISCAL, default='a')
    fabricante_fornecedor = models.ForeignKey('FabricanteFornecedor', verbose_name="Fornecedor")
    data_entrada = models.DateTimeField(blank=True, default=datetime.datetime.now)
    data_lancado_estoque = models.DateTimeField(blank=True, null=True)
    lancado_por = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    # totais e valores
    total_sem_imposto = models.DecimalField("Total da Nota sem Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    total_com_imposto = models.DecimalField("Total da Nota com Imposto", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    # para nota internacional
    total_da_nota_em_dolar = models.DecimalField("Total da Nota em Dolar", help_text="Campo calculado automaticamente", max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

# SUBPRODUTO

def subproduto_local_imagem(instance, filename):
    return os.path.join(
        'subproduto/', str(instance.id), filename
      )

class SubProduto(models.Model):
    
    def __unicode__(self):
        pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
        return "%s-SUB%s %s" % (pn_prepend, "%05d" % self.id, self.nome)
    
    imagem = models.ImageField(upload_to=subproduto_local_imagem, blank=True, null=True)
    nome = models.CharField(blank=True, max_length=100)
    descricao = models.TextField(blank=True)
    possui_tags = models.BooleanField(default=True, help_text="Se este campo for marcado, as Linhas do Sub Produto deverão ser alocadas para uma TAG única.")
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    
class LinhaSubProdutoAgregado(models.Model):
    ''' linha com os subprodutos e suas quantidades agregadas'''
    
    class Meta:
        verbose_name = "Linha Sub Produto Agregado"
        verbose_name_plural = "Linha de Sub Produtos Agregados"
    
    
    quantidade = models.IntegerField(help_text="Numero Inteiro", blank=True, null=True, default=0)
    subproduto_principal = models.ForeignKey('SubProduto', related_name="linhasubprodutos_agregados")
    subproduto_agregado = models.ForeignKey('SubProduto', related_name="linhasubproutos_escolhidos")

class LinhaSubProduto(models.Model):
    '''
    Modelo de Objeto
    '''
    
    def __unicode__(self):
        return u"Linha %s de SubProduto %s" % (self.peso, self.subproduto)
    
    class Meta:
        verbose_name = "Linha de Componentes do Sub Produto"
        verbose_name_plural = "Linhas de Componentes do Sub Produto"
    
    def clean(self, exclude=None):
        if self.subproduto.possui_tags:
            # subproduto tagueavel
            linha_igual = LinhaSubProduto.objects.filter(tag=self.tag, subproduto=self.subproduto)
            if linha_igual and linha_igual [0] != self:
                raise ValidationError('Erro! Já existe uma Linha de Sub Produto com essa TAG!')

    peso = models.IntegerField(blank=True, null=True)
    subproduto = models.ForeignKey('SubProduto')
    tag = models.CharField(blank=True, max_length=100)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

class OpcaoLinhaSubProduto(models.Model):

    class Meta:
        verbose_name = u"Opção para a Linha do SubProduto"
        unique_together = (('linha', 'padrao'))
    
    linha = models.ForeignKey('LinhaSubProduto')
    componente = models.ForeignKey('Componente')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    padrao = models.NullBooleanField(default=False)
    
def subproduto_local_documentos(instance, filename):
    return os.path.join(
        'subproduto/', str(instance.subproduto.id), 'documento', str(instance.id), filename
      )

class DocumentoTecnicoSubProduto(models.Model):
    
    class Meta:
        verbose_name = u"Documento Técnico do Sub Produto"
        verbose_name_plural = u"Documentos Técnicos do Sub Produto"
    
    subproduto = models.ForeignKey('SubProduto')
    titulo = models.CharField(blank=True, max_length=100)
    descricao = models.TextField(blank=True)
    arquivo = models.FileField(upload_to=subproduto_local_documentos)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    

class ProdutoFinal(models.Model):
    
    def __unicode__(self):
        pn_prepend = getattr(settings, 'PN_PREPEND', 'PN')
        return "%s-PRO%s %s" % (pn_prepend, "%05d" % self.id, self.nome)
    
    imagem = models.ImageField(upload_to=subproduto_local_imagem, blank=True, null=True)
    nome = models.CharField(blank=True, max_length=100)
    descricao = models.TextField(blank=True)
    
    subprodutos = models.ManyToManyField('SubProduto')
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    

class LinhaProdutoAvulso(models.Model):
    
    class Meta:
        verbose_name = "Linha de Componente Avulso do Produto"
        verbose_name_plural = "Linhas de Componentes Avulsos do Produto"
    
    produto = models.ForeignKey('ProdutoFinal')
    componente = models.ForeignKey('Componente')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    tag = models.CharField(blank=True, max_length=100)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")
    

def produto_local_documentos(instance, filename):
    return os.path.join(
        'produto/', str(instance.subproduto.id), 'documento', str(instance.id), filename
      )

class DocumentoTecnicoProduto(models.Model):
    
    class Meta:
        verbose_name = u"Documento Técnico do Sub Produto"
        verbose_name_plural = u"Documentos Técnicos do Sub Produto"
    
    produto = models.ForeignKey('ProdutoFinal')
    titulo = models.CharField(blank=True, max_length=100)
    descricao = models.TextField(blank=True)
    arquivo = models.FileField(upload_to=produto_local_documentos)
    # meta
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")