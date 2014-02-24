from django.core.management.base import BaseCommand
from optparse import make_option
import xlrd

from producao.models import Componente, ComponenteTipo

class Command(BaseCommand):
    help = "Importa os Componentes com Base na Planilha Mestria"
    option_list = BaseCommand.option_list + (
    make_option('--file',
            action='store_true',
            dest='arquivo',
            help='Importa uma nota fiscal',
        ),
    )

    def handle(self, *args, **options):
        arquivo = options.get('arquivo')
        if arquivo:
            f = args[0]
            print "Arquivo: %s" % f
            workbook = xlrd.open_workbook(f)
            worksheet = workbook.sheets()[0]
            for curr_row in range(worksheet.nrows):
                if curr_row > 1:
                    row = worksheet.row(curr_row)
                    
                    print '-'*50
                    print "LINHA:", curr_row
                    part_number = row[0].value 
                    print "PART NUBER:", part_number
                    tipo_slug = part_number.split("-")[1][0:3]
                    print "TIPO:", tipo_slug
                    # identificador da categoria
                    identificador = int(part_number.split("-")[1][3:])
                    print "IDENTIFICADOR", identificador
                    inativo = row[13].value
                    if inativo:
                        marcado_ativo = False
                    else:
                        marcado_ativo = True
                    marcado_ativo = True
                    print "ATIVO:", marcado_ativo
                    importado_nacional = row[5].value
                    print "IMPORTADO/NACIONAL:", importado_nacional
                    descricao = row[6].value
                    print "DESCRICAO:", descricao
                    try:
                        lead_time = int(row[7].value)
                    except:
                        lead_time = 1
                    print "LEADTIME:", lead_time
                    pmu = row[8].value
                    if not pmu:
                        pmu = 0
                    pmu = float(str(pmu).replace(',', '.'))
                    print "PMU - Preco Medio Unitario", pmu
                    medida = row[10].value
                    if medida == 'U':
                        medida = 'und'
                    else:
                        medida = 'm'
                    print "MEDIDA", medida
                    ########
                    #cria na base de dados
                    # tipo de componente 
                    
                    tipo,created = ComponenteTipo.objects.get_or_create(
                        slug=tipo_slug
                    )
                    tipo.nome = tipo_slug
                    tipo.save()
                    componente,created = Componente.objects.get_or_create(
                        part_number = part_number,
                        tipo=tipo,
                        identificador=identificador,
                        lead_time=lead_time,
                    )
                    componente.ativo = marcado_ativo
                    componente.nacionalidade = importado_nacional.lower()
                    componente.descricao=descricao
                    componente.lead_time=lead_time
                    componente.preco_medio_unitario=pmu
                    componente.medida = medida
                    componente.save()

                    
            
        else:
            print "Especifique um arquivo com --file"