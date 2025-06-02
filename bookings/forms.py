from django import forms
from .models import BookingRequest, Company, ROOM_CHOICES, STATUS_CHOICES
from django.utils import timezone
from datetime import time

class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['full_name', 'email', 'phone_number', 'company', 'room', 'purpose', 'date', 'start_time', 'end_time', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الاسم الكامل',
                'dir': 'rtl',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com',
                'dir': 'ltr',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '07xxxxxxxxx',
                'dir': 'ltr',
                'pattern': '[0-9]{10}',
            }),
            'company': forms.Select(attrs={
                'class': 'form-control form-select',
                'placeholder': 'اختر الشركة',
            }),
            'room': forms.Select(attrs={
                'class': 'form-control form-select',
                'placeholder': 'اختر القاعة',
            }),
            'purpose': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الغرض من الحجز',
                'dir': 'rtl',
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat(),
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'min': '08:00',
                'max': '20:00',
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'min': '08:00',
                'max': '20:00',
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'أي ملاحظات إضافية تود إضافتها...',
                'dir': 'rtl',
            }),
        }
        labels = {
            'full_name': 'الاسم الكامل',
            'email': 'البريد الإلكتروني',
            'phone_number': 'رقم الهاتف',
            'company': 'الشركة',
            'room': 'القاعة',
            'purpose': 'الغرض',
            'date': 'التاريخ',
            'start_time': 'وقت البدء',
            'end_time': 'وقت الانتهاء',
            'notes': 'ملاحظات إضافية',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إضافة classes للـ labels
        for field_name, field in self.fields.items():
            field.label_suffix = ''
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control-lg'
            if field_name in ['date', 'start_time', 'end_time']:
                field.widget.attrs['class'] += ' text-center'
            
            # جعل حقول الشركة والقاعة اختيارية
            if field_name in ['company', 'room']:
                field.required = False

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        room = cleaned_data.get('room')

        if start_time and end_time and date and room:
            # التحقق من تعارض الحجوزات لنفس القاعة (المقبولة والمعلقة)
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
                raise forms.ValidationError(error_message)

            if start_time >= end_time:
                raise forms.ValidationError('وقت الانتهاء يجب أن يكون بعد وقت البدء')

            # التحقق من أن وقت البدء والانتهاء ضمن ساعات العمل
            if start_time < time(8, 0) or end_time > time(20, 0):
                raise forms.ValidationError('وقت الحجز يجب أن يكون بين الساعة 8 صباحاً و 8 مساءً')

        if date:
            if date < timezone.now().date():
                raise forms.ValidationError('لا يمكن حجز موعد في الماضي')

        return cleaned_data