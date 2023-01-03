from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import Seat, Service
from .forms import RegisterForm, SearchForm
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout

def index(request):
    if Service.objects.all():
        service1 = Service.objects.filter(active=True).order_by('date')[0]
        service2 = Service.objects.filter(active=True).order_by('date')[1]
        service3 = Service.objects.filter(active=True).order_by('date')[2]
        service4 = Service.objects.filter(active=True).order_by('date')[3]
        service5 = Service.objects.filter(active=True).order_by('date')[4]

        curr = service1
        clicked = 1
        if request.method == 'POST':
            if 'service2' in request.POST:
                curr = service2
                clicked = 2
            elif 'service3' in request.POST:
                curr = service3
                clicked = 3
            elif 'service4' in request.POST:
                curr = service4
                clicked = 4
            elif 'service5' in request.POST:
                curr = service5
                clicked = 5
        
        seatsA = Seat.objects.filter(service=curr).filter(seat_id__startswith='A').order_by('seat_id')
        seatsB = Seat.objects.filter(service=curr).filter(seat_id__startswith='B').order_by('seat_id')
        seatsC = Seat.objects.filter(service=curr).filter(seat_id__startswith='C').order_by('seat_id')
        seatsD = Seat.objects.filter(service=curr).filter(seat_id__startswith='D').order_by('seat_id')
        
        return render(request, 
            'index.html', 
            context={
                'seatsA': seatsA,
                'seatsB': seatsB,
                'seatsC': seatsC,
                'seatsD': seatsD,
                'curr': curr,
                'service1': service1,
                'service2': service2,
                'service3': service3,
                'service4': service4,
                'service5': service5,
                'clicked': clicked
            })
    return HttpResponse('No services yet!')

def confirm(request, pk):
    seat = get_object_or_404(Seat, pk=pk)

    if request.method == "POST":
        form = RegisterForm(seat=seat, data=request.POST)
        service = seat.service
        if form.is_valid():
            name = form.cleaned_data.get('name')
            num_people = form.cleaned_data.get('num_people')

            seat = get_object_or_404(Seat, pk=pk)
            seat.booked = True
            seat.reserved_by = name
            seat.reservation_size = num_people
            seat.save()
            
            service.num_attendees += num_people
            service.seats_occupied += 1
            service.save()

            '''
            people = ' people. ' if num_people > 1 else ' person. '
            message_text = (
                'Hello, ' + name + '!\n\n' + 
                'Thank you for registering for the WCEC Sunday Service on ' + str(service) + 
                ' at 11:00 AM for ' + str(num_people) + people + 
                'Your seat is ' + str(seat) + '. ' + 
                'This service is designed to meet government guidelines and be as ' + 
                'safe as possible. Masks and social distancing are required. \n\n' +
                'If you did not reserve this seat or if there is any other problem, please ' + 
                'contact us at wcec.media@gmail.com.\n\n' +
                'Thank you!')

            send_mail(
                'CONFIRMATION: WCEC Service Registration',
                message_text,
                'wcecnotify@gmail.com',
                [email],
                fail_silently=False,
            )
            '''
            
            return redirect('seatbooker:finished')
        else:
            return render(request=request, 
                  template_name="confirm.html", 
                  context={
                        'form':form,
                        'seat':seat,
                        'messages':form._errors})
            
    form = RegisterForm(seat=seat)
    return render(request=request, 
                  template_name="confirm.html", 
                  context={
                        'form':form,
                        'seat':seat,
                        'messages':form._errors})

def finished(request):
    return render(request, 'finished.html')

def search(request):
    if request.method == 'POST':
        form = SearchForm(data=request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            possible = Seat.objects.filter(
                service__active=True).filter(reserved_by__contains=query)

            return render(request, 
                    template_name='search.html',
                    context={
                        'form': form,
                        'matches': possible,
                        'no_matches': len(possible) == 0
                    })
    
    form = SearchForm()
    return render(request=request, 
                  template_name="search.html", 
                  context={
                      'form':form,
                    })

