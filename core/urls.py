from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    # HTML Views
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('scan/', views.scan_attendance, name='scan_attendance'),
    path('scan-qr/', views.scan_qr_camera, name='scan_qr'),
    path('pay/<int:event_id>/', views.fake_payment, name='fake_payment'),
    path('success/<int:booking_id>/', views.booking_success, name='booking_success'), 
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('choose-role/', views.choose_role, name='choose_role'),
    # path('after-login/', views.after_login_view, name='after_login'),
    path('events/create/', views.create_event, name='create_event'),
    path('organizer/bookings/', views.organizer_bookings, name='organizer_bookings'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),


    # JSON APIs
    path('api/events/', views.api_event_list, name='api_event_list'),
    path('api/events/<int:event_id>/', views.api_event_detail, name='api_event_detail'),
    path('api/book/<int:event_id>/', views.book_ticket, name='book_ticket'), 
    path('api/qr/<int:booking_id>/', views.download_qr_code),           # Download QR
    path('api/attend/<str:ticket_id>/', views.mark_attendance),   
    path('api/payment-webhook/', views.payment_webhook, name='payment_webhook'),
    path('attendance/', views.mark_attendance, name='attendance'),
    path('download-pdf/<int:booking_id>/', views.download_ticket_pdf, name='download_ticket_pdf'),



 
]
