from django.db import models
import datetime, pytz

# Create your models here.
class Service(models.Model):
    date = models.DateTimeField()
    num_attendees = models.IntegerField(default=0)
    seats_occupied = models.IntegerField(default=0)
    has_seats = models.BooleanField(default=True)
    capacity = models.IntegerField(default=30)
    active = models.BooleanField(default=True)
    secA_seats = models.IntegerField(default=6)
    secB_seats = models.IntegerField(default=8)
    secC_seats = models.IntegerField(default=8)
    secD_seats = models.IntegerField(default=6)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.has_seats:
            for i in range(4):
                label = chr(65 + i) + '01'
                Seat.objects.create(seat_id=label, service=self, 
                    booked=True, reserved_by='Worship Coworker', 
                    reservation_size=1)

            for i in range(2, self.secA_seats + 1):
                label = 'A0' + str(i) if i < 10 else 'A' + str(i)
                if i == self.secA_seats:
                    Seat.objects.create(seat_id=label, service=self, 
                        booked=True, reserved_by='Usher', 
                        reservation_size=1)
                elif i == 2 or i == 4:
                    Seat.objects.create(seat_id=label, service=self, capacity=3)
                else:
                    Seat.objects.create(seat_id=label, service=self, capacity=4)

            for i in range(2, self.secB_seats + 1):
                label = 'B0' + str(i) if i < 10 else 'B' + str(i)
                if i == self.secB_seats:
                    Seat.objects.create(seat_id=label, service=self, 
                        booked=True, reserved_by='Usher', 
                        reservation_size=1)
                elif i == 2 or i == 3 or i == 6:
                    Seat.objects.create(seat_id=label, service=self, capacity=3)
                elif i == 4 or i == 5:
                    Seat.objects.create(seat_id=label, service=self, capacity=4)
                elif i == 7:
                    Seat.objects.create(seat_id=label, service=self, capacity=2)
                else:
                    Seat.objects.create(seat_id=label, service=self)

            for i in range(2, self.secC_seats + 1):
                label = 'C0' + str(i) if i < 10 else 'C' + str(i)
                if i == self.secB_seats:
                    Seat.objects.create(seat_id=label, service=self, 
                        booked=True, reserved_by='Usher', 
                        reservation_size=1)
                elif i == 2 or i == 3 or i == 6:
                    Seat.objects.create(seat_id=label, service=self, capacity=3)
                elif i == 4 or i == 5:
                    Seat.objects.create(seat_id=label, service=self, capacity=4)
                elif i == 7:
                    Seat.objects.create(seat_id=label, service=self, capacity=2)
                else:
                    Seat.objects.create(seat_id=label, service=self)

            for i in range(2, self.secD_seats + 1):
                label = 'D0' + str(i) if i < 10 else 'D' + str(i)
                if i == self.secD_seats:
                    Seat.objects.create(seat_id=label, service=self)
                elif i == 2 or i == 4:
                    Seat.objects.create(seat_id=label, service=self, capacity=3)
                else:
                    Seat.objects.create(seat_id=label, service=self, capacity=4)
               
            self.has_seats = True
            self.seats_occupied = 7
            self.num_attendees = 7
            super().save(*args, **kwargs)
            
    def delete(self, *args, **kwargs):
        seats = Seat.objects.filter(service=self)
        for seat in seats:
            seat.delete()
        super(Service, self).delete(*args, **kwargs)

    def __str__(self):
        eastern = pytz.timezone("US/Eastern")
        return self.date.astimezone(eastern).strftime('%m/%d/%Y %-I:%M %p')

class Seat(models.Model):
    service = models.ForeignKey('Service', null=True, on_delete=models.CASCADE)
    seat_id = models.CharField(max_length=3)
    booked = models.BooleanField(default=False)
    reserved_by = models.CharField(max_length=150, null=True, blank=True)
    reservation_size = models.IntegerField(null=True, blank=True)
    capacity = models.IntegerField(default=1)

    def __init__(self, *args, **kwargs):
        super(Seat, self).__init__(*args, **kwargs)
        self.old_state = self.booked
        if not self.reservation_size:
            self.old_num = 0
        else:
            self.old_num = self.reservation_size

    def save(self, *args, **kwargs):
        if self.old_state and not self.booked:
            self.service.num_attendees -= self.old_num
            self.service.seats_occupied -= 1
            self.service.save()
        elif self.service.has_seats and not self.old_num == self.reservation_size:
            self.service.num_attendees -= self.old_num
            if self.reservation_size:
                self.service.num_attendees += self.reservation_size
            self.service.save()
            
        self.old_state = self.booked
        self.old_num = self.reservation_size
        super(Seat, self).save(*args, **kwargs)

    def __str__(self):
        return "Seat " + str(self.seat_id)