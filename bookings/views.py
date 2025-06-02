from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .models import BookingRequest, ROOM_CHOICES, STATUS_CHOICES
from .forms import BookingRequestForm
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings





def booking_form(request):
    form = BookingRequestForm()
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            room = form.cleaned_data.get('room')
            
            # تحقق من تعارض الحجوزات المقبولة والمعلقة
            conflict_exists = BookingRequest.objects.filter(
                date=date,
                room=room,
                status__in=['accepted', 'pending'],
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if conflict_exists:
                # البحث عن الحجز المتعارض للحصول على تفاصيله
                conflicting_booking = BookingRequest.objects.filter(
                    date=date,
                    room=room,
                    status__in=['accepted', 'pending'],
                    start_time__lt=end_time,
                    end_time__gt=start_time
                ).first()

                status_display = dict(STATUS_CHOICES)[conflicting_booking.status]
                room_display = dict(ROOM_CHOICES)[conflicting_booking.room]
                
                error_message = f'هذه القاعة ({room_display}) محجوزة في هذا الوقت من قبل {conflicting_booking.full_name} ({status_display})'
                messages.error(request, error_message)
                return render(request, 'bookings/booking_form.html', {'form': form})
            
            # حفظ الطلب
            booking = form.save(commit=False)
            booking.status = 'pending'
            booking.save()
            messages.success(request, "تم تقديم طلب الحجز بنجاح، في انتظار الموافقة.")
            return redirect('booking_success', booking_id=booking.id)

    # جلب بيانات الأسبوع الحالي
    today = timezone.localdate()
    start_week = today - timedelta(days=today.weekday())  # بداية الأسبوع (الاثنين)
    end_week = start_week + timedelta(days=6)  # نهاية الأسبوع (الأحد)

    # جلب جميع الحجوزات خلال الأسبوع
    bookings_qs = BookingRequest.objects.filter(date__range=[start_week, end_week])

    # تجهيز بيانات الأحداث للكالندر
    bookings_events = []
    
    for b in bookings_qs:
        start_dt = timezone.make_aware(timezone.datetime.combine(b.date, b.start_time))
        end_dt = timezone.make_aware(timezone.datetime.combine(b.date, b.end_time))
        color = {
            'pending': '#ffc107',  # أصفر
            'accepted': '#198754',  # أخضر
            'rejected': '#dc3545',  # أحمر
        }.get(b.status, '#6c757d')  # رمادي افتراضي

        event_data = {
            'title': f"{b.full_name} ({b.purpose})",
            'start': start_dt,
            'end': end_dt,
            'color': color,
        }

        # إضافة معلومات الشركة والقاعة إذا كانت متوفرة
        if b.company:
            event_data['company'] = b.company.name
        if b.room:
            event_data['room'] = dict(ROOM_CHOICES)[b.room]

        bookings_events.append(event_data)

    bookings_json = json.dumps(bookings_events, cls=DjangoJSONEncoder)

    context = {
        'form': form,
        'bookings': bookings_json,
    }
    return render(request, 'bookings/booking_form.html', context)




# class BookingRequestCreateView(CreateView):
#     model = BookingRequest
#     form_class = BookingRequestForm
#     template_name = 'bookings/booking_form.html'

#     def form_valid(self, form):
#         booking = form.save()
#         return redirect('booking_success', booking_id=booking.id)

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

def send_booking_accepted_email(booking):
    """إرسال بريد إلكتروني عند قبول الحجز"""
    subject = 'تم قبول طلب حجز القاعة'
    
    # إنشاء رابط متابعة الحجز
    tracking_url = f"{settings.SITE_URL}/track/{booking.id}/"
    
    # تحضير سياق القالب
    context = {
        'booking': booking,
        'tracking_url': tracking_url
    }
    
    # تحميل قالب HTML
    html_message = render_to_string('bookings/email/booking_accepted.html', context)
    plain_message = strip_tags(html_message)
    
    # إرسال البريد الإلكتروني
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.email],
        html_message=html_message,
        fail_silently=False,
    )

def accept_booking(request, booking_id):
    """قبول طلب الحجز وإرسال بريد إلكتروني"""
    try:
        booking = BookingRequest.objects.get(id=booking_id)
        booking.status = 'accepted'
        booking.save()
        
        # إرسال بريد إلكتروني
        send_booking_accepted_email(booking)
        
        messages.success(request, 'تم قبول الحجز وإرسال تأكيد بالبريد الإلكتروني.')
    except BookingRequest.DoesNotExist:
        messages.error(request, 'لم يتم العثور على طلب الحجز.')
    
    return redirect('admin_bookings')  # أو أي صفحة أخرى تريد التوجيه إليها

