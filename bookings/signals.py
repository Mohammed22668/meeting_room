from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookingRequest
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .pdf_generator import create_booking_pdf
import os

@receiver(post_save, sender=BookingRequest)
def send_booking_status_email(sender, instance, created, **kwargs):
    """
    إرسال بريد إلكتروني عند تغيير حالة الحجز إلى مقبول
    """
    if not created and instance.status == 'accepted':
        try:
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
            
            # إنشاء ملف PDF
            pdf_path = create_booking_pdf(instance)
            
            # إنشاء رسالة البريد الإلكتروني
            email = EmailMessage(
                subject='تم قبول طلب حجز القاعة',
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[instance.email],
            )
            
            # تعيين نوع المحتوى إلى HTML
            email.content_subtype = "html"
            
            # إرفاق ملف PDF
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    email.attach(
                        f'booking_confirmation_{instance.id}.pdf',
                        f.read(),
                        'application/pdf'
                    )
            
            # إرسال البريد الإلكتروني
            email.send(fail_silently=False)
            
        except Exception as e:
            print(f"Error sending email: {e}")
            raise 