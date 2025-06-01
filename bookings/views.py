from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, TemplateView
from django.urls import reverse_lazy
from .models import BookingRequest
from .forms import BookingRequestForm


class BookingRequestCreateView(CreateView):
    model = BookingRequest
    form_class = BookingRequestForm
    template_name = 'bookings/booking_form.html'

    def form_valid(self, form):
        booking = form.save()
        return redirect('booking_success', booking_id=booking.id)

class BookingSuccessView(TemplateView):
    template_name = 'bookings/booking_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_id'] = self.kwargs['booking_id']
        return context

def home(request):
    return render(request, 'bookings/home.html')
def track_request_view(request):
    status = None
    booking = None
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        if booking_id and booking_id.isdigit():
            try:
                booking = BookingRequest.objects.get(id=int(booking_id))
                status = booking.get_status_display()
            except BookingRequest.DoesNotExist:
                status = 'طلب غير موجود.'
    return render(request, 'bookings/track_request.html', {'booking': booking, 'status': status})