from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

def home(request):
    return render_to_response('frontend/base.html', locals(), context_instance=RequestContext(request),)
    
