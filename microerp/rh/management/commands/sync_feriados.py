from django.core.management.base import BaseCommand
import urllib2
from icalendar import Calendar
from rh.models import Feriado

class Command(BaseCommand):
    help = "Sincroniza feriados."

    def handle(self, *args, **options):
        '''Populate Brazilian holidays'''
        url = "https://www.google.com/calendar/ical/pt_br.brazilian%23holiday%40group.v.calendar.google.com/public/basic.ics"
        u = urllib2.urlopen(url)
        r = u.read()
        u.close()
        gcal = Calendar.from_ical(r)
        datas = []
        for component in gcal.walk():
            if component.name == "VEVENT":
                uid = component.get('uid')
                nome = component.get('summary')
                data = component.get('dtstart').dt
                if data:
                    f,created = Feriado.objects.get_or_create(uid=uid, data=data, nome=nome, importado_por_sync=True)
                    f.save()
        