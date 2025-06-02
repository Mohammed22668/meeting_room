from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import arabic_reshaper
from bidi.algorithm import get_display
import os
from django.conf import settings
from datetime import datetime
from .models import ROOM_CHOICES, STATUS_CHOICES

def ensure_directories():
    """التأكد من وجود المجلدات المطلوبة"""
    # التأكد من وجود مجلد MEDIA_ROOT
    if not hasattr(settings, 'MEDIA_ROOT') or not settings.MEDIA_ROOT:
        media_root = os.path.join(settings.BASE_DIR, 'media')
    else:
        media_root = settings.MEDIA_ROOT
    
    # إنشاء مجلد pdfs إذا لم يكن موجوداً
    pdfs_dir = os.path.join(media_root, 'pdfs')
    os.makedirs(pdfs_dir, exist_ok=True)
    
    return pdfs_dir

def register_arabic_font():
    """تسجيل الخط العربي"""
    try:
        # محاولة العثور على الخط في المسارات المختلفة
        font_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Cairo-Regular.ttf'),
            os.path.join(settings.BASE_DIR, 'bookings', 'static', 'fonts', 'Cairo-Regular.ttf'),
            os.path.join(settings.STATIC_ROOT, 'fonts', 'Cairo-Regular.ttf') if hasattr(settings, 'STATIC_ROOT') else None,
        ]
        
        # إزالة المسارات الفارغة
        font_paths = [path for path in font_paths if path]
        
        # البحث عن أول مسار صالح
        font_path = next((path for path in font_paths if os.path.exists(path)), None)
        
        if font_path:
            pdfmetrics.registerFont(TTFont('Cairo', font_path))
            return True
        return False
    except Exception as e:
        print(f"Error registering font: {e}")
        return False

def create_booking_pdf(booking):
    """إنشاء ملف PDF لتأكيد الحجز"""
    try:
        # التأكد من وجود المجلدات
        pdfs_dir = ensure_directories()
        
        # إنشاء اسم الملف
        filename = f"booking_confirmation_{booking.id}.pdf"
        filepath = os.path.join(pdfs_dir, filename)
        
        # تسجيل الخط العربي
        has_arabic_font = register_arabic_font()
        if not has_arabic_font:
            print("Warning: Arabic font not found, using default font")
        
        # إنشاء المستند
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # قائمة العناصر التي سيتم إضافتها للمستند
        elements = []
        
        # إضافة العنوان
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=getSampleStyleSheet()['Title'],
            fontName='Cairo' if has_arabic_font else 'Helvetica',
            fontSize=24,
            spaceAfter=30,
            alignment=1  # توسيط
        )
        title = Paragraph(get_display(arabic_reshaper.reshape("تأكيد حجز القاعة")), title_style)
        elements.append(title)
        
        # إضافة معلومات الحجز
        data = [
            [get_display(arabic_reshaper.reshape("الاسم الكامل")), get_display(arabic_reshaper.reshape(booking.full_name))],
            [get_display(arabic_reshaper.reshape("البريد الإلكتروني")), booking.email],
            [get_display(arabic_reshaper.reshape("رقم الهاتف")), booking.phone_number],
            [get_display(arabic_reshaper.reshape("الشركة")), get_display(arabic_reshaper.reshape(booking.company.name)) if booking.company else "-"],
            [get_display(arabic_reshaper.reshape("القاعة")), get_display(arabic_reshaper.reshape(dict(ROOM_CHOICES)[booking.room])) if booking.room else "-"],
            [get_display(arabic_reshaper.reshape("التاريخ")), booking.date.strftime("%Y-%m-%d")],
            [get_display(arabic_reshaper.reshape("وقت البدء")), booking.start_time.strftime("%I:%M %p")],
            [get_display(arabic_reshaper.reshape("وقت الانتهاء")), booking.end_time.strftime("%I:%M %p")],
            [get_display(arabic_reshaper.reshape("الغرض")), get_display(arabic_reshaper.reshape(booking.purpose))],
            [get_display(arabic_reshaper.reshape("الملاحظات")), get_display(arabic_reshaper.reshape(booking.notes)) if booking.notes else "-"],
            [get_display(arabic_reshaper.reshape("الحالة")), get_display(arabic_reshaper.reshape(dict(STATUS_CHOICES)[booking.status]))],
            [get_display(arabic_reshaper.reshape("تاريخ الطلب")), booking.created_at.strftime("%Y-%m-%d %I:%M %p")],
        ]
        
        # إنشاء الجدول
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Cairo' if has_arabic_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # إضافة تذييل الصفحة
        footer_style = ParagraphStyle(
            'CustomFooter',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Cairo' if has_arabic_font else 'Helvetica',
            fontSize=10,
            alignment=1,
            textColor=colors.grey
        )
        footer = Paragraph(
            get_display(arabic_reshaper.reshape("مجموعة مارينا - نظام حجز القاعات")),
            footer_style
        )
        elements.append(footer)
        
        # بناء المستند
        doc.build(elements)
        
        # التأكد من أن الملف تم إنشاؤه بنجاح
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Failed to create PDF file at {filepath}")
        
        # التأكد من أن الملف غير فارغ
        if os.path.getsize(filepath) == 0:
            raise ValueError(f"Created PDF file is empty: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        raise 