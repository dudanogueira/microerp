from django.contrib import admin

from models import PerfilAcessoProgramacao
from models import FollowUpDeContrato
from models import TarefaDeProgramacao

class FollowUpDeContratoInline(admin.StackedInline):
    model = FollowUpDeContrato
    extra= 0

class TarefaDeProgramacaoAdmin(admin.ModelAdmin):
    inlines = [FollowUpDeContratoInline,]

admin.site.register(PerfilAcessoProgramacao)
admin.site.register(FollowUpDeContrato)
admin.site.register(TarefaDeProgramacao,TarefaDeProgramacaoAdmin)