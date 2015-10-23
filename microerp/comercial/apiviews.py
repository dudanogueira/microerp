from comercial.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cadastro.models import Cliente, PreCliente