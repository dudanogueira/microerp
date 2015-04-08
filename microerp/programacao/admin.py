from django.contrib import admin

from models import PerfilAcessoProgramacao
from models import FollowUpDeOrdemDeServico
from models import TarefaDeProgramacao
from models import OrdemDeServico

class FollowUpDeContratoInline(admin.StackedInline):
    model = FollowUpDeOrdemDeServico
    extra= 0

admin.site.register(PerfilAcessoProgramacao)
admin.site.register(FollowUpDeOrdemDeServico)
admin.site.register(TarefaDeProgramacao)
admin.site.register(OrdemDeServico)