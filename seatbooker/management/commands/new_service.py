from django.core.management.base import BaseCommand, CommandError
from seatbooker.models import Service, Seat
from mysite.settings import BASE_DIR, MEDIA_ROOT, EMAIL_HOST_USER
import os, datetime, csv
from django.core.mail import EmailMessage
import tempfile, shutil

class Command(BaseCommand):
    help = 'Create a new service and closes last service'

    def handle(self, *args, **kwargs):
        #Set the oldest service to be non-active
        oldest = Service.objects.filter(active=True).order_by('date')[0]
        oldest.active = False
        oldest.save()
        
        #Create service data file (temporary)
        filepath = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
        filename = os.path.join(filepath, 'attendees-' + str(oldest.date)[:11] + '.csv')

        attendee_data = open(filename, 'w')
        writer = csv.writer(attendee_data)
        writer.writerow(['Name', 'Seat', 'Number of people'])

        #Write all data to file
        for a in Seat.objects.filter(service=oldest):
            if a.reserved_by:
                writer.writerow([a.reserved_by, a.seat_id, a.reservation_size])

        writer.writerow(['Total attendees',str(oldest.num_attendees),''])
        writer.writerow(['Total seats occupied',str(oldest.seats_occupied),''])
        
        attendee_data.close()
        
        #Create new service one week from the latest
        newest = Service.objects.filter(active=True).order_by('-date')[0]
        d = datetime.timedelta(days=7)
        service = Service(date=newest.date + d, capacity=newest.capacity, has_seats=True)
        service.save()

        #Email data
        mail = EmailMessage(
            'WCEC: Service Data for ' + str(oldest), 
            'Service Data for ' + str(oldest), 
            EMAIL_HOST_USER, 
            [EMAIL_HOST_USER]
        )

        content = open(filename, 'rb').read()
        mail.attach(
            filename, content, 'text/csv')
        mail.send()

        shutil.rmtree(filepath)