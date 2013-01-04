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
__copyright__ = 'Copyright (c) 2012 Duda Nogueira'
__version__ = '0.0.1'

# extenda o seu frontend aqui

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'frontend_seltec.views.home', name='home'),
    url(r'^demo/$', 'frontend_seltec.views.demo', name='demo'),
    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # comercial
    (r'^comercial/', include('comercial.urls', namespace="comercial")),
)

# auth system
urlpatterns += patterns('django.contrib.auth',
    url(r'^sair/$', 'views.logout', {}, 'logout'),
    url(r'^entrar/$', 'views.login', {}, 'login'),
)

# georefs
urlpatterns += patterns('georefs',
    url(r'^geo/clientes/$', 'views.kml_clientes', {}, 'kml_clientes'),
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
