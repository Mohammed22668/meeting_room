from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookingRequest
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

@receiver(post_save, sender=BookingRequest)
def send_booking_status_email(sender, instance, created, **kwargs):
    """
    إرسال بريد إلكتروني عند تغيير حالة الحجز إلى مقبول
    """
    if not created and instance.status == 'accepted':
        # إنشاء رابط متابعة الحجز
        tracking_url = f"{settings.SITE_URL}/track/{instance.id}/"
        
        # تحضير سياق القالب
        context = {
            'booking': instance,
            'tracking_url': tracking_url
        }
        
        # تحميل قالب HTML
        html_message = render_to_string('bookings/email/booking_accepted.html', context)
        plain_message = strip_tags(html_message)
        
        # إرسال البريد الإلكتروني
        send_mail(
            subject='تم قبول طلب حجز القاعة',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            html_message=html_message,
            fail_silently=False,
        ) 