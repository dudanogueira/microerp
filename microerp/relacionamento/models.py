from django.db import models

class PerfilAcessoRelacionamento(models.Model):
    '''Perfil de Acesso ao Relacionamento'''
    
    class Meta:
        verbose_name = u"Perfil de Acesso à Recepção"
        verbose_name_plural = u"Perfis de Acesso à Recepção"
    
    gerente = models.BooleanField(default=False)
    analista = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class TipoDeInteracao(models.Model):
    nome = models.CharField(blank=True, max_length=100)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")

class CanalDeInteracao(models.Model):
    nome = models.CharField(blank=True, max_length=100)
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")


class Relacionamento(models.Model):
    '''Registro de cada interacao com Cliente ou Pre Cliente, como ligação, email,
    visita ao cliente, visita do cliente à Loja, etc '''
    
    def __unicode__(self):
        return u"Relacionamento ID%s" % self.pk
    
    # cliente / precliente
    cliente = models.ForeignKey('cadastro.Cliente', blank=True, null=True)
    precliente = models.ForeignKey('cadastro.PreCliente', blank=True, null=True)
    tipo = models.ForeignKey(TipoDeInteracao)
    canal = models.ForeignKey(TipoDeInteracao)
    resumo = models.TextField(blank=True)
    funcionario = models.ForeignKey('rh.Funcionario')
    # relacao generica
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    objeto_interacao = GenericForeignKey('content_type', 'object_id')
    # objeto de interacao pode ser: solicitacao, followup de proposta, followup de programacao, etc
    # metadata
    criado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True, verbose_name="Criado")
    atualizado = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True, verbose_name="Atualizado")