# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import user_passes_test


from django import forms

#
# DECORATORS
#

def possui_perfil_acesso_producao(user, login_url="/"):
    try:
        if user.perfilacessoproducao:
            return True
    except:
        return False

@user_passes_test(possui_perfil_acesso_producao)
def home(request):
    return render_to_response('frontend/producao/producao-home.html', locals(), context_instance=RequestContext(request),)