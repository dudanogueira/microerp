# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader, Context

from django import forms

from django.contrib import messages

from models import TabelaValores

class FormConfiguraRetscreen(forms.Form):
    fator = forms.DecimalField(label=u"Fator Energético", required=True, initial=0,  decimal_places=2)
    media = forms.DecimalField(label=u"Média de Consumo Energético", required=True)
    tamanho_placa = forms.DecimalField(label=u"Tamanho da Placa", required=True, initial=0.265)
    radiacao = forms.DecimalField(label=u"Radiação", required=True, initial=4.81)
    preco_eletricidade = forms.DecimalField(label=u"Preço da Eletricidade", initial=0.50974, required=True)
    quantidade_placa = forms.DecimalField(label=u"Quantidade de Placas", required=False)
    valor_final = forms.DecimalField(label=u"Valor Final", required=False)

def home(request):
    form = FormConfiguraRetscreen(request.POST or None)
    if request.POST and form.is_valid():
        messages.success(request, u"Sucesso!Form Válido")
        media = float(form.cleaned_data['media'])
        tamanho_placa = float(form.cleaned_data['tamanho_placa'])
        radiacao = float(form.cleaned_data['radiacao'])
        preco_eletricidade = float(form.cleaned_data['preco_eletricidade'])
        media_diaria = media / 30.00
        percentual_perda = (radiacao * 3) / 100
        perda = radiacao * percentual_perda
        radiacao_real = radiacao - perda
        tamanho_usina = (media_diaria / radiacao_real)
        if not form.cleaned_data['quantidade_placa']:
            numero_placas_sugerida = tamanho_usina / tamanho_placa
        else:
            numero_placas_sugerida = form.cleaned_data['quantidade_placa']
        # recacula tamanho da usina com quantidade de placas definida
        tamanho_usina = float(tamanho_placa) * float(numero_placas_sugerida)
        area_usina = float(numero_placas_sugerida) * 1.68
        geracao_kw_mes = tamanho_usina * 30 * radiacao_real
        geracao_kw_ano = geracao_kw_mes * 12
        economia_mensal = geracao_kw_mes * preco_eletricidade
        economia_anual = economia_mensal * 12
        tabela = TabelaValores.objects.get(
            quantidade_placas_inicial__lte=numero_placas_sugerida,
            quantidade_placas_final__gte=numero_placas_sugerida,
            )
        preco_por_watt = tabela.valor
        preco_sugerido = round(float(tamanho_usina) * float(preco_por_watt))
        if form.cleaned_data['fator'] != 0:
            preco_sugerido = preco_sugerido + (float(preco_sugerido) * float(form.cleaned_data['fator'])/100)
        retorno = {}
        if form.cleaned_data['valor_final']:
            preco_sugerido = float(form.cleaned_data['valor_final'])
        for i in range(0,26):
            retorno[i] = [preco_sugerido * -1, economia_anual]
            if i != 0:
                economia_no_ano = i * economia_anual
                reajuste_no_ano_anterior = retorno[i-1][1]
                reajuste_neste_ano = (reajuste_no_ano_anterior * 0.08) + reajuste_no_ano_anterior
                retorno[i] = [
                    ((i * reajuste_neste_ano) + reajuste_neste_ano) - preco_sugerido,
                    reajuste_neste_ano
                ]

        updated_data = request.POST.copy()
        updated_data.update(
            {
                'quantidade_placa': numero_placas_sugerida,
                'valor_final': preco_sugerido
            }
        )
        form = FormConfiguraRetscreen(data=updated_data)

    return render_to_response('frontend/retscreen/retscreen-home.html', locals(), context_instance=RequestContext(request),)
