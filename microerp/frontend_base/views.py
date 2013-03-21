from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django.contrib.auth.forms import AuthenticationForm

def home(request):
    form = AuthenticationForm()
    a = "aaaa"
    return render_to_response('frontend/main-home.html', locals(), context_instance=RequestContext(request),)