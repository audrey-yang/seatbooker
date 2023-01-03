from django.urls import path, include
from . import views
app_name = 'seatbooker'

urlpatterns = [
    path('', views.index, name='index'),
    path('confirm/<int:pk>', views.confirm, name='confirm'),
    path('thanks', views.finished, name='finished'),
    path('search', views.search, name='search')
]