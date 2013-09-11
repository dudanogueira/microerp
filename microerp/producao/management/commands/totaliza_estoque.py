from django.core.management.base import BaseCommand

from producao.models import Componente
from producao.models import EstoqueFisico
from producao.models import RegistroValorEstoque

class Command(BaseCommand):
    help = "Totaliza o estoque e registra na base de dados"

    def handle(self, *args, **options):
        valor_total = 0
        for componente in Componente.objects.all():
            print "COMPONENTE: %s" % componente
            total_em_estoques = 0
            #calcular a posicao do componente em todos os estoques
            for estoque in EstoqueFisico.objects.all():
                total_em_estoques += componente.posicao_no_estoque(estoque)
            valor_parcial = float(total_em_estoques) * float(componente.preco_liquido_unitario_real)
            print "VALOR PARCIAL: %s" % valor_parcial
            valor_total += valor_parcial
            print "VALOR TOTAL: %s" % valor_total
            print "####" * 10
        print "VALOR TOTAL:",valor_total
        registro = RegistroValorEstoque.objects.create(
            valor=valor_total
        )
        

                
        