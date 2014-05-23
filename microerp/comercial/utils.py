# -*- coding: utf-8 -*-
ext = [{1:"um", 2:"dois", 3:"três", 4:"quatro", 5:"cinco", 6:"seis",
7:"sete", 8:"oito", 9:"nove", 10:"dez", 11:"onze", 12:"doze",
13:"treze", 14:"quatorze", 15:"quinze", 16:"dezesseis", 
17:"dezessete", 18:"dezoito", 19:"dezenove"}, {2:"vinte", 3:"trinta",
4:"quarenta", 5:"cinquenta", 6:"sessenta", 7:"setenta", 8:"oitenta",
9:"noventa"}, {1:"cento", 2:"duzentos", 3:"trezentos",
4:"quatrocentos", 5:"quinhentos", 6:"seissentos", 7:"setessentos",
8:"oitocentos", 9:"novecentos"}]

und = ['', ' mil', (' milhão', ' milhões'), (' bilhão', ' bilhões'),
(' trilhão', ' trilhões')]

def cent(s, grand):
    s = '0' * (3 - len(s)) + s
    if s == '000':
        return ''
    if s == '100': 
        return 'cem'
    ret = ''
    dez = s[1] + s[2]
    if s[0] != '0':
        ret += ext[2][int(s[0])]
        if dez != '00':
            ret += ' e '
        else:
            return ret + (type(und[grand]) == type(()) and (int(s) > 1 and und[grand][1] or und[grand][0]) or und[grand])
    if int(dez) < 20:
        ret += ext[0][int(dez)]
    else:
        if s[1] != '0':
            ret += ext[1][int(s[1])]
            if s[2] != '0':
                ret += ' e ' + ext[0][int(s[2])]
    
    return ret + (type(und[grand]) == type(()) and (int(s) > 1 and und[grand][1] or und[grand][0]) or und[grand])

def extenso(n, joinner=" e "):
    sn = str(int(n))
    ret = []
    grand = 0
    while sn:
        s = sn[-3:]
        sn = sn[:-3]
        ret.append(cent(s, grand))
        grand += 1
    ret.reverse()
    return joinner.join([r for r in ret if r])

def extenso_com_centavos(n):
    milhares = str(n).split(".")[0]
    centavos = str(n).split(".")[1]
    texto_milhares = extenso(milhares, joinner=', ')
    texto_centavos = extenso(centavos)
    return "%s reais e %s centavos" % (texto_milhares, texto_centavos)