from django.urls import path
from .views import (
    booking_form, home, BookingSuccessView, track_request_view,
    admin_login, admin_dashboard, admin_logout,
    accept_booking, reject_booking, edit_booking, delete_booking
)
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    # path('book/', BookingRequestCreateView.as_view(), name='booking_form'),
    path('book/', booking_form, name='booking_form'),
    path('book/success/<int:booking_id>/', BookingSuccessView.as_view(), name='booking_success'),
    path('track/', track_request_view, name='track_booking'),
    
    # Admin URLs
    path('booking-admin/login/', admin_login, name='admin_login'),
    path('booking-admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('booking-admin/logout/', admin_logout, name='admin_logout'),
    path('booking-admin/booking/<int:booking_id>/accept/', accept_booking, name='accept_booking'),
    path('booking-admin/booking/<int:booking_id>/reject/', reject_booking, name='reject_booking'),
    path('booking-admin/booking/<int:booking_id>/edit/', edit_booking, name='edit_booking'),
    path('booking-admin/booking/<int:booking_id>/delete/', delete_booking, name='delete_booking'),
]
