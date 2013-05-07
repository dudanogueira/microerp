from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

# COMERCIAL DECORATORS
def possui_perfil_acesso_ocorrencia(user, login_url="/"):
    try:
        if user.perfilacessoocorrencia and user.funcionario.periodo_trabalhado_corrente:
            return True
    except:
        return False

# HOME
@login_required
@user_passes_test(possui_perfil_acesso_ocorrencia, login_url='/')
def home(request):
    return render_to_response('frontend/ocorrencia/ocorrencia-home.html', locals(), context_instance=RequestContext(request),)
