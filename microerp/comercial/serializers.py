from rest_framework import serializers
from comercial.models import FollowUpDePropostaComercial
from comercial.models import EmpresaComercial
from cadastro.models import Cliente, PreCliente
from rh.models import Funcionario

# BUSCA PRE / CLIENTES


class FuncionarioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Funcionario
        fields = ('nome', 'foto')

class ClienteSerializer(serializers.HyperlinkedModelSerializer):
    designado = FuncionarioSerializer()
    class Meta:
        model = Cliente
        fields = ('nome', 'tipo', 'designado')

class PreClienteSerializer(serializers.HyperlinkedModelSerializer):
    designado = FuncionarioSerializer()
    class Meta:
        model = PreCliente
        fields = ('id', 'nome', 'tipo', 'telefone_fixo', 'telefone_celular', 'designado')


class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmpresaComercial
        fields = ('nome', 'logo')

class FollowUpDePropostaComercialSerializer(serializers.ModelSerializer):
    criado_por = FuncionarioSerializer()
    empresa = EmpresaSerializer(source='criado_por.user.perfilacessocomercial.empresa')
    cliente = ClienteSerializer(source='proposta.cliente')
    precliente = PreClienteSerializer(source='proposta.precliente')

    class Meta:
        model = FollowUpDePropostaComercial
        fields = (
                'empresa',
                'proposta',
                'cliente',
                'precliente',
                'texto',
                'reagenda_data_expiracao',
                'data_expiracao',
                'probabilidade',
                'visita',
                'visita_por',
                'criado_por',
                'criado'
        )
        looakup_field = 'funcionario__user__perfilacessocomercial__empresa__nome'