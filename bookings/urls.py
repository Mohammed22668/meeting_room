from django.urls import path
from .views import booking_form,  home, BookingSuccessView, track_request_view, accept_booking
from django.views.generic import TemplateView

urlpatterns = [
    path('', home, name='home'),
    # path('book/', BookingRequestCreateView.as_view(), name='booking_form'),
     path('book/', booking_form, name='booking_form'),
    path('book/success/<int:booking_id>/', BookingSuccessView.as_view(), name='booking_success'),
    path('track/', track_request_view, name='track_booking'),
    path('admin/booking/<int:booking_id>/accept/', accept_booking, name='accept_booking'),
]
