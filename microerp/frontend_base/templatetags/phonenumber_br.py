from django import template
register = template.Library()

def phonenumber(value):
    if value:
        numero = ""
        for item in value:
            item = str(item)
            if item.isdigit():
                numero = "%s%s" % (numero, item)

        # XX-XXXX-XXXX
        if len(numero) == 10:
            phone = '%s-%s-%s' %(numero[0:2],numero[2:6],numero[6:])
        # XXXX-XXXX
        elif len(numero) == 8:
            phone = '%s-%s' %(numero[0:4],numero[4:8])
        else:
            phone = numero
        return phone

register.filter('phonenumber', phonenumber)