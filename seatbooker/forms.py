from django import forms
from .models import Service

class RegisterForm(forms.Form):
    active = Service.objects.filter(active=True)
    name = forms.CharField(label='Name', max_length=150)
    #email = forms.EmailField(label='Email', max_length=150)
    #num_people = forms.IntegerField(label='Number of attendees', min_value=1)

    def __init__(self, seat, *args, **kwargs):
        self.seat = seat
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['num_people'] = forms.IntegerField(
            label='Number of attendees', 
            min_value=1, 
            max_value=self.seat.capacity)

class SearchForm(forms.Form):
    query = forms.CharField(label='Enter your name (case-sensitive)', max_length=150)