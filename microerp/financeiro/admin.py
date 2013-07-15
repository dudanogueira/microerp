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

from financeiro.models import PerfilAcessoFinanceiro
from financeiro.models import Lancamento

class PerfilAcessoFinanceiroAdmin(admin.ModelAdmin):
    pass

class LancamentoAdmin(admin.ModelAdmin):
    pass

admin.site.register(PerfilAcessoFinanceiro, PerfilAcessoFinanceiroAdmin)
admin.site.register(Lancamento, LancamentoAdmin)