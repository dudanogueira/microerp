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

#
# VIEWS
#
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.contrib.auth.decorators import user_passes_test

from comercial.models import ContratoFechado

def possui_perfil_acesso_financeiro(user, login_url="/"):
    try:
        if user.perfilacessofinanceiro and user.funcionario.ativo():
            return True
    except:
        return False

@user_passes_test(possui_perfil_acesso_financeiro, login_url='/')
def home(request):
    return render_to_response('frontend/financeiro/financeiro-home.html', locals(), context_instance=RequestContext(request),)


def contratos_a_lancar(request):
    contratos_fechados = ContratoFechado.objects.filter(status="emaberto", tipo="fechado")
    return render_to_response('frontend/financeiro/financeiro-contratos-a-lancar.html', locals(), context_instance=RequestContext(request),)