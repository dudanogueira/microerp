# -*- coding: utf-8 -*-
from django.db import models
import datetime, os
from django.conf import settings

from django.db.models import signals

from django.utils.deconstruct import deconstructible

TIPO_ARQUIVO_IMPORTACAO = (
    ('digisat', 'Arquivo de Estoque do Digisat'),
)

PRODUTO_PADRAO_CODIGO_BARRAS_CHOICES = (
    ('ean13', 'EAN13 - European Article Number'),
    ('o', 'Outros'),
)

PRODUTO_UNIDADE_DE_VENDA_CHOICES = (
    ('un', 'Unidade'),
    ('pc', 'Peça'),
    ('am', 'AM'),
    ('pct', 'Pacote'),
    ('bl', 'Bloco'),
)

PRODUTO_UNIDADE_DE_COMPRA_CHOICES = PRODUTO_UNIDADE_DE_VENDA_CHOICES


PRODUTO_TRIBUTACAO_CHOICES = (
    ('i', 'Isento'),
    ('s', 'Substituição Tributária'),
    ('n', 'Normal'),
)

class PerfilAcessoEstoque(models.Model):
    '''Perfil de Acesso ao Comercial'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso ao Estoque"
        verbose_name_plural = u"Perfis de Acesso ao Estoque"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class TipoDeProduto(models.Model):
    
    def __unicode__(self):
        return self.nome

    nome = models.CharField(blank=True, max_length=100)
    # meta
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class Produto(models.Model):
    
    def __unicode__(self):
        return "%s - %s" % (self.codigo, self.descricao)
    
    def calcular_preco_venda(self, percentual=0):
        if percentual == 0 or None:
            return self.preco_custo
        else:
            percentual = float(self.preco_custo) * float(percentual) / float(100)
            soma = float(self.preco_custo) + float(percentual)
            return soma

    def unidade(self):
        return self.unidade_de_venda or self.unidade_de_compra
    
    def get_unidade_display(self):
        return self.get_unidade_de_venda_display() or self.get_unidade_de_compra_display()

    codigo = models.CharField(blank=False, max_length=500)
    nome = models.CharField(blank=False, max_length=300)
    descricao = models.CharField(blank=False, max_length=300)
    ativo = models.BooleanField(default=True)
    unidade_de_venda = models.CharField(blank=True, max_length=100, choices=PRODUTO_UNIDADE_DE_VENDA_CHOICES, null=True, default='un')
    unidade_de_compra = models.CharField(blank=True, max_length=100, choices=PRODUTO_UNIDADE_DE_VENDA_CHOICES, null=True, default='un')
    fator = models.CharField(blank=True, null=True, max_length=100)
    quantidade_em_estoque = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    preco_consumo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    # fk
    tipo = models.ForeignKey('TipoDeProduto', blank=True, null=True)
    tabela = models.ForeignKey('TabelaDePreco', blank=True, null=True)
    # fiscais e tributarios
    ncm = models.IntegerField(blank=True, null=True)
    tributacao = models.CharField(blank=True, max_length=100, choices=PRODUTO_TRIBUTACAO_CHOICES)
    substituicao_tributaria_valor = models.IntegerField(blank=False, null=False, default=0)
    icms = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    # indicadores de comercial
    grupo_indicador = models.ForeignKey('comercial.GrupoIndicadorDeProdutoProposto', blank=True, null=True)
    sub_grupo_indicador = models.ManyToManyField('comercial.SubGrupoIndicadorDeProdutoProposto', blank=True, null=True)
    # meta
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class CodigoDeBarra(models.Model):
    codigo_barras = models.CharField(blank=True, max_length=100)
    padrao_codigo_de_barras = models.CharField(blank=True, max_length=100, choices=PRODUTO_PADRAO_CODIGO_BARRAS_CHOICES)
    produto = models.ForeignKey('Produto')

class TabelaDePreco(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)
    percentual = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    # meta
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")


@deconstructible
class ArquivoImportacaoDir(object):

    def __call__(self, instance, filename):
        return os.path.join(
             'arquivo-importacao-produtos/', str(instance.tipo), datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), filename
             )

arquivo_importacao_dir = ArquivoImportacaoDir()

class ArquivoImportacaoProdutos(models.Model):
    
    class Meta:
        ordering = ('criado',)
    
    importado = models.BooleanField(default=False)
    importado_em = models.DateTimeField(blank=True, null=True)
    tipo = models.CharField(blank=False, max_length=100, choices=TIPO_ARQUIVO_IMPORTACAO)
    arquivo = models.FileField(upload_to=arquivo_importacao_dir)
    # meta
    enviado_por = models.ForeignKey('rh.Funcionario')
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")
    

# SIGNALS
def atualiza_preco_produto_pela_tabela(signal, instance, sender, **kwargs):
    '''
    SINAL ENVIADO PELA TABELA QUE ATUALIZA TODOS OS PRODUTOS VINCULADOS A ELA
    aumenta o preco do produto em X% conforme a tabela de preco
    '''
    for produto in instance.produto_set.all():
        valor_porcentagem = produto.preco_custo * instance.percentual / 100
        produto.preco_venda = produto.preco_custo + valor_porcentagem
        produto.save()

# SIGNALS CONNECTION
#signals.post_save.connect(atualiza_preco_produto_pela_tabela, sender=TabelaDePreco)