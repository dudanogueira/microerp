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
__copyright__ = 'Copyright (c) 2012 Duda Nogueira'
__version__ = '0.0.1'

import os, datetime
from django.db import models

from django.db.models import signals

from django.core.exceptions import ValidationError

from sorl.thumbnail import ImageField
from django_extensions.db.fields import UUIDField

from django.conf.global_settings import LANGUAGES

from django.contrib.localflavor.br.forms import BRCPFField, BRCNPJField, BRPhoneNumberField
from django.conf import settings
from django.contrib.auth.models import User, Group

def funcionario_avatar_img_path(instance, filename):
    return os.path.join(
        'funcionarios/', instance.uuid, 'avatar/', filename
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
        # se possui filhos, precisa informar a quantidade
        if self.possui_filhos:
            if not self.quantidade_filhos:
                raise ValidationError(
                    u"Se possuir filhos, é obrigatório informar a quantidade."
                )
            else:
                # ja que filhos, conferir os nascimentos
                if self.nascimento_dos_filhos:
                    nascimentos = self.nascimento_dos_filhos.split(",")
                    if len(nascimentos) != self.quantidade_filhos:
                        raise ValidationError(
                            u"Quantidade de nascimentos informado não confere com quantidade de filhos"
                        )
                else:
                    raise ValidationError(
                        u"Se possuir filhos, é obrigatório informar os anos de nascimento."
                    )
    
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
    
    def responsavel_comercial(self):
        try:
            dpto = Departamento.objects.get(pk=settings.DEPARTAMENTO_COMERCIAL_ID)
            if dpto.grupo_responsavel.user_set.filter(funcionario__id=self.pk):
                return True
            else: 
                return False
        except:
            return False

    def analista_comercial(self):
        try:
            dpto = Departamento.objects.get(pk=settings.DEPARTAMENTO_COMERCIAL_ID)
            if dpto.grupo_analista.user_set.filter(funcionario__id=self.pk):
                return True
            else: return False
        except:
            return False

    uuid = UUIDField()
    foto = ImageField(upload_to=funcionario_avatar_img_path, blank=True, null=True)
    user = models.OneToOneField(User, verbose_name="Usuário do Sistema", blank=True, null=True)
    nome = models.CharField(blank=False, null=False, max_length=300, verbose_name=u"Nome do Funcionário")
    # geral / documentos / pessoal
    residencia = models.CharField(blank=True, null=True, max_length=100, choices=FUNCIONARIO_RESIDENCIA_CHOICES)
    valor_aluguel = models.FloatField(blank=True, null=True)
    nascimento = models.DateField(blank=False)
    observacao = models.TextField(blank=True, null=True)
    sexo = models.CharField(blank=True, null=True, max_length=100, choices=FUNCIONARIO_SEXO_CHOICES)
    naturalidade = models.CharField(blank=True, null=True, max_length=100)
    nacionalidade = models.CharField(blank=True, null=True,  max_length=100, default="Brasil")
    estado_civil = models.CharField(blank=True, null=True, max_length=100, choices=FUNCIONARIO_ESTADO_CIVIL_CHOICES)
    possui_filhos = models.BooleanField(default=False)
    quantidade_filhos = models.IntegerField(blank=True, null=True)
    nascimento_dos_filhos = models.CharField(blank=True, null=True, max_length=100, help_text="Informe o ano de Nascimento dos filhos separado por vírgulas, Ex: 1999, 2001, 2003")
    nome_companheiro = models.CharField(blank=True, null=True, max_length=300)
    nome_pai = models.CharField(u"Nome do Pai", blank=True, null=True, max_length=300)
    nome_mae = models.CharField(u"Nome da Mãe", blank=True, null=True, max_length=300)
    rg = models.CharField(blank=True, null=True, max_length=100)
    rg_data = models.DateField(u"Data de Emissão do RG", blank=True, null=True,)
    rg_expeditor = models.CharField(u"Órgão Emissor do RG", blank=True, null=True, max_length=100)
    cpf = models.CharField(u"CPF - Cadastro de Pessoa Física", blank=True, null=True, max_length=255)
    carteira_profissional_numero = models.CharField(blank=True, null=True, max_length=100)
    carteira_profissional_serie = models.CharField(blank=True, null=True,max_length=100)
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
    escolaridade_conclusao = models.DateField("Ano de Conclusão dos estudos", default=datetime.datetime.today)
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
    salario_inicial = models.FloatField(blank=False, null=False)
    salario_atual = models.FloatField(blank=True, null=True)
    valor_hora = models.FloatField(blank=False, null=False, help_text=u"Valor usado para calcular serviços e projetos")
    # cargo
    cargo_inicial = models.ForeignKey("Cargo", related_name="cargo_inicial")
    cargo_atual = models.ForeignKey("Cargo", related_name="cargo_promovido", blank=True, null=True)
    departamento = models.ForeignKey("Departamento")
    funcionario_superior = models.ForeignKey("self", blank=True, null=True, verbose_name=u"Funcionário Superior", help_text=u"Funcionário a quem se reportar. Se deixado em branco, será usado o Grupo Responsável pelo Departamento", )
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
    ultimo_salario = models.FloatField()
    motivo_saida = models.CharField(blank=True, max_length=100)
    # metas
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    

class Cargo(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=False, null=False, max_length=100, verbose_name=u"Nome do Cargo")
    salario_referencia = models.FloatField(blank=True, null=True)
    departmento = models.ForeignKey('Departamento')

class Departamento(models.Model):
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100, verbose_name="Nome do Departamento")
    grupo_responsavel = models.ForeignKey(Group, blank=True, null=True, verbose_name="Grupo de Funcionários Responsáveis", related_name="grupo_responsavel")
    grupo_analista = models.ForeignKey(Group, blank=True, null=True, verbose_name="Grupo de Funcionários Analistas", related_name="grupo_analista") 


class PeriodoTrabalhado(models.Model):
    
    def __unicode__(self):
        if not self.fim:
            return u"Período ATIVO. Funcionário: %s. Início: %s" % (self.funcionario, self.inicio)
        else:
            return u"Período INATIVO. Funcionário: %s. Início: %s. Fim: %s" % (self.funcionario, self.inicio, self.fim)
    
    class Meta:
        verbose_name = u"Período Trabalhado"
        verbose_name_plural = u"Períodos Trabalhados"
    
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
    valor = models.FloatField(blank=False, null=False)
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
    cargo_antigo = models.ForeignKey(Cargo, related_name="cargo_antigo")
    cargo_novo = models.ForeignKey(Cargo, related_name="cargo_novo")
    periodo_trabalhado = models.ForeignKey("PeriodoTrabalhado")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
class SolicitacaoDeLicenca(models.Model):
    
    def __unicode__(self):
        return u"Solicitação Licença %s realizada pelo Funcionário %s no dia %s: %s" % \
            (self.get_tipo_display(), self.funcionario, self.data_criado.strftime("%d/%m/%y"), self.get_status_display())
    
    class Meta:
        verbose_name = u"Solicitação de Licença"
        verbose_name_plural = u"Solicitações de Licenças"
    
    def clean(self):
        if self.status == "autorizada" or self.status == "declinada":
            if not self.processado_por:
                raise ValidationError(u"Se a Solicitação de Licença for autorizada ou declinada, é previso informar o Funcionário que a processou.")
    
    funcionario = models.ForeignKey(Funcionario)
    
    inicio = models.DateField(u"Início da Licença", default=datetime.datetime.today)
    fim = models.DateField(u"Término da Licença", default=datetime.datetime.today)
    status = models.CharField(u"Situação da Solicitação", blank=False, null=False, max_length=100, choices=SOLICITACAO_LICENCA_STATUS_CHOICES, default="aberta")
    tipo = models.CharField(u"Tipo da Solicitação", blank=False, null=False, max_length=100, choices=SOLICITACAO_LICENCA_TIPO_CHOICES)
    data_criado = models.DateField(u"Data da Solicitação",default=datetime.datetime.today, blank=False, null=False)
    data_autorizado = models.DateField(u"Data da Autorização", blank=True, null=True)
    processado_por = models.ForeignKey(Funcionario, blank=True, null=True, related_name="autorizado_por")
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        

class FolhaDePonto(models.Model):
    
    def __unicode__(self):
        return u"Folha de ponto (#%d) para funcionário %s referente ao mês %d de %d" % (self.id, self.funcionario, self.data_referencia.month, self.data_referencia.year)

    def funcionario_mes_ano(self):
        return "%s: %s/%s" % (self.funcionario, self.data_referencia.month, self.data_referencia.year)

    def entradas_validas(self):
        entradas_validas = self.entradafolhadeponto_set.filter(
            hora__year=self.data_referencia.year,
            hora__month=self.data_referencia.month
        ).order_by('hora')
        return self.entradafolhadeponto_set.all()
    
    def calcular_tipo_entrada(self):
        '''Define as Entradas relacionadas como Registro de Entrada ou Registro de saída'''
        entradas_validas = self.entradas_validas()
        ref = 1
        for entrada in entradas_validas:
            if ref % 2 == 1:
                entrada.tipo = 'entrada'
            else:
                entrada.tipo = 'saida'
            entrada.save()
            ref += 1
    
    def calcular_acumulado(self):
        '''Calcula o acumulado de horas da folha de ponto com base nos registros de entrada e saída'''
        entradas_validas = self.entradas_validas()
        #TODO
    
    funcionario = models.ForeignKey(Funcionario)
    data_referencia = models.DateField(u"Mês e Ano de Referência",default=datetime.datetime.today)
    encerrado = models.BooleanField(default=False)
    autorizado = models.BooleanField(default=False)
    funcionario_autorizador = models.ForeignKey(Funcionario, related_name="folhadeponto_autorizado_set", blank=True, null=True)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
class EntradaFolhaDePonto(models.Model):
    
    def __unicode__(self):
        if self.tipo:
            return "%s às %s" % (self.tipo, self.hora)
        else:
            return u"Funcionário %s. Registro às %s" % (self.folha.funcionario, self.hora)
    
    def clean(self):
        if self.hora.year == self.folha.data_referencia.year:
            if self.hora.month == self.folha.data_referencia.month:
                pass
            else:
                raise ValidationError("Erro! A entrada na folha de ponto deve ser no mês e ano que a data de referência da Folha")
        else:            
            raise ValidationError("Erro! A entrada na folha de ponto deve ser no mesmo ano que a data de referência da Folha")
        
    
    folha = models.ForeignKey(FolhaDePonto)
    hora = models.DateTimeField(blank=False, default=datetime.datetime.now)
    tipo = models.CharField(blank=True, null=True, max_length=100, choices=ENTRADA_FOLHA_DE_PONTO_CHOICES)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")        
    
# SIGNALS
## FUNCIONARIO SIGNALS
def funcionario_post_save(signal, instance, sender, **kwargs):
      ''' Atualiza os campos cargo atual e salario atual sempre 
            que houver promocoes de salario ou cargo
      '''
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

# SIGNALS CONNECTION
signals.post_save.connect(funcionario_post_save, sender=Funcionario)
signals.post_save.connect(atualizador_promocao_post_save, sender=PromocaoCargo)
signals.post_save.connect(atualizador_promocao_post_save, sender=PromocaoSalario)