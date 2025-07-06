# events/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/book/', views.book_ticket, name='book_ticket'),
    path('event/<int:event_id>/confirm/', views.confirm_booking, name='confirm_booking'),  # next step
    path('event/<int:event_id>/payment/', views.payment, name='payment'),
     path('register/', views.register, name='register'),


]
