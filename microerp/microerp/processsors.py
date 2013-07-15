
from django.conf import settings
def logo_empresa(request):
    logo_empresa = getattr(settings, 'IMG_SRC_LOGO_EMPRESA', None)
    mostra_menu_principal_lateral = getattr(settings, 'MOSTRAR_MENU_PRINCIPAL_LATERAL', True)
    return {
        'logo_empresa': logo_empresa,
        'mostra_menu_principal_lateral': mostra_menu_principal_lateral,
        }
