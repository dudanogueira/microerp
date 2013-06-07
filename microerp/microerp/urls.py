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

from django.conf.urls import patterns, include, url

from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

# auth system
urlpatterns += patterns('django.contrib.auth',
    url(r'^sair/$', 'views.logout', {}, 'logout'),
    url(r'^accounts/login/$', 'views.login', {}, 'login'),
)

# urls do frontend
app_frontend = getattr(settings, 'APP_DE_FRONTEND', "frontend_base")
urlpatterns += patterns('',
    url(r'^$', '%s.views.home' % app_frontend, name='home'),
    # Interface do Cliente
    url(r'^cliente/$', '%s.views.cliente' % app_frontend, name='interface_home_cliente'),
    # Interface do Funcionario
    url(r'^funcionario/$', '%s.views.funcionario' % app_frontend, name='interface_home_funcionario'),
    # modulo principal>recados
    url(r'^funcionario/meus_recados/$', '%s.views.meus_recados' % app_frontend, name='meus_recados'),
    url(r'^funcionario/meus_recados/(?P<recado_id>[0-9]+)/marcar/lido/$', '%s.views.meus_recados_marcar_lido' % app_frontend, name='meus_recados_marcar_lido'),
    # modulo principal>solicitacoes
    url(r'^funcionario/minhas_solicitacoes/$', '%s.views.minhas_solicitacoes' % app_frontend, name='minhas_solicitacoes'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/resolvido/$', '%s.views.minhas_solicitacoes_resolvido' % app_frontend, name='minhas_solicitacoes_resolvido'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/abrir/correcao/$', '%s.views.minhas_solicitacoes_abrir_correcao' % app_frontend, name='minhas_solicitacoes_abrir_correcao'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/fechar/contato/$', '%s.views.minhas_solicitacoes_fechar_contato' % app_frontend, name='minhas_solicitacoes_fechar_contato'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/fechar/visto/$', '%s.views.minhas_solicitacoes_fechar_visto' % app_frontend, name='minhas_solicitacoes_fechar_visto'),
    
    # modulo RH
    url(r'^rh/', include('rh.urls', namespace="rh")),
    # modulo recepcao
    url(r'^recepcao/', include('cadastro.urls', namespace="cadastro")),
    # modulo comercial
    url(r'^comercial/', include('comercial.urls', namespace="comercial")),
    # modulo solicitacao
    url(r'^solicitao/', include('solicitacao.urls', namespace="solicitacao")),   
    # modulo estoque
    url(r'^estoque/', include('estoque.urls', namespace="estoque")),   
    
)
# django-select2
urlpatterns += patterns("",
    url(r"^select2/", include("django_select2.urls")),
)


# DEBUGG
from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        # CONTENT MEDIA
        url(r'^media/(.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT }
        ),
        url(r'^static/(.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT }
        ),
    )
