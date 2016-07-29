from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import login, logout
from frontend2.views import home, funcionario, minhas_solicitacoes, \
minhas_solicitacoes_resolvido, minhas_solicitacoes_abrir_correcao, \
minhas_solicitacoes_fechar_contato, minhas_solicitacoes_fechar_visto, \
teste

from estoque.views import ajax_consulta_produto
from rh.views import ajax_consulta_cargo

urlpatterns = [
    url(r'^teste/$', teste ),
    url(r'^admin/', admin.site.urls),
    url(r'^sair/$', logout, name='logout'),
    url(r'^accounts/login/$', login, name='login'),
    # PAGINA INICIAL
    url(r'^$', home, name='home'),
    url(r'^funcionario/$', funcionario, name='interface_home_funcionario'),
    url(r'^funcionario/minhas_solicitacoes/$', minhas_solicitacoes, name='minhas_solicitacoes'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/resolvido/$', minhas_solicitacoes_resolvido, name='minhas_solicitacoes_resolvido'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/abrir/correcao/$', minhas_solicitacoes_abrir_correcao, name='minhas_solicitacoes_abrir_correcao'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/fechar/contato/$', minhas_solicitacoes_fechar_contato, name='minhas_solicitacoes_fechar_contato'),
    url(r'^funcionario/minhas_solicitacoes/(?P<solicitacao_id>[0-9]+)/fechar/visto/$', minhas_solicitacoes_fechar_visto, name='minhas_solicitacoes_fechar_visto'),

    # modulo RH
    url(r'^rh/', include('rh.urls', namespace="rh")),
    # modulo recepcao
    url(r'^recepcao/', include('cadastro.urls', namespace="cadastro")),
    # modulo comercial
    url(r'^comercial/', include('comercial.urls', namespace="comercial")),
    # modulo solicitacao
    url(r'^solicitacao/', include('solicitacao.urls', namespace="solicitacao")),
    # modulo estoque
    url(r'^estoque/', include('estoque.urls', namespace="estoque")),
    # modulo programacao
    url(r'^programacao/', include('programacao.urls', namespace="programacao")),
    # modulo financeiro
    url(r'^financeiro/', include('financeiro.urls', namespace="financeiro")),
    # ajax helpers
    url(r'^ajax/consulta/produtos.json$', ajax_consulta_produto, name='ajax_consulta_produto'),
    url(r'^ajax/consulta/cargos.json$', ajax_consulta_cargo, name='ajax_consulta_cargo'),
]

from django.conf import settings

# apps condicionais
if 'retscreen' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^retscreen/', include('retscreen.urls', namespace="retscreen")))

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
