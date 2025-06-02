from django.contrib import admin
from .models import BookingRequest, Company
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

class BookingRequestResource(resources.ModelResource):
    status_display = Field(attribute='status', column_name='الحالة')
    room_display = Field(attribute='room', column_name='القاعة')
    company_name = Field(attribute='company__name', column_name='الشركة')
    
    class Meta:
        model = BookingRequest
        fields = ('id', 'full_name', 'email', 'phone_number', 'company_name', 'room_display', 
                 'purpose', 'date', 'start_time', 'end_time', 'notes', 'status_display', 'created_at')
        export_order = fields
        import_id_fields = ['id']

class CompanyResource(resources.ModelResource):
    class Meta:
        model = Company
        fields = ('id', 'name', 'created_at')
        export_order = fields
        import_id_fields = ['id']

@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 20

@admin.register(BookingRequest)
class BookingRequestAdmin(ImportExportModelAdmin):
    resource_class = BookingRequestResource
    list_display = ('id', 'full_name', 'email', 'room', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'room', 'date')
    list_display_links = ('id', 'full_name')
    search_fields = ('full_name', 'email', 'purpose')
    readonly_fields = ('id',)
    actions = ['send_test_email']

    def send_test_email(self, request, queryset):
        for booking in queryset:
            try:
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
                    subject='اختبار: تم قبول طلب حجز القاعة',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, f'تم إرسال بريد اختبار إلى {booking.email}')
            except Exception as e:
                messages.error(request, f'فشل إرسال البريد إلى {booking.email}: {str(e)}')
    
    send_test_email.short_description = "إرسال بريد اختبار للحجوزات المحددة"

    fieldsets = (
        ('معلومات الحجز', {
            'fields': ('full_name', 'email', 'phone_number', 'company', 'room')
        }),
        ('تفاصيل الموعد', {
            'fields': ('date', 'start_time', 'end_time', 'purpose')
        }),
        ('معلومات إضافية', {
            'fields': ('notes', 'status'),
            'classes': ('collapse',)
        }),
    )
