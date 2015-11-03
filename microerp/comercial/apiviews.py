from comercial.serializers import *
from comercial.models import FollowUpDePropostaComercial
from cadastro.models import Cliente, PreCliente
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q


# ViewSets define the view behavior.
class FollowUpDePropostaComercialViewSet(viewsets.ModelViewSet):
    queryset = FollowUpDePropostaComercial.objects.all()[0:10]
    serializer_class = FollowUpDePropostaComercialSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    def get_queryset(self):
        queryset = Cliente.objects.all()
        query = self.request.query_params.get('q', None)
        if query:
            if self.request.user.perfilacessocomercial.super_gerente:
                queryset = queryset.filter(
                    Q(ativo=True) & \
                    Q(nome__icontains=query) | \
                    Q(fantasia__icontains=query) | \
                    Q(cnpj__icontains=query) | \
                    Q(cpf__icontains=query)
                )
            # puxa somente os da mesma empresa
            else:
                queryset = queryset.filter(
                    designado__user__perfilacessocomercial__empresa=self.request.user.perfilacessocomercial.empresa
                ).filter(
                    Q(ativo=True) & \
                    Q(nome__icontains=query) | \
                    Q(fantasia__icontains=query) | \
                    Q(cnpj__icontains=query) | \
                    Q(cpf__icontains=query)
                )
        return queryset

class PreClienteViewSet(viewsets.ModelViewSet):
    serializer_class = PreClienteSerializer

    def base_queryset(self):
        queryset = PreCliente.objects.all()
        if self.request.user.perfilacessocomercial.super_gerente:
                # todos os preclientes
                queryset = queryset.filter(
                    cliente_convertido=None
                )
        # puxa somente os da mesma empresa
        else:
            queryset = queryset.filter(
            designado__user__perfilacessocomercial__empresa=self.request.user.perfilacessocomercial.empresa,
            cliente_convertido=None
            )
        return queryset


    def get_queryset(self):
        queryset = self.base_queryset()
        query = self.request.query_params.get('q', None)
        queryset = queryset.filter(
                    Q(nome__icontains=query) | \
                    Q(cnpj__icontains=query) | \
                    Q(cpf__icontains=query)
                )
        query = self.request.query_params.get('q', None)
        if query:
            self.base_queryset()
        return queryset

    def retrieve(self, request, pk=None):
        queryset = self.base_queryset()
        precliente = get_object_or_404(queryset, pk=pk)
        serializer = PreClienteSerializer(precliente)
        return Response(serializer.data)