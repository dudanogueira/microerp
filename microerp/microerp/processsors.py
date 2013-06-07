
from django.conf import settings
def logo_empresa(request):
    logo_empresa = getattr(settings, 'IMG_SRC_LOGO_EMPRESA', None)
    return {'logo_empresa': logo_empresa}
