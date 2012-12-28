from django import forms
from models import ContatoComercial


class ContatoComercialAdd(forms.ModelForm):
    
    class Meta:
        model = ContatoComercial
        fields = ('nome', 'cliente', 'o_dia_todo','inicio', 'fim', 'tipo')