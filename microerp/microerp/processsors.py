
from django.conf import settings
def logo_empresa(request):
    logo_empresa = getattr(settings, 'IMG_SRC_LOGO_EMPRESA', None)
    ambiente_testes = getattr(settings, 'AMBIENTE_TESTES', False)
    mostra_menu_principal_lateral = getattr(settings, 'MOSTRAR_MENU_PRINCIPAL_LATERAL', True)
    rh_usa_banco_de_horas = getattr(settings, 'RH_USA_BANCO_DE_HORAS', True)
    nome_sistema = getattr(settings, 'NOME_SISTEMA', 'Microerp')
    return {
        'nome_sistema': nome_sistema,
        'logo_empresa': logo_empresa,
        'mostra_menu_principal_lateral': mostra_menu_principal_lateral,
        'rh_usa_banco_de_horas': rh_usa_banco_de_horas,
        'ambiente_testes': ambiente_testes,
        }
