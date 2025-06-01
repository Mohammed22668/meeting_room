from django.db import models

# Create your models here.

STATUS_CHOICES = [
 ('pending', 'معلق'),
    ('accepted', 'مقبول'),
    ('rejected', 'مرفوض'),
]  

class BookingRequest(models.Model):
    full_name = models.CharField(max_length=100 , verbose_name='الاسم الكامل')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    phone_number = models.CharField(max_length=20 , verbose_name='رقم الهاتف')
    purpose = models.TextField(verbose_name='الغرض')
    date = models.DateField(verbose_name='التاريخ')
    start_time = models.TimeField(verbose_name='الوقت البدء')
    end_time = models.TimeField(verbose_name='الوقت الانتهاء')
    notes = models.TextField(blank=True, null=True , verbose_name='الملاحظات')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending' , verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True , verbose_name='تاريخ الإنشاء')

    def __str__(self):
        return f"{self.full_name} - {self.date} ({self.start_time} - {self.end_time})"
