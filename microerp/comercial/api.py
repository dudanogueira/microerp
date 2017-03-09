from rest_framework import routers, serializers, viewsets, filters
from rest_framework.pagination import PageNumberPagination
from models import ContratoFechado, CategoriaContratoFechado, PropostaComercial

from cadastro.models import Cliente
from rh.models import Funcionario

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000



class FuncionarioSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Funcionario
        fields = 'id', 'nome',


class FuncionarioViewSet(viewsets.ModelViewSet):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer



class ClienteSerializer(serializers.ModelSerializer):
    designado = FuncionarioSerializer()
    class Meta:
        model = Cliente
        #fields = 'nome', 'cnpj', 'cpf'
        #fields = '__all__'
        exclude = 'ramo', 'origem'


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer




class CategoriaContratoFechadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaContratoFechado
        fields = 'nome',

class PropostaComercialSerializer(serializers.ModelSerializer):
    definido_convertido_por = FuncionarioSerializer()
    designado = FuncionarioSerializer()
    criado_por = FuncionarioSerializer()

    class Meta:
        model = PropostaComercial
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    categoria = CategoriaContratoFechadoSerializer()
    propostacomercial = PropostaComercialSerializer()
    responsavel = FuncionarioSerializer()
    responsavel_comissionado = FuncionarioSerializer()
    funcionario_validador = FuncionarioSerializer()
    class Meta:
        model = ContratoFechado
        #fields = 'url', 'id', 'cliente', 'propostacomercial', 'tipo', 'categoria', 'valor', 'parcelas'
        fields = '__all__'
        
class ContratoViewSet(viewsets.ModelViewSet):
    queryset = ContratoFechado.objects.all()
    serializer_class = ContratoSerializer
    filter_backends = (filters.SearchFilter,)
    pagination_class = StandardResultsSetPagination
    search_fields = 'id', 'cliente__nome', 'cliente__cpf', 'cliente__cnpj'