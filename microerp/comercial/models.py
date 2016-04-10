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
__version__ = '2.0.0'

from django.utils.deconstruct import deconstructible
import uuid
import datetime, os, locale, decimal

from utils import extenso_com_centavos

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from django.db.models import Sum
from localflavor.br.br_states import STATE_CHOICES

from cadastro.models import Cliente, PreCliente
from rh.models import Funcionario
from django import forms

import urllib2

from django.db.models import signals, Q

from django.contrib import messages

from icalendar import Calendar, Event

from estoque.models import Produto

from localflavor.br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField

from localflavor.br.br_states import STATE_CHOICES

PROPOSTA_COMERCIAL_STATUS_CHOICES = (
    ('aberta', 'Aberta'),
    ('convertida', 'Convertida'),
    ('perdida', 'Perdida'),
    ('perdida_aguardando', 'Perdida: Aguardando Aprovação'),
)

CONTRATO_FORMA_DE_PAGAMENTO_CHOICES = (
    ('boleto', 'Boleto'),
    ('credito', u'Cartão de Crédito'),
    ('debito', u'Cartão de Débito'),
    ('dinheiro', 'Dinheiro'),
    ('cheque', 'Cheque'),
    ('transferencia', u'Transferência Bancária'),
    ('permuta', 'Permuta'),
)

CONTRATO_TIPO_CHOICES = (
    ('aberto', 'Aberto'),
    ('fechado', 'Fechado'),
    ('mensal', 'Mensal'),
)

CONTRATO_STATUS_CHOICES = (
    ('cancelado', 'Cancelado'),
    ('arquivado', 'Arquivado'),
    ('emanalise', 'Em Análise'),
    ('invalido', u'Inválido'),
    ('assinatura', u'Aguardando Assinatura'),
    ('emaberto', 'Em Aberto'),
    ('lancado', u'Contrato Lançado'),
)

CONTRATO_STATUS_DE_EXECUCAO_CHOICES = (
    ('naoiniciado', 'Não Iniciado'),
    ('comunicadoinicio', 'Início do Contrato Comunicado'),
    ('emandamento', 'Em Andamento'),
    ('pendente', 'Pendente'),
    ('finalizado', 'Finalizado'),
    ('comunicadofim', 'Fim do Contrato Comunicado'),
)


DOCUMENTO_GERADO_TIPO_CHOICES = (
    ('contrato', u'Contrato'),
    ('proposta', u'Proposta'),
)

DADO_VARIAVEL_CHOICES = (
    ('texto', 'Texto'),
    ('inteiro', u'Número  Inteiro'),
    ('decimal', u'Número Decimal'),
)
class PropostaComercial(models.Model):

    def __unicode__(self):
        return "Proposta %s" % self.pk
        if self.cliente:
            proposto = 'cliente'
            obj = self.cliente
        else:
            proposto = 'precliente'
            obj = self.precliente
        try:
            locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")
            valor_formatado = locale.currency(self.valor_proposto, grouping=True)
        except:
            valor_formatado = self.valor_proposto

        return u"Proposta #%s para %s %s de %s com %s%% de probabilidade criado por %s" % (self.id, proposto, obj, valor_formatado, self.probabilidade, self.criado_por)

    def texto_descricao_items(self):
        texto = ''
        for orcamento in self.orcamentos_ativos():
            texto += "%s\n" % orcamento.descricao
        return texto

    def expirada(self):
        if datetime.date.today() >= self.data_expiracao:
            return True
        else:
            return False

    def ultimo_followup(self):
        if self.followupdepropostacomercial_set.count():
            return self.followupdepropostacomercial_set.all().order_by('-criado')[0]
        else:
            return False

    def dono(self):
        return self.cliente or "Pré Cliente: %s" % self.precliente

    def sugere_data_reagendamento_expiracao(self):
        if self.data_expiracao > datetime.date.today():
            return self.data_expiracao + datetime.timedelta(days=getattr(settings, 'EXPIRACAO_FOLLOWUP_PADRAO', 7))
        else:
            return datetime.date.today() + datetime.timedelta(days=getattr(settings, 'EXPIRACAO_FOLLOWUP_PADRAO', 7))

    def orcamentos_ativos(self):
        return self.orcamento_set.filter(ativo=True)

    def orcamentos_inativos(self):
        return self.orcamento_set.filter(ativo=False)

    def consolidado(self):
        '''soma todos os valores de orcamentos ativos presentes
        se proposta for do tipo substitutivo, considerar logistica + menor valor
        de orcamentos
        '''
        if self.substitutivo:
            menor_valor = self.orcamento_set.filter(ativo=True).aggregate(m=models.Min('custo_total'))['m'] or 0
            soma = float(menor_valor) + self.custo_logistica_com_margem()
        else:
            soma = self.custo_logistica_com_margem() + self.custo_orcamentos_com_margem() + self.custo_tabelados() + self.custo_promocional()
        return soma or 0

    def consolidado_liquido(self):
        '''soma todos os valores de orcamentos ativos presentes'''
        soma = self.custo_logistica() + self.custo_orcamentos() + self.custo_tabelados() + self.custo_promocional()
        return soma or 0

    def contrato_id(self):
        return self.pk

    def clean(self):
        if self.status == 'convertida' and self.definido_convertido_em is None:
              raise ValidationError('Para ser convertida, uma proposta deve possuir a data de conversão.')

    def expira_hoje(self):
        if datetime.date.today() == self.data_expiracao:
            return True
        else:
            return False

    def valor_extenso(self):
        return extenso_com_centavos(str(self.valor_proposto))

    def custo_logistica(self):
        valor_custo_logistica = self.linharecursologistico_set.aggregate(Sum("custo_total"))['custo_total__sum'] or 0
        return float(valor_custo_logistica)

    def custo_logistica_com_margem(self):
        valor_custo_logistica = self.linharecursologistico_set.aggregate(Sum("custo_total"))['custo_total__sum'] or 0
        total_margem = self.taxa_margem()
        valor_margem =  (float(total_margem) * float(valor_custo_logistica)) / 100.0
        novo_valor = float(valor_custo_logistica) + float(valor_margem)
        return float(novo_valor) or 0

    def custo_orcamentos(self):
        '''valor calculado'''
        valor_custo_orcamentos = self.orcamento_set.filter(ativo=True, tabelado=False, promocao=False).aggregate(Sum("custo_total"))['custo_total__sum'] or 0
        return float(valor_custo_orcamentos) or 0

    def custo_tabelados(self):
        valor_custo_tabelados = self.orcamento_set.filter(ativo=True, tabelado=True, promocao=False).aggregate(Sum("custo_total"))['custo_total__sum'] or 0
        return float(valor_custo_tabelados) or 0

    def custo_promocional(self):
        valor_custo_promocionais = self.orcamento_set.filter(ativo=True, tabelado=False, promocao=True).aggregate(Sum("custo_total"))['custo_total__sum'] or 0
        return float(valor_custo_promocionais) or 0

    def custo_orcamentos_com_margem(self):
        valor_custo_orcamentos = self.custo_orcamentos()
        # aplica margem
        total_margem = self.taxa_margem()
        valor_margem =  (total_margem * float(valor_custo_orcamentos)) / 100.0
        novo_valor = float(valor_custo_orcamentos) + float(valor_margem)
        return float(novo_valor) or 0

    def taxa_margem(self):
        lucro = self.lucro
        administrativo = self.administrativo
        impostos = self.impostos
        total_margem = float(lucro) + float(administrativo) + float(impostos)
        return float(total_margem) or 0

    def parcelamentos_aplicados(self):
        retorno = []
        for parcelamento in self.parcelamentos_possiveis.all():
            retorno.append((parcelamento, parcelamento.aplica_no_valor( self.consolidado() ) ) )
        return retorno

    def cria_documento_gerado(self, modelo, tipo='proposta'):
        '''cria/clona um documento gerado à partir de um modelo'''
        documento = DocumentoGerado.objects.create(
            nome = 'Documento Gerado para a Proposta #%s' % self.pk,
            tipo_proposta=self.tipo,
            tipo=tipo,
            imprime_logo=modelo.imprime_logo
        )
        # clona acapa
        if modelo.capa:
            documento.capa.save(os.path.basename(modelo.capa.url),modelo.capa.file,save=True)
        # associa documento gerado com esta proposta
        self.documento_gerado = documento
        self.save()
        # clona grupos e itens
        for grupo_modelo in modelo.grupodocumento_set.all():
            grupo_novo = documento.grupodocumento_set.create(
                    peso=grupo_modelo.peso,
            )
            for item in grupo_modelo.itemgrupodocumento_set.all():
                novo_item = grupo_novo.itemgrupodocumento_set.create(
                    peso=item.peso,
                    chave_identificadora=item.chave_identificadora,
                    titulo=item.titulo,
                    texto=item.texto,
                    quebra_pagina=item.quebra_pagina,
                    texto_editavel=item.texto_editavel,
                )
                if item.imagem:
                    try:
                        novo_item.imagem.save(os.path.basename(item.imagem.url),item.imagem.file,save=True)
                    except:
                        pass
            # clona grupo de variaveis
            if modelo.grupodadosvariaveis:
                # cria grupo de dados variaveis pro documento
                grupo = GrupoDadosVariaveis.objects.create(
                    documento=documento
                )
                # copia os que estão no modelo
                for dado in modelo.grupodadosvariaveis.dadovariavel_set.all():
                    documento.grupodadosvariaveis.dadovariavel_set.create(
                        chave=dado.chave,
                        valor=dado.valor,
                        tipo=dado.tipo
                    )
        return documento

    def cria_contrato_pelo_modelo(self, modelo, responsavel, comissionado):
        # cria o documento gerado do tipo contrato
        documento_contrato = self.cria_documento_gerado(modelo=modelo, tipo='contrato')
        # cria o contratofechado
        contrato = ContratoFechado.objects.create()
        # faz vinculacoes

    cliente = models.ForeignKey('cadastro.Cliente', blank=True, null=True)
    precliente = models.ForeignKey('cadastro.PreCliente', blank=True, null=True)
    documento_gerado = models.OneToOneField('DocumentoGerado', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(blank=True, max_length=100, choices=PROPOSTA_COMERCIAL_STATUS_CHOICES, default='aberta')
    tipo = models.ForeignKey('TipoDeProposta', blank=True, null=True)
    tipos = models.ManyToManyField('TipoDeProposta', blank=True, related_name="proposta_por_tipos_set")
    substitutivo = models.BooleanField(default=False, help_text="Define se Proposta possui orçamentos substitutivos. Nesses casos, o valor mínimo será definido como o valor da menor proposta")
    probabilidade = models.IntegerField("Probabilidade (%)", blank=True, null=True, default=50)
    probabilidade_inicial = models.IntegerField("Probabilidade Inicial (%)", blank=True, null=True, default=50)
    valor_proposto = models.DecimalField(max_digits=10, decimal_places=2)
    valor_fechado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_expiracao = models.DateField("Data de Expiração desta Proposta", blank=False, null=False, default=datetime.date.today)
    designado = models.ForeignKey("rh.Funcionario", blank=True, null=True)
    reaberta = models.BooleanField(default=False)
    # porcentagens de margem
    lucro = models.IntegerField("Lucro (%)", blank=False, null=False, default=0)
    administrativo = models.IntegerField("Taxa Administrativa (%)", blank=False, null=False, default=0)
    impostos = models.IntegerField("Impostos (%)", blank=False, null=False, default=0)
    # parcelamentos selecionados
    parcelamentos_possiveis = models.ManyToManyField('TabelaDeParcelamento', verbose_name=u"Parcelamenos Possíveis", blank=True)
    # dados para impressao
    nome_do_proposto = models.CharField(blank=True, max_length=100)
    documento_do_proposto = models.CharField(blank=True, max_length=100)
    rua_do_proposto = models.CharField(blank=True, max_length=100)
    bairro_do_proposto = models.CharField(blank=True, max_length=100)
    cep_do_proposto = models.CharField(blank=True, max_length=100)
    cidade_do_proposto = models.CharField(blank=True, max_length=100)
    estado_do_proposto = models.CharField(blank=True, null=True, max_length=100, choices=STATE_CHOICES, default='MG')
    endereco_obra_proposto = models.TextField(blank=True)
    representante_legal_proposto = models.CharField(blank=True, max_length=100)
    telefone_contato_proposto = models.CharField(blank=True, max_length=100)
    email_proposto = models.CharField(blank=True, max_length=100)
    objeto_proposto = models.TextField(blank=True)
    descricao_items_proposto = models.TextField(blank=True, verbose_name=u"Descrição dos Itens Proposto")
    items_nao_incluso = models.TextField(blank=True, verbose_name=u"Itens Não Incluso")
    forma_pagamento_proposto = models.TextField(blank=True)
    garantia_proposto = models.TextField(blank=True)
    # definido perdido
    definido_perdido_por = models.ForeignKey('rh.Funcionario', verbose_name=u"Definido Como Perdido por", related_name="proposta_definida_perdido_set", blank=True, null=True)
    definido_perdido_em = models.DateTimeField(blank=True, null=True)
    definido_perdido_motivo = models.TextField(u"Motivo de Perda da Proposta", blank=True)
    definido_perdido_motivo_opcao = models.ForeignKey('MotivoFechamentoProposta', blank=True, null=True)
    # definido convertido
    definido_convertido_por = models.ForeignKey('rh.Funcionario', verbose_name=u"Definido Como Convertido por", related_name="proposta_definida_convertida_set", blank=True, null=True)
    definido_convertido_em = models.DateTimeField(blank=True, null=True)
    # contrato fechado vinculado
    contrato_vinculado = models.OneToOneField('ContratoFechado', primary_key=False, blank=True, null=True)
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="proposta_adicionada_set",  blank=True, null=True)
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class MotivoFechamentoProposta(models.Model):

    def __unicode__(self):
        return self.motivo

    motivo = models.CharField(blank=True, max_length=100)

class ClasseTipoDeProposta(models.Model):
    def __unicode__(self):
        return self.nome

    nome = models.CharField(blank=False, max_length=100)


class TipoDeProposta(models.Model):

    def __unicode__(self):
        if self.classe:
            return '%s - %s' % (self.classe.nome, self.nome)
        else:
            return self.nome

    nome = models.CharField(blank=True, max_length=100)
    classe = models.ForeignKey(ClasseTipoDeProposta, blank=True, null=True)
    tipo_contrato_mapeado = models.ForeignKey('CategoriaContratoFechado', blank=True, null=True)

class FollowUpDePropostaComercial(models.Model):

    def __unicode__(self):
        return u"Follow Up da Proposta #%s" % self.proposta.id

    def data(self):
        return self.criado

    class Meta:
        ordering = ['-criado']

    proposta = models.ForeignKey('PropostaComercial')
    texto = models.TextField(blank=False)
    reagenda_data_expiracao = models.BooleanField("Reagenda Nova Data de Expiração", default=False)
    data_expiracao = models.DateField("Data de Expiração", blank=False, default=datetime.datetime.today)
    probabilidade = models.IntegerField("Probabilidade (%)", blank=True, null=True)
    # registro de visita com followup
    visita = models.BooleanField(u"Registra Visita Comercial", default=False, help_text=u"Indica se houve visita física neste FollowUp")
    visita_por = models.ForeignKey('rh.Funcionario', related_name="followup_com_visita_set",  blank=True, null=True)
    # registro histórico
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="followup_adicionado_set",  blank=False, null=False)
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")


@deconstructible
class AssinaturaDir(object):

    def __call__(self, instance, filename):
        return os.path.join(
            'funcionarios/', str(instance.user.funcionario.uuid), 'assinaturas/', filename
          )

assinatura_local_imagem = AssinaturaDir()


class PerfilAcessoComercial(models.Model):
    '''Perfil de Acesso ao Comercial'''
    class Meta:
        verbose_name = u"Perfil de Acesso ao Comercial"
        verbose_name_plural = u"Perfis de Acesso ao Comercial"

    def funcionarios_disponiveis(self):
        '''mostra todos os funcionarios disponiveis pra este perfil
        se super gerente, mostra todos, especificando a empresa
        se gerente ou analista, mostra todos da mesma empresa'''

        if self.super_gerente:
            ids_possiveis = self._meta.model.objects.exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        else:
            ids_possiveis = self._meta.model.objects.filter(empresa=self.empresa).exclude(user__funcionario__periodo_trabalhado_corrente=None).values_list('user__funcionario__id')
        return Funcionario.objects.filter(pk__in=ids_possiveis)

    def ultimos_followups(self, quantidade=10):
        '''
        Mostra todos os followups que o perfil tem acesso
        se Super Gerente, todos de todas as empresas especificando empresa no nome funcionario
        se Gerente, todos somente da empresa comercial
        '''
        if self.super_gerente:
            # super gerente, puxa todos
            ultimos_followups = FollowUpDePropostaComercial.objects.all()

        elif self.gerente:
            # gerente puxa somente empresa
            ultimos_followups = FollowUpDePropostaComercial.objects.filter(
                #mesma empresa
                Q(proposta__designado__user__perfilacessocomercial__empresa=self.empresa)
            )
        elif not self.gerente and not self.super_gerente:
            ultimos_followups = FollowUpDePropostaComercial.objects.filter(
                # propostas designadas amim
                Q(proposta__designado=self.user.funcionario) | \
                # propostas de clientes designados a mim
                Q(proposta__cliente__designado=self.user.funcionario) | \
                # propostas de preclientes desginados a mim
                Q(proposta__precliente__designado=self.user.funcionario) | \
                # propostas, preclientes e clientes sem designacao
                Q(proposta__designado=None) | \
                Q(proposta__cliente__designado=None) & \
                Q(proposta__precliente__designado=None) & \
                Q(proposta__designado__user__perfilacessocomercial__empresa=self.empresa)

            )
        if quantidade:
            ultimos_followups = ultimos_followups[0:quantidade]
        return ultimos_followups

    def preclientes_sem_proposta(self):
        return PreCliente.objects.filter(
                propostacomercial=None,
                cliente_convertido=None,
                designado=self.user.funcionario,
                sem_interesse=False
        )

    def requisicao_de_proposta(self):
        return RequisicaoDeProposta.objects.filter(
                atendido=False,
                cliente__designado=self.user.funcionario
        )

    super_gerente = models.BooleanField("Super Gerente", default=False)
    gerente = models.BooleanField("Gerente da Empresa", default=False)
    analista = models.BooleanField(default=True)
    telefone_celular = models.CharField(blank=True, max_length=100)
    telefone_fixo = models.CharField(blank=True, max_length=100)
    imagem_assinatura = models.ImageField(upload_to=assinatura_local_imagem, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    empresa = models.ForeignKey('EmpresaComercial', blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

# EMPRESA PRINCIPAL E CREDENCIADA

@deconstructible
class LogoEmpresaDir(object):

    def __call__(self, instance, filename):
        return os.path.join(
            'empresas/', str(instance.uuid), 'logo/', filename
          )
logo_empresa_local_imagem = LogoEmpresaDir()

class EmpresaComercial(models.Model):

    def __unicode__(self):
        return self.nome_reduzido

    def logradouro_completo(self):
        string = u"%s %s %s. %s - %s, %s CEP: %s" % (self.logradouro, self.complemento, self.numero, self.bairro, self.cidade, self.estado, self.cep)
        return string

    logo = models.ImageField(upload_to=logo_empresa_local_imagem, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    nome = models.CharField(max_length=300)
    nome_reduzido = models.CharField(max_length=300)
    responsavel_legal = models.CharField(max_length=300, blank=True, null=True)
    responsavel_legal_cpf = models.CharField(max_length=300, blank=True, null=True)
    principal = models.BooleanField()
    cnpj = models.CharField(max_length=300)
    telefone_fixo = models.CharField(blank=True, null=True, max_length=100, help_text="Formato: XX-XXXX-XXXX")
    telefone_celular = models.CharField(blank=True, null=True, max_length=100)
    email = models.EmailField(blank=True, null=True)
    logradouro = models.CharField(max_length=300)
    numero = models.IntegerField()
    complemento = models.CharField(max_length=300, blank=True, null=True)
    cep = models.CharField(max_length=300)
    bairro = models.CharField(max_length=300)
    cidade = models.CharField(max_length=300)
    estado = models.CharField("Estado", max_length=100,  blank=True, null=True, choices=STATE_CHOICES)
    contas_disponiveis = models.ManyToManyField('financeiro.ContaBancaria', blank=True)

# DOCUMENTO GERADO (CONTRATO OU PROPOSTA)

@deconstructible
class ImagemDocumentoDir(object):

    def __call__(self, instance, filename):
        return os.path.join(
            'documentos_gerados/', str(instance.grupo.documento.uuid), 'imagens/', filename
          )

@deconstructible
class CapaDocumentoDir(object):
    def __call__(self, instance, filename):
        return os.path.join(
            'documentos_gerados/', str(instance .uuid), 'imagens/capa/', filename
          )

documento_local_imagem = ImagemDocumentoDir()
documento_capa = CapaDocumentoDir()

class   DocumentoGerado(models.Model):
    def __unicode__(self):
        if self.modelo:
            return u"Modelo (%s): %s" % (self.get_tipo_display(), self.nome)
        else:
            return u"%s" % self.nome

    uuid = models.UUIDField(default=uuid.uuid4)
    modelo = models.BooleanField(default=False)
    imprime_logo = models.BooleanField(default=True)
    capa = models.ImageField(upload_to=documento_capa, blank=True, null=True)
    tipo = models.CharField(blank=False, null=False, max_length=15, choices=DOCUMENTO_GERADO_TIPO_CHOICES, default='proposta')
    tipo_proposta = models.ForeignKey('TipoDeProposta', blank=True, null=True)
    nome = models.CharField(blank=True, null=True, max_length=150)
    empresa_vinculada = models.ManyToManyField(EmpresaComercial, blank=True)
    versao = models.IntegerField(default=1)

class GrupoDocumento(models.Model):

    def __unicode__(self):
        return u"Grupo %s do Documento %s" % (self.peso, self.documento)

    peso = models.IntegerField()
    documento = models.ForeignKey(DocumentoGerado)

    class Meta:
        #unique_together = (('peso', 'documento'))
        ordering = ['peso', ]

class ItemGrupoDocumento(models.Model):

    def __unicode__(self):
        return u"Chave: %s do Documento: %s" % (self.chave_identificadora, self.grupo.documento)

    def formulario(self,request=None):
        if request:
            return EditarItemGrupoDocumentoForm(request.POST, request.FILES, instance=self)
        else:
            return EditarItemGrupoDocumentoForm(instance=self)

    def titulo_label(self):
        if self.titulo:
            return self.titulo
        if self.titulo_exibir:
            return self.titulo_exibir
        else:
            return "chave: %s" % self.chave_identificadora

    peso = models.IntegerField()
    grupo = models.ForeignKey(GrupoDocumento)
    chave_identificadora = models.CharField(blank=False, null=False, max_length=30)
    titulo = models.CharField(blank=True, null=True, max_length=150, help_text=u"Título para Impressão")
    titulo_centralizado = models.BooleanField(default=False)
    titulo_exibir = models.CharField(blank=True, null=True, max_length=150, help_text=u"Caso não exista um Título para impressão, usar este")
    texto = models.TextField(blank=True, null=True)
    texto_editavel = models.BooleanField(default=False)
    possui_variavel = models.BooleanField(default=False, help_text=u"Este item possui valores que precisam ser alterados.")
    imagem = models.ImageField(upload_to=documento_local_imagem, blank=True, null=True)
    imagem_editavel = models.BooleanField(default=False)
    quebra_pagina = models.BooleanField(default=False)


    class Meta:
        #unique_together = (('peso', 'grupo'))
        ordering = ['peso', 'chave_identificadora']

class EditarItemGrupoDocumentoForm(forms.ModelForm):

    class Meta:
        fields = 'titulo', 'texto', 'imagem'
        model = ItemGrupoDocumento

# ORCAMENTO / REQUISICAO DE RECURSOS
class Orcamento(models.Model):
    '''Recurso que pode ser estoque.Produto e rh.Funcionario'''

    def __unicode__(self):
        try:
            locale.setlocale(locale.LC_ALL,"pt_BR.UTF-8")
            custo_total = locale.currency(self.custo_total, grouping=True)
        except:
            custo_total = self.custo_total
        if self.modelo:
            if self.promocao:
                return u"Promoção Modelo: %s - R$ %s" % (self.descricao, custo_total)
            elif self.tabelado:
                return u"Tabelado Modelo: %s - R$ %s" % (self.descricao, custo_total)
            else:
                return u"Modelo: %s - R$ %s" % (self.descricao, custo_total)
        else:
            if self.promocao:
                return u"Promoção: %s - R$ %s" % (self.descricao, custo_total)
            elif self.tabelado:
                return u"Tabelado: %s - R$ %s" % (self.descricao, custo_total)
            else:
                return u"Avulso: %s - R$ %s" % (self.descricao, custo_total)

    def clean(self):
        if self.promocao:
            if self.fim_promocao == None or self.inicio_promocao == None:
                raise ValidationError("Quando o Orçamento for promoção o início e fim da promoção é obrigatório.")

    def reajusta_custo(self):
        '''Atualiza o custo de todas as linhas e geral'''
        reajustou = False
        custo_total = 0
        if not self.promocao and not self.tabelado:
            # material
            for linha in self.linharecursomaterial_set.all():
                linha.custo_unitario = linha.produto.preco_venda
                custo_total = linha.produto.preco_venda * linha.quantidade
                if custo_total != linha.custo_total:
                    reajustou = True
                linha.custo_total = custo_total
                linha.save()
                custo_total += decimal.Decimal(linha.custo_total)
            # humano
            for linha in self.linharecursohumano_set.all():
                linha.custo_unitario = linha.cargo.fracao_hora_referencia
                custo_total = linha.cargo.fracao_hora_referencia * linha.quantidade
                if custo_total != linha.custo_total:
                    reajustou = True
                linha.custo_total = custo_total
                linha.save()
                custo_total += decimal.Decimal(linha.custo_total)

            self.custo_total = custo_total
            self.save()
        return reajustou

    def custo_real_total(self):
        custo = 0
        # material
        for linha in self.linharecursomaterial_set.all():
            custo += linha.quantidade * linha.produto.preco_venda
        # humano
        for linha in self.linharecursohumano_set.all():
            custo += linha.quantidade * linha.cargo.fracao_hora_referencia
        return custo

    def recalcula_custo_total(self, save=True):
        self.custo_material = self.linharecursomaterial_set.aggregate(total=Sum('custo_total'))['total'] or 0
        self.custo_humano = self.linharecursohumano_set.aggregate(total=Sum('custo_total'))['total'] or 0
        if not self.tabelado or self.promocao:
            self.custo_total = self.custo_material + self.custo_humano
        if save:
            self.save()

    def custo_material_com_margem(self):
        valor_custo_total = self.custo_material
        # aplica margem
        total_margem = self.proposta.taxa_margem()
        valor_margem =  (total_margem * float(valor_custo_total)) / 100.0
        novo_valor = float(valor_custo_total) + float(valor_margem)
        return float(novo_valor) or 0

    def custo_humano_com_margem(self):
        valor_custo_total = self.custo_humano
        # aplica margem
        total_margem = self.proposta.taxa_margem()
        valor_margem =  (total_margem * float(valor_custo_total)) / 100.0
        novo_valor = float(valor_custo_total) + float(valor_margem)
        return float(novo_valor) or 0

    def custo_total_com_margem(self):
        valor_custo_total = self.custo_total
        # aplica margem
        total_margem = self.proposta.taxa_margem()
        valor_margem =  (total_margem * float(valor_custo_total)) / 100.0
        novo_valor = float(valor_custo_total) + float(valor_margem)
        return float(novo_valor) or 0

    def interpreta_notacao(self, notacao):
        notacao = notacao.replace(' ', '')
        notacao_split = notacao.split(',')
        for item in notacao_split:
            codigo,quantidade = item.split('-')
            try:
                codigo = int(codigo)
                quantidade = float(quantidade)
                produto = Produto.objects.get(codigo=codigo)
                self.linharecursomaterial_set.create(produto=produto, quantidade=quantidade)
            except:
                raise
                pass

    def gera_notacao(self):
        retorno = []
        for linha in self.linharecursomaterial_set.all().order_by('produto__codigo'):
            node = "%s-%s" % (linha.produto.codigo, linha.quantidade)
            retorno.append(node)
        return ",".join(retorno)


    descricao = models.CharField(u"Descrição", blank=True, max_length=100)
    proposta = models.ForeignKey('PropostaComercial', blank=True, null=True)
    selecionado = models.BooleanField(default=True)
    modelo = models.BooleanField(default=False)
    # tabelado
    tabelado = models.BooleanField(default=False)
    tabelado_originario = models.ForeignKey("self", limit_choices_to={'tabelado': True}, blank=True, null=True, related_name="tabelados_originados")
    # promocao
    promocao = models.BooleanField(default=False)
    inicio_promocao = models.DateField(u"Início da Promoção", blank=True, null=True)
    fim_promocao = models.DateField(u"Fim da Promoção", blank=True, null=True)
    promocao_originaria = models.ForeignKey("self", limit_choices_to={'promocao': True}, blank=True, null=True, related_name="promocoes_originadas")
    #
    ativo = models.BooleanField(default=True)

    # custos
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_material = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    custo_humano = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # metadata
    #orcamento_modelo = models.ForeignKey(self)
    criado_por = models.ForeignKey('rh.Funcionario', related_name="orcamento_criado_set",  blank=True, null=True)
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class LinhaRecursoMaterial(models.Model):

    class Meta:
        ordering = (('produto__codigo'),)


    orcamento = models.ForeignKey('Orcamento')
    produto = models.ForeignKey('estoque.Produto')
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,  default=0)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class LinhaRecursoHumano(models.Model):
    orcamento = models.ForeignKey('Orcamento')
    cargo = models.ForeignKey('rh.Cargo')
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    quantidade = models.IntegerField(blank=False, null=False, verbose_name="Quantidade de Horas")
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class TipoRecursoLogistico(models.Model):

    def __unicode__(self):
        return self.nome

    nome = models.CharField(blank=True, max_length=100)

class LinhaRecursoLogistico(models.Model):
    proposta = models.ForeignKey('PropostaComercial')
    tipo = models.ForeignKey(TipoRecursoLogistico)
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, default=0)
    descricao = models.TextField(blank=True)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class TabelaDeParcelamento(models.Model):

    def __unicode__(self):
        if self.parcelas == 1:
            return u"À vista"
        elif self.entrada == 0:
            return "%sX" % (self.parcelas)
        else:
            return "Entrada de %s%% + %sX" % (self.entrada, self.parcelas)

    class Meta:
        ordering = (['parcelas',])

    def clean(self):
        if self.parcelas == 1 and self.entrada != 0:
            raise ValidationError(u"Erro! Quando for 1 parcela somente, não poderá ter entrada.")

    def aplica_no_valor(self, valor):
        # a vista
        retorno = valor
        margem_inversa = 1 - float(self.juros) / 100
        retorno = float(valor) / float(margem_inversa)
        return "%.2f" % retorno

    parcelas = models.IntegerField(blank=False, null=False)
    juros = models.DecimalField(max_digits=3, decimal_places=2, blank=False, null=False, default=0)
    entrada = models.IntegerField(blank=False, null=False, default=0, verbose_name=u"Entrada (%)")

class CategoriaContratoFechado(models.Model):

    def __unicode__(self):
        return self.nome
    nome = models.CharField(blank=True, max_length=200)

class ContratoFechado(models.Model):

    def ultimo_followup(self):
        return self.followupdecontrato_set.last()


    def lancamentos_abertos(self):
        return self.lancamentofinanceiroreceber_set.filter(situacao='a')

    def sugere_texto_lancamentos_abertos(self, adiciona_total=True):
        textos = []
        for lancamento in self.lancamentos_abertos():
            if lancamento.observacao_recebido:
                textos.append(u"Parcela %s, no Valor de %s, na Data de %s do Tipo: %s. Observação: %s" % \
                             (
                                 lancamento.peso,
                                 lancamento.valor_cobrado,
                                 lancamento.data_cobranca,
                                 lancamento.get_modo_recebido_display(),
                                 lancamento.observacao_recebido
                            )
                        )
            else:
                textos.append(u"Parcela %s, no Valor de %s, na Data de %s do Tipo: %s." % \
                         (
                             lancamento.peso,
                             lancamento.valor_cobrado,
                             lancamento.data_cobranca,
                             lancamento.get_modo_recebido_display(),
                        )
                    )
        if adiciona_total:
            textos.append("Valor Total: %s (%s)" % (self.valor, self.valor_extenso()))
        return "\n".join(textos)

    def proposta_id(self):
        return self.propostacomercial.id

    def lancar(self, request=None):
        '''lancar o contrato'''
        if self.status  == 'emaberto':
            # lanca o contrato, vinculando X lancamentos mensais do valor_total do contrato à partir da data de inicio da cobranca
            # valor da parcela
            try:
                # verifica se tem entrada
                if self.valor_entrada != 0:
                    # cria lancamento de entrada
                    lancamento = self.lancamentofinanceiroreceber_set.create(valor_cobrado=self.valor_entrada, peso=0, data_cobranca=datetime.date.today(), modo_recebido=self.forma_pagamento)
                    if request:
                        messages.info(request, u"Sucesso! Lançamento de Entrada para o contrato #%s, valor %s em %s" % (self.pk, self.valor_entrada, lancamento.data_cobranca.strftime("%d/%m/%y")))
                valor_parcela = (self.valor - self.valor_entrada) / self.parcelas
                for peso_parcela in range(1, self.parcelas+1):
                    data_cobranca = self.inicio_cobranca + datetime.timedelta(days=30) * peso_parcela
                    self.lancamentofinanceiroreceber_set.create(valor_cobrado=valor_parcela, peso=peso_parcela, data_cobranca=data_cobranca, modo_recebido=self.forma_pagamento)
                    if request:
                        messages.info(request, u"Sucesso! Lançamento para o contrato #%s, Parcela %s, valor %s, no dia %s realizado" % (self.pk, peso_parcela, valor_parcela, data_cobranca.strftime("%d/%m/%y")))
                # fecha o contrato
                self.status = 'lancado'
                self.concluido = True
                self.save()
            except:
                raise

    def proximo_peso_lancamento(self):
        try:
            ultimo_peso = self.lancamentofinanceiroreceber_set.order_by('-peso')[0].peso
        except:
            ultimo_peso = 0
        proximo_peso = int(ultimo_peso) + 1
        return proximo_peso

    def __unicode__(self):
        return u"Contrato #%d  com %s do tipo %s no valor %s (%dx) a começar no dia %s. Situação: %s. Categoria: %s. Responsável: %s, Comissionado: %s" % \
            (self.id, self.cliente, self.get_tipo_display(), self.valor, self.parcelas, self.previsao_inicio_execucao, self.get_status_display(), self.categoria, self.responsavel, self.responsavel_comissionado)

    def total_valor_cobrado_lancamentos(self):
        return self.lancamentofinanceiroreceber_set.all().aggregate(Sum('valor_cobrado'))

    def total_valor_recebido_lancamentos(self):
        return self.lancamentofinanceiroreceber_set.all().aggregate(Sum('valor_recebido'))

    def ultimo_lancamento(self):
        try:
            ultimo_lancamento = self.lancamentofinanceiroreceber_set.all().order_by('-criado')[0]
        except:
            ultimo_lancamento = None
        return ultimo_lancamento

    def sugerir_texto_contratante(self):
        if self.cliente.tipo == "pj":
            texto = u'''%s, CNPJ %s, Representante Legal: %s, Documento do Representante: %s, endereço %s, Telefone Fixo: %s, Telefone Fixo: %s, Email: %s''' % (
                unicode(self.cliente.nome),
                unicode(self.cliente.cnpj or "CNPJ: "+("_" * 30) ),
                unicode(self.nome_proposto_legal or "Representante Legal: "+("_" * 30) ),
                unicode(self.documento_proposto_legal or "Documento Representante Legal (CPF): "+("_" * 30) ),
                unicode(self.cliente.logradouro_completo() or u"Endereço: "+("_" * 30)),
                unicode(self.cliente.telefone_fixo or ("_" * 30)),
                unicode(self.cliente.telefone_celular or ("_" * 30)),
                unicode(self.cliente.email or ("_" * 30)),
            )
        else:
            #self.cliente.tipo =="pf"
            texto = u'''%s, CPF: %s, RG nº %s, residente e domiciliado no endereço %s, Telefone Fixo: %s, Telefone Celular: %s, Email: %s''' % (

                unicode(self.cliente.nome),
                unicode(self.cliente.cpf or "_" * 30 ),
                unicode(self.cliente.rg or "_" * 30  ),
                unicode(self.cliente.logradouro_completo() or "_" * 90),
                unicode(self.cliente.telefone_fixo or ("_" * 30)),
                unicode(self.cliente.telefone_celular or ("_" * 30)),
                unicode(self.cliente.email or ("_" * 30)),
            )
        return texto

    def sugerir_texto_contratado(self, empresa=None):
        if not empresa:
            # puxar vinculado do usuário
            try:
                empresa = self.responsavel.user.perfilacessocomercial.empresa
            except EmpresaComercial.DoesNotExist:
                return None

        texto = u'''%s, CNPJ %s, Representante Legal: %s, Documento do Representante: %s, endereço %s, Telefone Fixo: %s, Telefone Fixo: %s, Email: %s''' % (
            unicode(empresa.nome),
            unicode(empresa.cnpj or "CNPJ: "+("_" * 30) ),
            unicode(empresa.responsavel_legal or "Representante Legal: "+("_" * 30) ),
            unicode(empresa.responsavel_legal_cpf or "Documento Representante Legal (CPF): "+("_" * 30) ),
            unicode(empresa.logradouro_completo() or u"Endereço: "+("_" * 30)),
            unicode(empresa.telefone_fixo or ("_" * 30)),
            unicode(empresa.telefone_celular or ("_" * 30)),
            unicode(empresa.email or ("_" * 30)),
            )
        return texto

    def form_configurar_impressao_contrato(self):
        from views import ConfigurarImpressaoContrato
        form = ConfigurarImpressaoContrato(contrato=self)
        return form

    def valor_extenso(self):
        return extenso_com_centavos(str(self.valor))

    def gera_ordem_de_servico(self):
        '''Methodo que deve ser chamado quando converter um contrato
        ele pega os orcamentos e converte em lista de materiais,
        matendo os registros de documento originário, à partir de uma ordem de servicos
        '''
        # verifica se contrato já possui ordem de serviço,
        # afinal só pode haver uma por contrato
        if not self.ordemdeservico_set.all():
            ordem_de_servico = self.ordemdeservico_set.create(
                cliente=self.cliente, valor=self.valor,
            )
            for orcamento in self.propostacomercial.orcamentos_ativos():
                # para cada orcamento
                lista_material_contrato = ordem_de_servico.listamaterialdocontrato_set.create(orcamento=orcamento)
                for linha in orcamento.linharecursomaterial_set.all():
                    # para cada material no orcamento
                    lista_material_contrato.linhalistamaterial_set.create(
                        produto=linha.produto, quantidade_requisitada=linha.quantidade
                    )

    def cria_documento_gerado(self, modelo, tipo='contrato'):
        '''cria/clona um documento gerado à partir de um modelo'''
        documento = DocumentoGerado.objects.create(
            nome = u'Documento Gerado para o Contrato #%s' % self.pk,
            tipo_proposta=self.propostacomercial.tipo,
            tipo=tipo,
            imprime_logo=modelo.imprime_logo
        )
        # clona acapa
        if modelo.capa:
            documento.capa.save(os.path.basename(documento.capa.url),documento.capa.file,save=True)
        # associa documento gerado com esta proposta
        self.documento_gerado = documento
        self.save()
        # clona grupos e itens
        for grupo_modelo in modelo.grupodocumento_set.all():
            grupo_novo = documento.grupodocumento_set.create(
                peso=grupo_modelo.peso,
            )
            for item in grupo_modelo.itemgrupodocumento_set.all():
                novo_item = grupo_novo.itemgrupodocumento_set.create(
                    peso=item.peso,
                    chave_identificadora=item.chave_identificadora,
                    titulo=item.titulo,
                    titulo_exibir=item.titulo_exibir,
                    titulo_centralizado=item.titulo_centralizado,
                    texto=item.texto,
                    quebra_pagina=item.quebra_pagina,
                    texto_editavel=item.texto_editavel,
                )
                if item.imagem:
                    novo_item.imagem.save(os.path.basename(item.imagem.url),item.imagem.file,save=True)
        # clona grupo de variaveis
        if (hasattr(self.propostacomercial.documento_gerado, 'grupodadosvariaveis')):
            # cria grupo de dados variaveis pro documento
            grupo = GrupoDadosVariaveis.objects.create(
                documento=documento
            )
            # copia os que estão na proposta
            for dado in self.propostacomercial.documento_gerado.grupodadosvariaveis.dadovariavel_set.all():
                documento.grupodadosvariaveis.dadovariavel_set.create(
                    chave=dado.chave,
                    valor=dado.valor,
                    tipo=dado.tipo,
                )


    def gera_texto_lancamentos(self):
        pass

    cliente = models.ForeignKey('cadastro.Cliente')
    tipo = models.ForeignKey('TipodeContratoFechado', blank=True, null=True)
    documento_gerado = models.OneToOneField(DocumentoGerado, blank=True, null=True, on_delete=models.SET_NULL)
    categoria = models.ForeignKey('CategoriaContratoFechado', blank=True, null=True)
    objeto = models.TextField(blank=False)
    nome_proposto_legal = models.CharField(blank=True, max_length=100)
    endereco_obra = models.TextField(u"Endereço da Obra", blank=True, null=True)
    documento_proposto_legal = models.CharField("Documento Legal do Proposto (CPF)", blank=True, max_length=100)
    garantia = models.TextField(blank=True)
    items_incluso = models.TextField("Itens Incluso", blank=True)
    items_nao_incluso = models.TextField("Itens Não Incluso", blank=True)
    forma_pagamento = models.CharField("Forma de Pagamento", blank=False, null=False, max_length=100, default="dinheiro", choices=CONTRATO_FORMA_DE_PAGAMENTO_CHOICES)
    normas_execucao = models.TextField("Normas de Execução", blank=True, null=True)
    prazo_execucao = models.TextField("Prazos de Execução", blank=True, null=True)
    rescisao = models.TextField("Rescisão", blank=True, null=True)
    foro = models.TextField("Foro", blank=True, null=True)
    conta_transferencia = models.ForeignKey('financeiro.ContaBancaria', blank=True, null=True)
    parcelas = models.IntegerField("Quantidade de Parcelas", blank=False, null=False, default=1)
    inicio_cobranca = models.DateField(u"Início da Cobrança", default=datetime.datetime.today)
    valor = models.DecimalField("Valor do Contrato", max_digits=10, decimal_places=2)
    valor_entrada = models.DecimalField("Valor de Entrada", max_digits=10, decimal_places=2, default=0)
    receber_apos_conclusao = models.BooleanField("Receber após a conclusão do Contrato", default=False)
    tipo = models.CharField(blank=False, max_length=100, default="fechado", choices=CONTRATO_TIPO_CHOICES)
    status = models.CharField(u"Status/Situação do Contrato", blank=False, max_length=100, default="emaberto", choices=CONTRATO_STATUS_CHOICES)
    # programacao
    status_execucao = models.CharField(u"Status da Execução do Contrato", blank=False, max_length=100, default="naoiniciado", choices=CONTRATO_STATUS_DE_EXECUCAO_CHOICES)
    porcentagem_execucao = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    termo_de_entrega_recebido = models.BooleanField(default=False)
    numero_termo_de_entrega = models.CharField(blank=True, max_length=100)
    aguardando_cliente = models.BooleanField(default=False)
    data_aguardando_cliente = models.DateTimeField(blank=True, null=True)
    data_marcado_emandamento = models.DateTimeField(blank=True, null=True)
    data_marcado_pendente = models.DateTimeField(blank=True, null=True)
    data_marcado_retorno_cliente = models.DateTimeField(blank=True, null=True)
    data_marcado_finalizado = models.DateTimeField(blank=True, null=True)
    previsao_inicio_execucao = models.DateField(default=datetime.datetime.today)
    previsao_termino_execucao = models.DateField(blank=True, null=True)
    efetivo_inicio_execucao = models.DateField(default=datetime.datetime.today)
    efetivo_termino_execucao = models.DateField(blank=True, null=True)
    funcionarios_participantes = models.ManyToManyField('rh.Funcionario', related_name="contratos_participados", blank=True)
    apoio_tecnico = models.ForeignKey('rh.Funcionario', related_name="contratos_apoio_tecnico", blank=True, null=True, verbose_name=u"Apoio Técnico")
    #
    concluido = models.BooleanField(default=False)
    responsavel = models.ForeignKey('rh.Funcionario', verbose_name=u"Responsável pelo Contrato")
    responsavel_comissionado = models.ForeignKey('rh.Funcionario', blank=True, null=True, verbose_name=u"Responsável Comissionado", related_name="contrato_comissionado_set")
    motivo_invalido = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    # Datas
    data_validacao = models.DateTimeField(blank=True, null=True)
    data_assinatura = models.DateTimeField(blank=True, null=True)
    funcionario_validador = models.ForeignKey('rh.Funcionario', verbose_name=u"Funcionário que Validou", related_name="contrato_validado_set", blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class TipodeContratoFechado(models.Model):
    nome = models.CharField(blank=True, max_length=100)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class FechamentoDeComissao(models.Model):

    def valor_total(self):
        return self.contratos.exclude(status="cancelado").aggregate(Sum('valor'))['valor__sum'] or 0

    def comissao_tabelada(self, valor=None):
        if valor == None:
            valor = self.valor_total()
        try:
            comissao = TabelaDeComissao.objects.filter(valor_inicio__lte=valor, valor_fim__gte=valor)[0].porcentagem
        except:
            comissao = 0
        return comissao

    def comissao_calculada(self):
        valor = self.valor_total()
        valor_calculado = (valor * self.comissao_tabelada(valor)) / 100
        return valor_calculado

    comissionado = models.ForeignKey('rh.Funcionario', blank=True, null=True, verbose_name=u"Responsável Comissionado", related_name="fechamento_comissao__set")
    contratos = models.ManyToManyField('ContratoFechado', blank=False)
    # metadata
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")
    criado_por = models.ForeignKey('rh.Funcionario',  blank=True, null=True, related_name="fechamento_comissao_criado_set")

class LancamentoDeFechamentoComissao(models.Model):
    fechamento = models.ForeignKey('FechamentoDeComissao')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    pago = models.BooleanField(default=False)

class TabelaDeComissao(models.Model):
    valor_inicio = models.DecimalField(max_digits=10, decimal_places=2)
    valor_fim = models.DecimalField(max_digits=10, decimal_places=2)
    porcentagem = models.DecimalField(max_digits=10, decimal_places=2)

class RequisicaoDeProposta(models.Model):

    def __unicode__(self):
        if self.atendido:
            return u"Requisição de Proposta ATENDIDO para %s" % self.cliente
        else:
            return u"Requisição de Proposta ABERTA para %s" % self.cliente

    cliente = models.ForeignKey('cadastro.Cliente')
    descricao = models.TextField(blank=False)
    atendido = models.BooleanField(default=False)
    atendido_data = models.DateTimeField(blank=True, null=True)
    atendido_por = models.ForeignKey("rh.Funcionario", blank=True, null=True, related_name="requisicao_proposta_atendida")
    proposta_vinculada = models.ForeignKey('PropostaComercial', blank=True, null=True)
    # metadata
    criado_por = models.ForeignKey('rh.Funcionario', related_name="proposta_requisitada_set",  blank=True, null=True)
    criado = models.DateTimeField(blank=True, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, auto_now=True, verbose_name="Atualizado")

class GrupoIndicadorDeProdutoProposto(models.Model):
    '''Esse modelo se é vinculada por cada produto para se calcular os indicadores de produtos vendidos'''

    def __unicode__(self):
        return self.nome

    nome = models.CharField(blank=False, max_length=100)

class SubGrupoIndicadorDeProdutoProposto(models.Model):
    '''Esse modelo se é vinculada por cada produto para se calcular os indicadores de produtos vendidos'''

    def __unicode__(self):
        return "%s - %s" % (self.grupo, self.nome)

    nome = models.CharField(blank=True, max_length=100)
    grupo = models.ForeignKey('GrupoIndicadorDeProdutoProposto')

# grupo de dados variaveis

class GrupoDadosVariaveis(models.Model):

    documento = models.OneToOneField('DocumentoGerado', blank=True, null=True)

class DadoVariavel(models.Model):

    def clean(self):
        if self.valor and self.tipo == 'inteiro' and not self.valor.isdigit():
            raise ValidationError(u"Erro! Deve ser um Inteiro válido")
        if self.valor and self.tipo == 'decimal':
            try:
                f = float(self.valor)
            except:
                raise ValidationError(u"Erro! Deve ser um Decimal Válido")

    grupo = models.ForeignKey(GrupoDadosVariaveis)
    chave = models.CharField(blank=False, max_length=100)
    valor = models.TextField(blank=True, null=True)
    tipo = models.CharField(blank=True, max_length=100, choices=DADO_VARIAVEL_CHOICES, default="texto ")

# signals
def proposta_comercial_post_save(signal, instance, sender, **kwargs):
      ''' Atualiza os campos da Proposta Comercial após criacao'''
      # somente criados
      if not kwargs.get('created'):
              return False

      instance.probabilidade_inicial = instance.probabilidade
      instance.save()

def follow_up_post_save(signal, instance, sender, **kwargs):
    '''Após criar o o FollowUp, atualizar a data de exibicao da proposta se marcado como tal
        e a probabilidade'''

    # somente criados
    if not kwargs.get('created'):
            return False

    if instance.reagenda_data_expiracao:
        instance.proposta.data_expiracao = instance.data_expiracao
    if instance.probabilidade:
        instance.proposta.probabilidade = instance.probabilidade
    else:
        instance.probabilidade = instance.proposta.probabilidade
    instance.proposta.save()

def atualiza_preco_linhas_material(signal, instance, sender, **kwargs):
    '''atualiza o preco das linhas de orcamento'''
    recalcula = True
    # quando não tem proposta, é modelo (promocao, modelo livre, tabelado)
    # nesses casos, não pode calcular automático
    if instance.orcamento.proposta == None:
        if instance.orcamento.promocao or instance.orcamento.tabelado:
            recalcula = False
        else:
            recalcula = True
    else:
        recalcula=True
    if recalcula:
        try:
            obj = LinhaRecursoMaterial.objects.get(pk=instance.pk)
        except LinhaRecursoMaterial.DoesNotExist:
            instance.custo_unitario = instance.produto.preco_venda
        else:
            if not obj.produto == instance.produto: # Field has changed
                instance.custo_unitario = instance.produto.preco_venda

        if instance.quantidade and instance.custo_unitario:
            resultado = float(instance.custo_unitario) * float(instance.quantidade)
        else:
            resultado = 0
        instance.custo_total = resultado

def atualiza_preco_linhas_humano(signal, instance, sender, **kwargs):
    '''atualiza o preco das linhas de orcamento'''
    # se for promocao ou modelo o preco pode ser definido
    recalcula = True
    # quando não tem proposta, é modelo (promocao, modelo livre, tabelado)
    # nesses casos, não pode calcular automático
    if instance.orcamento.proposta == None:
        if instance.orcamento.promocao or instance.orcamento.tabelado:
            recalcula = False
        else:
            recalcula = True
    else:
        recalcula=True
    if recalcula:
        try:
            obj = LinhaRecursoHumano.objects.get(pk=instance.pk)
            instance.custo_unitario = instance.cargo.fracao_hora_referencia
        except LinhaRecursoHumano.DoesNotExist:
            instance.custo_unitario = instance.cargo.fracao_hora_referencia
        else:
            if not obj.cargo == instance.cargo: # Field has changed
                instance.custo_unitario = instance.cargo.fracao_hora_referencia

        if instance.quantidade and instance.cargo.fracao_hora_referencia:
            resultado = instance.cargo.fracao_hora_referencia * instance.quantidade
        else:
            resultado = 0
        instance.custo_total = resultado

def atualiza_custo_total_orcamento(signal, instance, sender, **kwargs):
    instance.recalcula_custo_total(save=False)

def atualiza_preco_orcamento_pela_linha(signal, instance, sender, **kwargs):
    try:
        instance.orcamento.recalcula_custo_total(save=True)
    except:
        pass

def proposta_comercial_pre_save(signal, instance, sender, **kwargs):
    '''puxa a configuracao de margem da proposta baseando no settings'''
    instance.lucro = getattr(settings, 'LUCRO', 0)
    instance.administrativo = getattr(settings, 'ADMINISTRATIVO', 0)
    instance.impostos = getattr(settings, 'IMPOSTOS', 0)

def orcamento_post_save(signal, instance, sender, **kwargs):
    '''confere se, apos salvar o orcamento, o preco minimo da proposta é menor que o preço proposta
        caso seja, definir automaticamente o valor proposto para o mínimo
    '''
    if instance.proposta:
        if float(instance.proposta.consolidado()) > float(instance.proposta.valor_proposto):
            instance.proposta.valor_proposto = float(instance.proposta.consolidado())
            instance.proposta.save()

def grupo_dados_variaveis_post_save(signal, instance, sender, **kwargs):
    '''Após atualizar os dados variaveis, ou após algum calculo, chama
        o que for necessario para realizar calculos automarizados
    '''
    # calculo restscreen
    pass
    try:
        # resgata campos
        media = instance.dadovariavel_set.get(chave='retscreen_media')
        tamanho_placa = instance.dadovariavel_set.get(chave='retscreen_tamanho_placa')
        radiacao = instance.dadovariavel_set.get(chave='retscreen_radiacao')
        media_diaria = instance.dadovariavel_set.get(chave='retscreen_media_diaria')
        percentual_perda = instance.dadovariavel_set.get(chave='retscreen_percentual_perda')
        perda = instance.dadovariavel_set.get(chave='retscreen_perda')
        radiacao_real = instance.dadovariavel_set.get(chave='retscreen_radiacao_real')
        tamanho_usina = instance.dadovariavel_set.get(chave='retscreen_tamanho_usina')
        numero_placas_sugerida = instance.dadovariavel_set.get(chave='retscreen_numero_placas_sugerida')
        area_usina = instance.dadovariavel_set.get(chave='retscreen_area_usina')
        # calculos
        media_diaria.valor = float(media.valor) / 30.0
        media_diaria.save()
        percentual_perda.valor = (float(radiacao.valor) * 3) / 100
        percentual_perda.save()
        perda.valor = float(radiacao.valor) * float(percentual_perda.valor)
        perda.save()
        radiacao_real.valor = float(radiacao.valor) - float(perda.valor)
        radiacao_real.save()
        tamanho_usina.valor = float(media_diaria.valor) / float(radiacao_real.valor)
        tamanho_usina.save()
        numero_placas_sugerida.valor = float(tamanho_usina.valor) / float(tamanho_placa.valor)
        numero_placas_sugerida.save()
        area_usina.valor = float(numero_placas_sugerida.valor) * 1.68
        area_usina.save()
    #except instance.dadovariavel_set.model.DoesNotExist:
    except:
        pass


# SIGNALS CONNECTION
signals.pre_save.connect(proposta_comercial_pre_save, sender=PropostaComercial)
signals.post_save.connect(proposta_comercial_post_save, sender=PropostaComercial)
signals.post_save.connect(follow_up_post_save, sender=FollowUpDePropostaComercial)
# RECURSO MATERIAL
signals.pre_save.connect(atualiza_preco_linhas_material, sender=LinhaRecursoMaterial)
signals.post_save.connect(atualiza_preco_orcamento_pela_linha, sender=LinhaRecursoMaterial)
signals.post_delete.connect(atualiza_preco_orcamento_pela_linha, sender=LinhaRecursoMaterial)
# RECURSO HUMANO
signals.pre_save.connect(atualiza_preco_linhas_humano, sender=LinhaRecursoHumano)
signals.post_save.connect(atualiza_preco_orcamento_pela_linha, sender=LinhaRecursoHumano)
signals.post_delete.connect(atualiza_preco_orcamento_pela_linha, sender=LinhaRecursoHumano)
# RECURSO LOGISTICO
signals.post_save.connect(orcamento_post_save, sender=LinhaRecursoLogistico)
# OUTROS
signals.pre_save.connect(atualiza_custo_total_orcamento, sender=Orcamento)
signals.post_save.connect(orcamento_post_save, sender=Orcamento)
# GRUPO DADO VARIAVEL
signals.post_save.connect(grupo_dados_variaveis_post_save, sender=GrupoDadosVariaveis)
