# -*- coding: utf-8 -*-
import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.db.models import signals
class LocalAula(models.Model):
    '''Endereço de onde é possível ter aulas'''
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)
    cidade = models.ForeignKey("cadastro.Cidade", blank=False, null=False)
    bairro = models.ForeignKey("cadastro.Bairro")
    cep = models.CharField(blank=True, max_length=100, verbose_name=u"CEP")
    rua = models.CharField(blank=True, max_length=500, verbose_name=u"Rua")
    numero = models.CharField(blank=True, max_length=100, verbose_name=u"Número")
    complemento = models.CharField(blank=True, max_length=200, verbose_name=u"Complemento")

class PerfilProfessor(models.Model):
    '''Somente funcionario pode ser professor'''
    
    def __unicode__(self):
        return "Professor: %s" % self.funcionario.nome

    funcionario = models.OneToOneField('rh.Funcionario')

class PerfilAluno(models.Model):
    '''Cliente ou Funcionario pode ser Aluno'''
    
    def __unicode__(self):
        return self.content_object.nome
    
    nome = models.CharField(blank=True, max_length=100)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

class GrupoAula(models.Model):
    '''Grupos de Aula para separação básica'''
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)

class Aula(models.Model):
    '''Aula em si, separada por grupo, contendo professor e local'''
    
    def __unicode__(self):
        return self.nome
    
    nome = models.CharField(blank=True, max_length=100)
    grupo = models.ForeignKey('GrupoAula')
    professor = models.ForeignKey('PerfilProfessor')
    local = models.ForeignKey('LocalAula')
    alunos_inscritos = models.ManyToManyField('PerfilAluno')

class UnidadeDeAula(models.Model):
    '''Dias Agendados de Aulas'''
    
    def __unicode__(self):
        return "Aula #%s: %s, de: %s a %s com %s" % (self.id, self.aula, self.inicio, self.fim, self.professor)
    
    aula = models.ForeignKey('Aula')
    inicio = models.DateTimeField(blank=True, default=datetime.datetime.now)
    fim = models.DateTimeField(blank=True, default=datetime.datetime.now)
    professor = models.ForeignKey('PerfilProfessor')

class ParticipaoDiaDeAula(models.Model):
    dia_de_aula = models.ForeignKey('UnidadeDeAula')
    professor = models.ForeignKey('PerfilProfessor')
    aluno = models.ForeignKey('PerfilAluno')
    participacao_efetiva = models.BooleanField(default=True)



# SINAIS
def grava_nome_aluno(signal, instance, sender, **kwargs):
    '''Após salvar o Perfil do aluno, puxa o nome do objeto relacionado (Funcionario ou Cliente)
    '''
    if instance.nome != instance.content_object.nome:
        instance.nome = instance.content_object.nome
        instance.save()


# conectores de sinais
signals.post_save.connect(grava_nome_aluno, sender=PerfilAluno)