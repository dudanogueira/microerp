from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Calculo Retscreen'

    def calcula_retscreen(self, media, radiacao):
        pass

    def add_arguments(self, parser):
        parser.add_argument('media', nargs='+', type=float)
        parser.add_argument('tamanho_placa', nargs='+', type=float)

    def handle(self, *args, **options):
        print options
        media = options['media'][0]
        tamanho_placa = options['tamanho_placa'][0]
        radiacao = 4.81
        media_diaria = media / 30.00
        percentual_perda = (radiacao * 3) / 100
        perda = radiacao * percentual_perda
        radiacao_real = radiacao - perda
        tamanho_usina = (media_diaria / radiacao_real)
        numero_placas_sugerida = tamanho_usina / tamanho_placa
        

        print "Media", media
        print "Radiacao", radiacao
        print "Radiacao com Perda", perda
        print "Media Diaria", media_diaria
        print "Percentual Perda", percentual_perda
        print "Radiacao Real", radiacao_real
        print "Tamanho Usina", tamanho_usina
        print "Numero Placas Sugerida", numero_placas_sugerida



        self.stdout.write(
            self.style.SUCCESS('Media: %s' % media)
        )
        self.stdout.write(
            self.style.SUCCESS('Radiacao: %s' % radiacao)
        )
