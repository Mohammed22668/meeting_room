from django.apps import AppConfig
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'

    def ready(self):
        from .models import BookingRequest
        import bookings.signals  # تسجيل الإشارات
        logger = logging.getLogger(__name__)

        @receiver(post_save, sender=BookingRequest)
        def send_booking_status_email(sender, instance, created, **kwargs):
            if not created and instance.status == 'accepted':
                try:
                    # ... كود إرسال البريد ...
                    logger.info(f"تم إرسال بريد تأكيد الحجز إلى {instance.email}")
                except Exception as e:
                    logger.error(f"فشل إرسال البريد: {str(e)}")
