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

from django.contrib import admin

from treinamento.models import LocalAula
from treinamento.models import PerfilProfessor
from treinamento.models import PerfilAluno
from treinamento.models import GrupoAula
from treinamento.models import Aula
from treinamento.models import UnidadeDeAula
from treinamento.models import ParticipaoDiaDeAula

class AulaAdmin(admin.ModelAdmin):
    search_fields = 'nome', 'grupo__nome', 'alunos_inscritos__nome'
    filter_horizontal = 'alunos_inscritos',
    list_display = 'nome', 'professor', 'grupo', 'local'
    list_filter = 'grupo', 'professor', 'local'

class UnidadeDeAulaAdmin(admin.ModelAdmin):
    search_fields = 'aula__nome', 'aula_grupo__nome',

admin.site.register(LocalAula)
admin.site.register(PerfilProfessor)
admin.site.register(PerfilAluno)
admin.site.register(GrupoAula)
admin.site.register(Aula, AulaAdmin)
admin.site.register(UnidadeDeAula)
admin.site.register(ParticipaoDiaDeAula)