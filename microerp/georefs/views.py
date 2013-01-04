# -*- coding: utf-8 -*-

from django.contrib.gis.sitemaps.views import kml

from models import ReferenciaGeograficaCliente

from django.http import HttpResponse

from django.template.loader import render_to_string

def kml_clientes(request):
    georef_clientes = ReferenciaGeograficaCliente.objects.all()
    rendered = render_to_string('georefs/clientes_kml_list.html', {'georef_clientes': georef_clientes})
    return HttpResponse(rendered, content_type="application/xhtml+xml")
    #return kml(request, "georefs", "ReferenciaGeograficaCliente", field_name="ponto", compress=False, )