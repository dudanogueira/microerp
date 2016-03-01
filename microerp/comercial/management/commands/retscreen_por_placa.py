from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Calculo Retscreen'

    def calcula_retscreen(self, media, radiacao):
        pass

    def add_arguments(self, parser):
        parser.add_argument('quantidade_placa', nargs='+', type=float)
        parser.add_argument('preco_eletricidade', nargs='+', type=float)

    def handle(self, *args, **options):
        quantidade_placa = options['quantidade_placa'][0]
        preco_eletricidade = options['preco_eletricidade'][0]

        radiacao = 4.81
        percentual_perda = (radiacao * 3) / 100
        perda = radiacao * percentual_perda
        radiacao_real = radiacao - perda
        tamanho_usina = quantidade_placa * 0.260
        area_usina = quantidade_placa * 1.68
        tabela = [
            [0, 7, 10600],
            [8, 20, 8000],
            [21, 30, 8300],
            [30, 32, 8200],
            [33, 100, 7000]
        ]
        for a in tabela:
            if a[0] <= quantidade_placa and a[1] >= quantidade_placa:
                preco_por_watt = a[2]
        preco_sugerido = tamanho_usina * preco_por_watt
        geracao_kw_mes = tamanho_usina * 30 * radiacao_real
        geracao_kw_ano = geracao_kw_mes * 12
        economia_mensal = geracao_kw_mes * preco_eletricidade
        economia_anual = economia_mensal * 12

        retorno = {}
        for i in range(0,25):
            retorno[i] = [preco_sugerido * -1, economia_anual]
            if i != 0:
                economia_no_ano = i * economia_anual
                reajuste_no_ano_anterior = retorno[i-1][1]
                reajuste_neste_ano = (reajuste_no_ano_anterior * 0.08) + reajuste_no_ano_anterior
                retorno[i] = [
                    ((i * reajuste_neste_ano) + reajuste_neste_ano) - preco_sugerido,
                    reajuste_neste_ano
                ]
        print retorno

        print "Tamanho Usina", tamanho_usina
        print "Area Usina", area_usina
        print "Preco por Watt", preco_por_watt
        print "Preco Sugerido", preco_sugerido
        print "Geracao KW MES", geracao_kw_mes
        print "Geracao KW Ano", geracao_kw_ano
        print "Economia Mensal", economia_mensal
        print "Economia Anual", economia_anual
