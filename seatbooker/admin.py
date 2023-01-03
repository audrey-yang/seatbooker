from django.contrib import admin
from django.core.management import call_command
from django.urls import path, reverse
from django.utils.html import mark_safe
from django.shortcuts import render
from django.http import HttpResponseRedirect
import datetime

from django.contrib.auth.models import Group
from .models import Seat, Service

admin.site.site_header = 'WCEC Seat Booker Administration'

class ServiceAdmin(admin.ModelAdmin):
    ordering = ['-date']

    list_display = (
        'date',
        'seats_link',
        'num_attendees',
        'seats_occupied',
        'capacity',
        'active',
    )
    
    change_list_template = 'admin/service_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('new', self.new_service),
        ]
        return new_urls + urls

    def seats_link(self, service):
        link = reverse("admin:seatbooker_seat_changelist")
        return mark_safe(u'<a href="%s?service_id__exact=%d">Seats</a>' % (
            link, service.id))

    def new_service(self, request):
        if 'continue' in request.POST:
            call_command('new_service')
            new_service = Service.objects.order_by('-date')[0]
            new_service.secA_seats = int(request.POST.get('secA'))
            new_service.secB_seats = int(request.POST.get('secB'))
            new_service.secC_seats = int(request.POST.get('secC'))
            new_service.secD_seats = int(request.POST.get('secD'))
            new_service.capacity = int(request.POST.get('capacity'))
            new_service.has_seats = False
            new_service.save()
            self.message_user(request, 'Created new service for ' + str(new_service) + '.')
            return HttpResponseRedirect('../../')
        elif 'back' in request.POST:
            return HttpResponseRedirect('../') 

        newest = Service.objects.filter(active=True).order_by('-date')[0]
        next_date = newest.date + datetime.timedelta(days=7)

        return render(request,
                    'admin/confirm_action.html',
                    context={
                        'date': str(next_date)[:11],
                        'secA': newest.secA_seats,
                        'secB': newest.secB_seats,
                        'secC': newest.secC_seats,
                        'secD': newest.secD_seats,
                        'capacity': newest.capacity
                    }) 

class SeatAdmin(admin.ModelAdmin):
    ordering = ['service', 'seat_id']

    list_display = (
        'seat_id',
        'service',
        'booked',
        'reserved_by',
        'reservation_size'
    )

    list_filter = ['service']

# Register your models here.
admin.site.register(Service, ServiceAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.unregister(Group)