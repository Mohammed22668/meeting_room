from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch, cm
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

def process_arabic_text(text):
    """معالجة النص العربي للعرض الصحيح"""
    if not text:
        return "-"
    try:
        # إضافة مسافة في نهاية النص إذا كان يحتوي على نص عربي
        if any('\u0600' <= char <= '\u06FF' for char in text):
            text = text + ' '
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Error processing Arabic text: {e}")
        return text

def register_arabic_font():
    """تسجيل الخط العربي"""
    try:
        # قائمة المسارات المحتملة للخطوط
        font_paths = []
        
        # مسارات Windows
        if os.name == 'nt':  # Windows
            windows_fonts = [
                'C:\\Windows\\Fonts\\arial.ttf',
                'C:\\Windows\\Fonts\\arialbd.ttf',
                'C:\\Windows\\Fonts\\ariali.ttf',
                'C:\\Windows\\Fonts\\arialbi.ttf',
                'C:\\Windows\\Fonts\\simsun.ttc',
                'C:\\Windows\\Fonts\\simhei.ttf',
            ]
            font_paths.extend(windows_fonts)
        
        # مسارات Linux
        elif os.name == 'posix':  # Linux/Unix
            linux_fonts = [
                # مسارات Noto
                '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
                '/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf',
                '/usr/share/fonts/noto/NotoSansArabic-Regular.ttf',
                '/usr/share/fonts/noto/NotoSansArabic-Bold.ttf',
                # مسارات Liberation
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                '/usr/share/fonts/liberation/LiberationSans-Regular.ttf',
                '/usr/share/fonts/liberation/LiberationSans-Bold.ttf',
                # مسارات DejaVu
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/dejavu/DejaVuSans.ttf',
                # مسارات إضافية
                '/usr/share/fonts/truetype/arabic/arabic.ttf',
                '/usr/share/fonts/truetype/arabic/arabic-bold.ttf',
                # مسارات النظام
                '/usr/share/fonts/TTF/arial.ttf',
                '/usr/share/fonts/TTF/arialbd.ttf',
                '/usr/share/fonts/TTF/ariali.ttf',
                '/usr/share/fonts/TTF/arialbi.ttf',
            ]
            font_paths.extend(linux_fonts)
            
            # البحث في مجلدات الخطوط الإضافية
            additional_font_dirs = [
                '/usr/local/share/fonts',
                os.path.expanduser('~/.fonts'),
                os.path.expanduser('~/.local/share/fonts'),
            ]
            
            for font_dir in additional_font_dirs:
                if os.path.exists(font_dir):
                    for root, dirs, files in os.walk(font_dir):
                        for file in files:
                            if file.endswith(('.ttf', '.otf')):
                                font_paths.append(os.path.join(root, file))
        
        # البحث عن الخط في المسارات المتاحة
        for font_path in font_paths:
            if os.path.exists(font_path):
                print(f"Using font from: {font_path}")
                pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                return True
        
        # إذا لم يتم العثور على أي خط، استخدم الخط الافتراضي
        print("No suitable font found, using default font")
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
            rightMargin=0.8*cm,
            leftMargin=0.8*cm,
            topMargin=0.8*cm,
            bottomMargin=0.8*cm
        )
        
        # قائمة العناصر التي سيتم إضافتها للمستند
        elements = []
        
        # إضافة الشعار
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo', 'marina-logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*inch))
        
        # إضافة العنوان
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=getSampleStyleSheet()['Title'],
            fontName='ArabicFont' if has_arabic_font else 'Helvetica',
            fontSize=20,
            spaceAfter=20,
            alignment=1,  # توسيط
            leading=24,  # المسافة بين الأسطر
            allowWidows=0,
            allowOrphans=0,
            textColor=colors.HexColor('#1a237e')  # لون أزرق داكن
        )
        title = Paragraph(process_arabic_text("تأكيد حجز القاعة"), title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # إضافة معلومات الحجز
        data = [
            [process_arabic_text(booking.full_name), process_arabic_text("الاسم الكامل")],
            [booking.email, process_arabic_text("البريد الإلكتروني")],
            [booking.phone_number, process_arabic_text("رقم الهاتف")],
            [process_arabic_text(booking.company.name) if booking.company else "-", process_arabic_text("الشركة")],
            [process_arabic_text(dict(ROOM_CHOICES)[booking.room]) if booking.room else "-", process_arabic_text("القاعة")],
            [booking.date.strftime("%Y-%m-%d"), process_arabic_text("التاريخ")],
            [booking.start_time.strftime("%I:%M %p"), process_arabic_text("وقت البدء")],
            [booking.end_time.strftime("%I:%M %p"), process_arabic_text("وقت الانتهاء")],
            [process_arabic_text(booking.purpose), process_arabic_text("الغرض")],
            [process_arabic_text(booking.notes) if booking.notes else "-", process_arabic_text("الملاحظات")],
            [process_arabic_text(dict(STATUS_CHOICES)[booking.status]), process_arabic_text("الحالة")],
            [booking.created_at.strftime("%Y-%m-%d %I:%M %p"), process_arabic_text("تاريخ الطلب")],
        ]
        
        # إنشاء الجدول
        table = Table(data, colWidths=[3.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#e8eaf6')),  # لون خلفية فاتح
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont' if has_arabic_font else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a237e')),  # لون الشبكة أزرق داكن
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEADING', (0, 0), (-1, -1), 12),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),  # تناوب ألوان الصفوف
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # إضافة تذييل الصفحة
        footer_style = ParagraphStyle(
            'CustomFooter',
            parent=getSampleStyleSheet()['Normal'],
            fontName='ArabicFont' if has_arabic_font else 'Helvetica',
            fontSize=9,
            alignment=1,
            textColor=colors.HexColor('#1a237e'),  # لون أزرق داكن
            leading=11,
            allowWidows=0,
            allowOrphans=0
        )
        footer = Paragraph(
            process_arabic_text("مجموعة مارينا - نظام حجز القاعات"),
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