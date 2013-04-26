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

import os, datetime
from django.db import models

from django.db.models import signals
from django.db.models import Sum

from django.contrib.sites.models import Site

from django.core.exceptions import ValidationError

from sorl.thumbnail import ImageField
from django_extensions.db.fields import UUIDField

from django.conf.global_settings import LANGUAGES

from django_localflavor_br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField
from django.conf import settings

from workdays import networkdays

from decimal import Decimal

horas_por_dia = getattr(settings, 'HORAS_TRABALHADAS_POR_DIA', 8.4)

def funcionario_avatar_img_path(instance, filename):
    return os.path.join(
        'funcionarios/', instance.uuid, 'avatar/', filename
      )

def funcionario_entrada_folha_ponto_assinada(instance, filename):
    return os.path.join(
        'funcionarios/', instance.funcionario.uuid, 'folha_de_ponto', str(instance.data_referencia.year), str(instance.data_referencia.month), 'ID-ENTRADA-%d' % instance.id, filename
    )

def funcionario_folha_ponto_assinada(instance, filename):
    return os.path.join(
        'funcionarios/', instance.folha.funcionario.uuid, 'folha_de_ponto', str(instance.folha.data_referencia.year), str(instance.folha.data_referencia.month), 'ID-FOLHA-%d' % instance.id, filename
    )

def funcionario_rotina_exame_medico(instance, filename):
    return os.path.join(
        'funcionarios/', instance.funcionario.uuid, 'exames_medicos', str(instance.id), "ID-%s-%s" % (instance.id, filename)
    )

SOLICITACAO_LICENCA_STATUS_CHOICES = (
    ('aberta', u"Aberta"),
    ('autorizada', u"Autorizada"),
    ('declinada', u"Declinada"),
)

SOLICITACAO_LICENCA_TIPO_CHOICES = (
    ('ferias', u"Férias"),
    ('medica', u"Médica"),
)

FUNCIONARIO_RESIDENCIA_CHOICES = (
    ('propria', 'Residência Própria'),
    ('aluguel', 'Residência por Aluguel'),
    ('outro', 'Outro: Casa de Parentes/Amigos'),
)

FUNCIONARIO_SEXO_CHOICES = (
    ('m', 'Masculino'),
    ('f', 'Feminino'),
)

FUNCIONARIO_ESTADO_CIVIL_CHOICES = (
    ('casado', 'Casado'),
    ('solteiro', 'Solteiro'),
    ('divorciado', 'Divorciado'),
    ('viuvo', 'Viúvo'),
    ('outros', 'Outros'),
)

IDIOMA_FUNCIONARIO_NIVEL_CHOICES = (
    ('0', 'Básico'),
    ('1', 'Intermediário'),
    ('2', 'Avançado'),
    ('3', 'Fluente'),
)

FUNCIONARIO_ESCOLARIDADE_NIVEL_CHOICES = (
    ('0', '2º Grau Incompleto'),
    ('1', '2º Grau Completo'),
    ('2', 'Ensino Superior Incompleto'),
    ('3', 'Ensino Superior Completo'),
    ('4', 'Ensino Superior Completo + Pós Graduação'),
    ('5', 'Ensino Superior Completo + Mestrado'),
    ('6', 'Ensino Superior Completo + Doutorado'),
)

ENTRADA_FOLHA_DE_PONTO_CHOICES = (
    ('entrada', 'Entrada do Funcionário'),
    ('saida', 'Saída do Funcionário'),
)

DEPENDENTE_FUNCIONARIO_CHOICES = (
    ('f', 'Filho / Filha'),
    ('p', 'Parceiro / Esposo / Esposa'),
)

ROTINA_EXAME_MEDICO_CHOICES = (
    ('a', u"Admissão"),
    ('d', u"Demissão"),
    ('u', u"Atualização"),
    ('p', u"Promoção"),
)

FUNCIONARIO_FORMA_PAGAMENTO_CHOICES = (
    ('mensal', u"Pagamento Mensal"),
)

DEMISSAO_FUNCIONARIO_CHOICES = (
    ('andamento', 'Em Andamento'),
    ('finalizado', 'Finalizado'),
)


class Funcionario(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    class Meta:
        verbose_name = u"Funcionário"
        verbose_name_plural = u"Funcionários"
        ordering = ['nome']
    
    def clean(self):
        # check telefones
        if self.telefone_fixo:
            BRPhoneNumberField().clean(self.telefone_fixo)
        if self.telefone_celular:
            BRPhoneNumberField().clean(self.telefone_celular)
        # cpf check
        try:
            if self.cpf:
                self.cpf = BRCPFField().clean(self.cpf)
        except:
            raise ValidationError(u"Número do CPF Inválido!")
    
    def salario(self):
        if self.promocaosalario_set.filter(aprovado=True).count():
            return self.promocaosalario_set.filter(aprovado=True).order_by('data')[0].valor
        else:
            return self.salario_inicial
    
    def cargo(self, update=False):
        if self.promocaocargo_set.filter(aprovado=True).count():
            return self.promocaocargo_set.all().order_by('data')[0].cargo_novo
        else:
            return self.cargo_inicial
    
    def exames_agendados(self):
        return self.rotinaexamemedico_set.filter(data__gt=datetime.date.today())

    def exames_passados(self):
        return self.rotinaexamemedico_set.filter(data__lt=datetime.date.today())

    def exames_data_indefinida(self):
        return self.rotinaexamemedico_set.filter(data=None)
    
    #
    # ferias
    #

    def ferias_situacao(self):
        dias_trabalhados = self.dias_trabalhados()
        ferias_direito = self.ferias_dias_de_direito()
        delta = int(ferias_direito) - self.ferias_dias_total_soma()
        # padrao, AMARELO "warning"
        # precisa
        #
        # VERDE "success" - nao possui férias
        # periodo trabalhado menor que 1 ano
        if int(ferias_direito) == 0:
            return "success"
        # verde porque a quantidade de ferias gozadas e agendadas está
        # igual à quantidade de ferias de direito.
        elif int(ferias_direito) == self.ferias_dias_total_soma():
            return "success"
        
        # VERMELHO "error" - alerta
        # diferença de ferias de direito com dias é maior do que 30 dias        
        elif delta > 30:
            return "error"
         
    def dias_trabalhados(self):
        dias_trabalhados = datetime.date.today() - self.periodo_trabalhado_corrente.inicio
        return dias_trabalhados.days
    
    def ferias_dias_de_direito(self):
        dias_trabalhados = self.dias_trabalhados()
        if dias_trabalhados > 365:
            # 30 dias para cada ano trabalhado
            return dias_trabalhados / 365 * 30
        else:
            return 0

    def ferias_dias_gozados(self):
        return self.solicitacaodelicenca_set.filter(tipo="ferias", status="autorizada", realizada=True)
        
    def ferias_dias_nao_gozados(self):
        return self.solicitacaodelicenca_set.filter(tipo="ferias", realizada=False)

    def ferias_dias_autorizados(self):
        return self.solicitacaodelicenca_set.filter(tipo="ferias", status='autorizada', realizada=False)

    def ferias_dias_agendados(self):
        return self.solicitacaodelicenca_set.filter(tipo="ferias", realizada=False, status="aberta")
    
    def ferias_dias_total_soma(self):
        solicitacoes = self.solicitacaodelicenca_set.filter(tipo="ferias")
        dias = []
        if solicitacoes:
            for solicitacao in solicitacoes:
                delta = solicitacao.fim - solicitacao.inicio
                dias.append(delta.days)
        else:
            dias.append(0)
        import operator
        return reduce(operator.add, dias)

    def ferias_dias_disponiveis(self):
        return self.ferias_dias_de_direito() - self.ferias_dias_total_soma()

    # BANCO DE HORAS
    def banco_de_horas_ultimo_lancamento(self):
        ultimo = EntradaFolhaDePonto.objects.filter(folha__funcionario__id=self.id).order_by('criado').all()
        if ultimo:
            return ultimo[0]
        else:
            return None
    
    def banco_de_horas_trabalhadas(self):
        retorno = EntradaFolhaDePonto.objects.filter(folha__funcionario__id=self.id).aggregate(total_trabalhado=Sum('total'))['total_trabalhado']
        return retorno or 0
    
    def banco_de_horas_esperada(self):
        if not self.periodo_trabalhado_corrente:
            return 0
        inicio = self.periodo_trabalhado_corrente.inicio
        feriados = Feriado.objects.filter(ativo=True).values('data')
        feriados_list = [feriado['data'] for feriado in feriados]
        dias = networkdays(inicio, datetime.date.today(), feriados_list)
        horas =  dias * horas_por_dia
        return horas or 0
    
    def banco_de_horas_saldo(self):
        f1 = self.banco_de_horas_trabalhadas()
        f2 = self.banco_de_horas_esperada()
        return Decimal(f1) - Decimal(f2)
    
    def banco_de_horas_situacao(self):
        saldo = Decimal(self.banco_de_horas_saldo())
        if saldo >= 0:
            return "success"
        else:
            return "error"
    
    # CONTATOS
    def destino_recado_formatado(self):
        if self.email:
            return email
        else:
            current_site = Site.objects.get()
            return "ME:%s@%s" % (self.user.username, current_site.domain)
    
    # RECADOS
    def recados_nao_lidos(self):
        return self.recado_recebido_set.filter(lido=False)
    
    def recados_lidos(self):
        return self.recado_recebido_set.filter(lido=True)
    

    uuid = UUIDField()
    foto = ImageField(upload_to=funcionario_avatar_img_path, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="Usuário do Sistema", blank=True, null=True)
    nome = models.CharField(blank=False, null=False, max_length=300, verbose_name=u"Nome do Funcionário")
    # geral / documentos / pessoal
    residencia = models.CharField(blank=True, null=True, max_length=100, choices=FUNCIONARIO_RESIDENCIA_CHOICES)
    valor_aluguel = models.DecimalField(u"Valor do Aluguel", max_digits=10, decimal_places=2, blank=True, null=True)
    nascimento = models.DateField(blank=False)
    observacao = models.TextField(blank=True, null=True)
    sexo = models.CharField(blank=True, null=True, max_length=100, choices=FUNCIONARIO_SEXO_CHOICES)
    naturalidade = models.CharField(blank=True, null=True, max_length=100)
    nacionalidade = models.CharField(blank=True, null=True,  max_length=100, default="Brasil")
    estado_civil = models.CharField(blank=True, null=True, max_length=100, choices=FUNCIONARIO_ESTADO_CIVIL_CHOICES)
    nome_companheiro = models.CharField(blank=True, null=True, max_length=300)
    nome_pai = models.CharField(u"Nome do Pai", blank=True, null=True, max_length=300)
    nome_mae = models.CharField(u"Nome da Mãe", blank=True, null=True, max_length=300)
    rg = models.CharField(blank=True, null=True, max_length=100)
    rg_data = models.DateField(u"Data de Emissão do RG", blank=True, null=True,)
    rg_expeditor = models.CharField(u"Órgão Emissor do RG", blank=True, null=True, max_length=100)
    cpf = models.CharField(u"CPF - Cadastro de Pessoa Física", blank=True, null=True, max_length=255)
    carteira_profissional_numero = models.CharField(blank=True, null=True, max_length=100)
    carteira_profissional_serie = models.CharField(blank=True, null=True,max_length=100)
    carteira_profissional_emissao = models.DateField(blank=True, null=True)
    titulo_eleitor = models.CharField(blank=True, null=True,max_length=100)
    pis = models.CharField(blank=True, null=True,max_length=100)
    certificado_reservista = models.CharField(blank=True, null=True,max_length=100)
    carteira_habilitacao_numero = models.CharField(blank=True, null=True, max_length=100)
    carteira_habilitacao_categoria = models.CharField(blank=True, null=True,max_length=100)
    carteira_habilitacao_vencimento = models.DateField(blank=True, null=True,)
    carteira_habilitacao_expedicao = models.DateField(blank=True, null=True,)
    # escolaridade
    escolaridade_nivel = models.CharField(blank=True, null=True,max_length=100, choices=FUNCIONARIO_ESCOLARIDADE_NIVEL_CHOICES)
    escolaridade_cursos = models.TextField("Cursos e Instituições",blank=True, null=True,)
    escolaridade_serie_inconclusa = models.CharField("Série máxima estudada", blank=True, null=True, max_length=100)
    escolaridade_conclusao = models.DateField("Ano de Conclusão dos estudos", blank=True, null=True, default=datetime.datetime.today)
    # contatos
    email = models.EmailField(blank=True, null=True)
    telefone_fixo = models.CharField(blank=True, null=True, max_length=100, help_text="Formato: XX-XXXX-XXXX")
    telefone_celular = models.CharField(blank=True, null=True, max_length=100)
    telefone_recado = models.TextField(blank=True, null=True, help_text="Número do telefone e contato para recados.")
    # endereco
    bairro = models.ForeignKey('cadastro.Bairro', verbose_name="Bairro, Cidade e Estado")
    cep = models.CharField(blank=True, null=True,max_length=100, verbose_name=u"CEP")
    rua = models.CharField(blank=True, null=True,max_length=500, verbose_name=u"Rua")
    numero = models.CharField(blank=True, null=True,max_length=100, verbose_name=u"Número")
    complemento = models.CharField(blank=True, null=True, max_length=200, verbose_name=u"Complemento")
    # salario
    salario_inicial = models.DecimalField(u"Salário Inicial", max_digits=10, decimal_places=2, blank=True, null=True)
    salario_atual = models.DecimalField(u"Salário Atual", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_hora = models.DecimalField(u"Valor Hora", max_digits=10, decimal_places=2, blank=True, null=True)
    forma_de_pagamento = models.CharField(blank=True, max_length=100, choices=FUNCIONARIO_FORMA_PAGAMENTO_CHOICES)
    gratificacao = models.DecimalField(u"Gratificação", max_digits=10, decimal_places=2, blank=True, null=True)
    numero_lre = models.CharField("Número LRE", blank=True, max_length=100)
    # cargo
    cargo_inicial = models.ForeignKey("Cargo", related_name="funcionario_cargo_inicial_set")
    cargo_atual = models.ForeignKey("Cargo", related_name="funcionario_cargo_atual_set", blank=True, null=True)
    funcionario_superior = models.ForeignKey("self", blank=True, null=True, verbose_name=u"Funcionário Superior", help_text=u"Funcionário a quem se reportar. Se deixado em branco, será usado o Grupo Responsável pelo Departamento", )
    local_de_trabalho = models.TextField(blank=True)
    membro_cipa = models.BooleanField(default=True)
    periodo_trabalhado_corrente = models.OneToOneField("PeriodoTrabalhado", blank=True, null=True, related_name="periodo_trabalhado_corrente")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class IdiomaFuncionario(models.Model): 
    
    class Meta:
        verbose_name = u"Idioma falado pelo Funcionário"
        verbose_name_plural = u"Idiomas falado pelo Funcionário"
    
    
    funcionario = models.ForeignKey(Funcionario)
    idioma = models.CharField(blank=True, max_length=100, choices=LANGUAGES)
    nivel = models.CharField(blank=True, max_length=100, choices=IDIOMA_FUNCIONARIO_NIVEL_CHOICES)
    instituicao = models.CharField("Instituição de Ensino do Idioma", blank=True, max_length=100)    
    # metas
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    

class CursoFuncionario(models.Model):
    
    class Meta:
        verbose_name = u"Curso Extra do Funcionário"
        verbose_name_plural = u"Cursos Extra dos Funcionário"
    
    funcionario = models.ForeignKey(Funcionario)
    nome = models.CharField(blank=True, max_length=100)
    data = models.DateField(u"Data de Conclusão", default=datetime.datetime.today)
    carga_horaria = models.IntegerField("Carga Horária", blank=True, null=True)
    # metas
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    

class ExperienciasProfissionaisFuncionario(models.Model):
    
    def __unicode__(self):
        return u"Experiência do Funcionário %s em %s" % (self.funcionario, self.nome_da_empresa)
    
    class Meta:
        verbose_name = "Experiência Profissional do Funcionário"
        verbose_name_plural = "Experiências Profissionais do Funcionário"
    
    def clean(self):
        if not self.emprego_atual and not self.data_demissao:
            raise ValidationError(u"É obrigatório a data da demissão caso esta não seja a experiência atual")
    
    funcionario = models.ForeignKey(Funcionario)
    emprego_atual = models.BooleanField(default=False)
    nome_da_empresa = models.CharField(blank=True, max_length=100)
    # endereço e contato da empresa
    telefone_fixo = models.CharField(blank=False, max_length=100, null=False, help_text="Formato: XX-XXXX-XXXX")
    endereco_completo = models.TextField(blank=True)
    # informacoes da experiencia
    data_admissao = models.DateField(blank=False)
    data_demissao = models.DateField(blank=True, null=True)
    cargo_inicial = models.CharField(blank=True, max_length=100)
    cargo_final = models.CharField(blank=True, max_length=100)
    ultimo_salario = models.DecimalField(u"Último Salário", max_digits=10, decimal_places=2)
    motivo_saida = models.CharField(blank=True, max_length=100)
    # metas
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class Cargo(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=False, null=False, max_length=100, verbose_name=u"Nome do Cargo")
    descricao = models.TextField(u"Descrição", blank=True)
    salario_referencia = models.DecimalField(u"Salário Referência", max_digits=10, decimal_places=2)
    departamento = models.ForeignKey('Departamento')
    periculosidade = models.DecimalField(u"Periculosidade", max_digits=10, decimal_places=2)
    gratificacao = models.DecimalField(u"Gratificação", max_digits=10, decimal_places=2)
    # exames padrao deste cargo
    exame_medico_padrao = models.ManyToManyField('TipoDeExameMedico')
    dias_renovacao_exames = models.IntegerField(blank=False, null=False, default=365)

class Departamento(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100, verbose_name="Nome do Departamento")

class PeriodoTrabalhado(models.Model):
    
    def __unicode__(self):
        if not self.fim:
            return u"Período ATIVO. Funcionário: %s. Admissão: %s" % (self.funcionario, self.inicio.strftime("%d/%m/%y"))
        else:
            return u"Período INATIVO. Funcionário: %s. Admissão: %s. Desligamento: %s" % (self.funcionario, self.inicio.strftime("%d/%m/%y"), self.fim.strftime("%d/%m/%y"))
    
    class Meta:
        verbose_name = u"Período Trabalhado"
        verbose_name_plural = u"Períodos Trabalhados"
        ordering = ['-criado',]
    
    funcionario = models.ForeignKey(Funcionario)
    inicio = models.DateField(default=datetime.datetime.today, blank=False)
    fim = models.DateField(blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class PromocaoSalario(models.Model):
    
    def __unicode__(self):
        if self.data_resolucao:
            data_resolucao_str = self.data_resolucao.strftime("%d/%m/%y")
        else:
            data_resolucao_str = u"Data Não Definida"
        if not self.avaliado:
            return u"Promoção de Salário do Funcionário %s SOLICITADO no dia %s" % (self.beneficiario, self.data_solicitacao.strftime("%d/%m/%y"))
        else:            
            if self.avaliado and self.aprovado:
                return u"Promoção de Salário do Funcionário %s APROVADA no dia %s" % (self.beneficiario, data_resolucao_str)
            if self.avaliado and not self.aprovado:
                return u"Promoção de Salário do Funcionário %s DECLINADA no dia %s" % (self.beneficiario, data_resolucao_str)
        
    
    class Meta:
        verbose_name = u"Promoção Salarial"
        verbose_name_plural = u"Promoções Salariais"
        ordering = ['data_solicitacao']
    

    def clean(self):
        if self.aprovado and not self.avaliado:
            raise ValidationError(u"Para aprovar uma Solicitação é preciso marcar como avaliado antes")
        if self.avaliado and not self.data_resolucao:
            raise ValidationError(u"Para avaliar uma Promoção de Salário, é obrigatório preencher a Data da Resolução.")
        if self.aprovado and not self.autorizador:
            raise ValidationError(u"Para aprovar uma Promoção de Salário, é obrigatório um Funcionário Autorizador.")
        if self.avaliado and not self.autorizador:
            raise ValidationError(u"Para avaliar uma Promoção de Salário, é obrigatório um Funcionário Autorizador.")
    
    aprovado = models.BooleanField(default=False)
    avaliado = models.BooleanField(default=False)
    descricao = models.CharField(blank=False, null=False,  max_length=100, verbose_name=u"Descrição")
    data_solicitacao = models.DateField(default=datetime.datetime.today, blank=False, null=False, verbose_name=u"Data da Solicitação")
    data_resolucao = models.DateField(blank=True, null=True, verbose_name=u"Data de Resolução")
    beneficiario = models.ForeignKey(Funcionario, related_name="promocao_salarial_set", verbose_name=u"Funcionário Beneficiado")
    solicitante = models.ForeignKey(Funcionario, related_name="solicitacao_promocao_salarial_set", verbose_name=u"Funcionário Solicitante")
    autorizador = models.ForeignKey(Funcionario, related_name="autorizacao_promocao_salarial_set", verbose_name=u"Funcionário que Autorizou a Promoção", blank=True, null=True)
    valor = models.DecimalField(u"Valor", max_digits=10, decimal_places=2)
    periodo_trabalhado = models.ForeignKey("PeriodoTrabalhado")
    observacao = models.TextField(blank=True, verbose_name=u"Observações Internas")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
class PromocaoCargo(models.Model):
    
    def __unicode__(self):
        if self.data_resolucao:
            data_resolucao_str = self.data_resolucao.strftime("%d/%m/%y")
        else:
            data_resolucao_str = u"Data Não Definida"
        if not self.avaliado:
            return u"Promoção de Cargo do Funcionário %s SOLICITADO no dia %s" % (self.beneficiario, self.data_solicitacao.strftime("%d/%m/%y"))
        else:            
            if self.avaliado and self.aprovado:
                return u"Promoção de Cargo do Funcionário %s APROVADA no dia %s" % (self.beneficiario, data_resolucao_str)
            if self.avaliado and not self.aprovado:
                return u"Promoção de Cargo do Funcionário %s DECLINADA no dia %s" % (self.beneficiario, data_resolucao_str)
    
    class Meta:
        verbose_name = u"Promoção de Cargo"
        verbose_name_plural = u"Promoções de Cargos"
        ordering = ['-criado']
    
    def clean(self):
        if self.aprovado and not self.avaliado:
            raise ValidationError(u"Para aprovar uma Solicitação é preciso marcar como avaliado antes")
        if self.avaliado and not self.data_resolucao:
            raise ValidationError(u"Para avaliar uma Promoção de Cargo, é obrigatório preencher a Data da Resolução.")
        if self.aprovado and not self.autorizador:
            raise ValidationError(u"Para aprovar uma Promoção de Cargo, é obrigatório um Funcionário Autorizador.")
        if self.avaliado and not self.autorizador:
            raise ValidationError(u"Para avaliar uma Promoção de Cargo, é obrigatório um Funcionário Autorizador.")
    
    # situação
    avaliado = models.BooleanField(default=False)
    aprovado = models.BooleanField(default=False)
    # dados gerais
    descricao = models.CharField(blank=False, null=False,  max_length=100, verbose_name=u"Descrição")
    data_solicitacao = models.DateField(default=datetime.datetime.today, blank=False, null=False, verbose_name=u"Data da Solicitação de Promoção de Cargo")
    data_resolucao = models.DateField(blank=True, null=True, verbose_name=u"Data de Resolução")
    # dados da promocao de cargo
    beneficiario = models.ForeignKey(Funcionario, related_name="promocao_cargo_set", verbose_name=u"Funcionário Beneficiado pela Promoção de Cargo")
    solicitante = models.ForeignKey(Funcionario, related_name="solicitacao_promocao_cargo_set", verbose_name=u"Funcionário Solicitante da Promoção de Cargo")
    autorizador = models.ForeignKey(Funcionario, related_name="autorizacao_promocao_cargo_set", verbose_name=u"Funcionário que Autorizou a Promoção de Cargo", blank=True, null=True)
    cargo_antigo = models.ForeignKey(Cargo, related_name="cargo_antigo_set")
    cargo_novo = models.ForeignKey(Cargo, related_name="cargo_novo_set")
    periodo_trabalhado = models.ForeignKey("PeriodoTrabalhado")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
class SolicitacaoDeLicenca(models.Model):
    
    def __unicode__(self):
        return u"Solicitação Licença %s do Funcionário %s entre %s e %s: %s" % \
            (self.get_tipo_display(), self.funcionario, self.inicio.strftime("%d/%m/%y"), self.fim.strftime("%d/%m/%y"), self.get_status_display())
    
    class Meta:
        verbose_name = u"Solicitação de Licença"
        verbose_name_plural = u"Solicitações de Licenças"
        ordering = ['inicio']
    
    def clean(self):
        if self.status == "autorizada" or self.status == "declinada":
            if not self.processado_por:
                raise ValidationError(u"Se a Solicitação de Licença for autorizada ou declinada, é previso informar o Funcionário que a processou.")
    
    def delta(self):
        delta = self.fim - self.inicio
        return delta
    
    funcionario = models.ForeignKey(Funcionario)
    motivo = models.TextField(blank=False)
    realizada = models.BooleanField(default=False)
    inicio = models.DateField(u"Início da Licença", default=datetime.datetime.today)
    fim = models.DateField(u"Término da Licença", default=datetime.datetime.today()+datetime.timedelta(days=4))
    status = models.CharField(u"Situação da Solicitação", blank=False, null=False, max_length=100, choices=SOLICITACAO_LICENCA_STATUS_CHOICES, default="aberta")
    tipo = models.CharField(u"Tipo da Solicitação", blank=False, null=False, max_length=100, choices=SOLICITACAO_LICENCA_TIPO_CHOICES)
    data_criado = models.DateField(u"Data da Solicitação",default=datetime.datetime.today, blank=False, null=False)
    data_autorizado = models.DateField(u"Data da Autorização", blank=True, null=True)
    processado_por = models.ForeignKey(Funcionario, blank=True, null=True, related_name="autorizado_por")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class FolhaDePonto(models.Model):
    
    class Meta:
        verbose_name = u"Folha de Ponto"
        verbose_name_plural = u"Folhas de Ponto"
        ordering = ['data_referencia',]
    
    def __unicode__(self):
        return u"Folha de ponto (#%d) para funcionário %s referente ao mês %d de %d" % (self.id, self.funcionario, self.data_referencia.month, self.data_referencia.year)

    def filename(self):
            return os.path.basename(self.arquivo.name)

    def funcionario_mes_ano(self):
        return "%s: %s/%s" % (self.funcionario, self.data_referencia.month, self.data_referencia.year)

    def total_horas(self):
        return self.entradafolhadeponto_set.all().aggregate(total_trabalhado=Sum('total'))['total_trabalhado'] or 0

    funcionario = models.ForeignKey(Funcionario)
    periodo_trabalhado = models.ForeignKey('PeriodoTrabalhado')
    data_referencia = models.DateField(u"Mês e Ano de Referência",default=datetime.datetime.today)
    encerrado = models.BooleanField(default=False)
    autorizado = models.BooleanField(default=False)
    arquivo = models.FileField(upload_to=funcionario_entrada_folha_ponto_assinada, blank=True, null=True, help_text="Arquivo a ser anexado no fechamento do mês da data de referência", max_length=300)
    funcionario_autorizador = models.ForeignKey(Funcionario, related_name="folhadeponto_autorizado_set", blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class EntradaFolhaDePonto(models.Model):

    def __unicode__(self):
        return u"Funcionário %s. de %s a %s: %s" % (self.folha.funcionario, self.inicio, self.fim, self.total)
    
    def funcionario():
        return self.folha.funcionario
        
    class Meta:
        verbose_name = "Entrada de Folha de Ponto"
        verbose_name_plural = "Entradas de Folha de Ponto"
    
    
    folha = models.ForeignKey(FolhaDePonto)
    inicio = models.DateField(default=datetime.datetime.today)
    fim = models.DateField(default=datetime.date.today()+datetime.timedelta(days=7))
    total = models.DecimalField(max_digits=5, decimal_places=1)
    # arquivo impresso e digitalizado
    arquivo = models.FileField(upload_to=funcionario_entrada_folha_ponto_assinada, blank=True, null=True, max_length=300, help_text="Arquivo a ser anexado a cada entrada")
    adicionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="entradas_folha_lancada_set")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class DependenteDeFuncionario(models.Model):
    
    class Meta:
        verbose_name = "Dependente de Funcionário"
        verbose_name_plural = "Dependentes de Funcionários"
    

    def __unicode__(self):
        return "%s (%s de %s)" % (self.nome, self.get_relacao_display(), self.funcionario)

    nome = models.CharField(blank=True, max_length=100)
    relacao = models.CharField(blank=True, max_length=100, choices=DEPENDENTE_FUNCIONARIO_CHOICES)
    nascimento = models.DateField(default=datetime.datetime.today)
    funcionario = models.ForeignKey('Funcionario')
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
class TipoDeExameMedico(models.Model):
    
    def __unicode__(self):
        return "%s - %s" % (self.nome, self.valor)
        
    class Meta:
        verbose_name = "Tipo de Exame Médico"
        verbose_name_plural = "Tipos de Exames Médicos"
        
    
    nome = models.CharField(blank=True, max_length=100)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class RotinaExameMedico(models.Model):
    
    class Meta:
        verbose_name = "Rotina de Exame Médico"
        verbose_name_plural = "Rotinas de Exames Médicos"
    
    
    def __unicode__(self):
        if self.data:
            data = self.data.strftime("%d/%m/%y")
        else:
            data = u"Data Indefinida"
        if self.realizado:
            realizado = u"Realizado"
        else:
            realizado = u"Não Realizado"
        return "Exame do tipo %s para %s em %s %s" % (self.get_tipo_display(), self.funcionario.nome, data, realizado)
    
    def valor_total(self):
        valor_total = 0
        for i in self.exames.all():
            valor_total += i.valor
        return valor_total
    
    def pendente(self):
        if datetime.date.today() > self.data and not self.realizado:
            return True
        else:
            return False
    
    def clean(self):
        if self.realizado and not self.arquivo:
            raise ValidationError(u"Para marcar um exame como realizado, é preciso anexar o Arquivo Digital do retorno do Exame.")
    
    data = models.DateTimeField(blank=True, null=True, default=datetime.datetime.now, help_text="Formato: dd/mm/yy hh:mm")
    tipo = models.CharField(blank=True, max_length=100, choices=ROTINA_EXAME_MEDICO_CHOICES)
    funcionario = models.ForeignKey('Funcionario')
    exames = models.ManyToManyField('TipoDeExameMedico', blank=True, null=True)
    realizado = models.BooleanField(default=False)
    periodo_trabalhado = models.ForeignKey('PeriodoTrabalhado')
    arquivo = models.FileField(upload_to=funcionario_rotina_exame_medico, blank=True, null=True, max_length=300)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
class Demissao(models.Model):
    
    def __unicode__(self):
        return u"Processo de demissão para %s (%s -> %s) iniciado em %s" % (self.demitido, self.periodo_trabalhado_finalizado.inicio, self.periodo_trabalhado_finalizado.fim, self.criado)
    
    class Meta:
        verbose_name = "Processo de Demissão"
        verbose_name_plural = "Processos de Demissão"
        
    # ATENCAO
    # O demitido é um Funcionário, não precisa ter user
    # O demissor é um user, com acesso ao sistema
    
    demitido = models.ForeignKey('Funcionario', related_name="demissao_set")
    data = models.DateField(default=datetime.datetime.today)
    periodo_trabalhado_finalizado = models.ForeignKey('PeriodoTrabalhado')
    demissor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="demissor_set")
    status = models.CharField(blank=True, max_length=100, choices=DEMISSAO_FUNCIONARIO_CHOICES, default="andamento")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")    

class PerfilAcessoRH(models.Model):
    '''Perfil de Acesso ao RH'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso ao RH"
        verbose_name_plural = u"Perfis de Acesso ao RH"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        


class Feriado(models.Model):
    
    class Meta:
        ordering = ['data']

    ativo = models.BooleanField(default=True)
    nome = models.CharField(blank=True, max_length=100)
    data = models.DateField()
    importado_por_sync = models.BooleanField(default=False)
    uid = models.CharField(blank=True, max_length=100) # caso tenha sido importado
    
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criação")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualização")

# SIGNALS

## PeriodoTrabalhado SIGNALS
def periodo_trabalhado_post_save(signal, instance, sender, **kwargs):
    '''Rotina de pós save:
    Ao criar um periodo trabalhado, cria um exame admissional,
    Define como corrent do funcionario escolhido
    '''
    # somente criados
    if not kwargs.get('created'):
            return False
    # cria rotina de exame
    exame = RotinaExameMedico.objects.create(
        tipo='a',
        periodo_trabalhado=instance,
        funcionario=instance.funcionario,
        data=None,
    )
    for exame_padrao in instance.funcionario.cargo_atual.exame_medico_padrao.all():
        exame.exames.add(exame_padrao)
    exame.save()
    # define o periodo trablhado como a corrente
    instance.funcionario.periodo_trabalhado_corrente = instance
    instance.funcionario.save()
    
    

## FUNCIONARIO SIGNALS
def funcionario_post_save(signal, instance, sender, **kwargs):
      ''' Atualiza os campos cargo atual e salario atual sempre 
            que houver promocoes de salario ou cargo
      '''
      # consolidacao do cargo:
      # caso ele não possua um cargo promovido, o cargo inicial sera o atual
      if not instance.cargo_atual and instance.cargo_inicial:
          instance.cargo_atual = instance.cargo_inicial
          instance.save()
      # atualizacao de cargo:
      #caso haja alguma promocao e o cargo for diferente do atual...
      promo_cargos = instance.promocao_cargo_set.filter(aprovado=True)
      if promo_cargos.count():
            ultimo_cargo = promo_cargos.order_by('-criado')[0].cargo_novo
            if ultimo_cargo != instance.cargo_atual:
                  instance.cargo_atual = ultimo_cargo
                  instance.save()

      # atualizacao de salario:
      #caso haja alguma promocao de salario diferente do atual...
      promo_salarios = instance.promocao_salarial_set.filter(aprovado=True)
      if promo_salarios.count():
            ultimo_salario = promo_salarios.order_by('-criado')[0].valor
            if ultimo_salario != instance.salario_atual:
                  instance.salario_atual = ultimo_salario
                  instance.save()

def atualizador_promocao_post_save(signal, instance, sender, **kwargs):
    '''Signal da promoção de Cargo.
     salva o beneficiario apos criar uma promocao para atualizar
     o cargo
    '''
    instance.beneficiario.save()

def cria_folha_ponto_funcionario_criado(signal, instance, sender, **kwargs):
    '''Após criar o funcionário, este sinal garante também a criação da folha de ponto
    '''
    if instance.periodo_trabalhado_corrente:
        today = datetime.date.today()
        folha,created = instance.folhadeponto_set.get_or_create(
            data_referencia__month=today.month,
            data_referencia__year=today.year,
            periodo_trabalhado=instance.periodo_trabalhado_corrente
        )

# SIGNALS CONNECTION
signals.post_save.connect(cria_folha_ponto_funcionario_criado, sender=Funcionario)
signals.post_save.connect(funcionario_post_save, sender=Funcionario)
signals.post_save.connect(atualizador_promocao_post_save, sender=PromocaoCargo)
signals.post_save.connect(atualizador_promocao_post_save, sender=PromocaoSalario)
signals.post_save.connect(periodo_trabalhado_post_save, sender=PeriodoTrabalhado)