from django.db import models

# Create your models here.

STATUS_CHOICES = [
 ('pending', 'قيد الانتظار'),
    ('accepted', 'مقبول'),
    ('rejected', 'مرفوض'),
]  

ROOM_CHOICES = [
    ('room1', 'قاعة الاجتماعات الرئيسية/16 شخص'),
    ('room2', 'قاعة  تدريب مجموعة مارينا/24 شخص'),
]

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم الشركة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'شركة'
        verbose_name_plural = 'الشركات'

class BookingRequest(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='الاسم الكامل')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    phone_number = models.CharField(max_length=20, verbose_name='رقم الهاتف')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='الشركة' , null=True, blank=True)
    room = models.CharField(max_length=10, choices=ROOM_CHOICES, verbose_name='القاعة' , null=True, blank=True)
    purpose = models.TextField(verbose_name='الغرض')
    date = models.DateField(verbose_name='التاريخ')
    start_time = models.TimeField(verbose_name='وقت البدء')
    end_time = models.TimeField(verbose_name='وقت الانتهاء')
    notes = models.TextField(blank=True, null=True, verbose_name='الملاحظات')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    def __str__(self):
        return f"{self.full_name} - {self.date} ({self.start_time} - {self.end_time})"
    
    
    class Meta:
        verbose_name = 'طلب حجز'
        verbose_name_plural = 'طلبات الحجز'
