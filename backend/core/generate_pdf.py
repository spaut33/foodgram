from io import BytesIO

from django.conf import settings
from reportlab.lib import styles
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import registerFontFamily, registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph


class PDFFile:
    """Класс PDF-файла из элементов"""
    # TODO: Сделать заголовок и футер как на сайте

    FONT_FAMILY = 'Montserrat'
    FONT = {
        f'{FONT_FAMILY}-Regular': f'{FONT_FAMILY}-Regular.ttf',
        f'{FONT_FAMILY}-Bold': f'{FONT_FAMILY}-Bold.ttf',
        f'{FONT_FAMILY}-Italic': f'{FONT_FAMILY}-Italic.ttf',
        f'{FONT_FAMILY}-BoldItalic': f'{FONT_FAMILY}-BoldItalic.ttf',
    }

    def __init__(self):
        self.title = 'Foodgram - Продуктовый помощник'
        self.author = 'Roman Petrakov'
        self.subject = 'Список покупок'
        self.page_size = A4
        self.left_margin = 10 * mm
        self.right_margin = 10 * mm
        self.top_margin = 10 * mm
        self.bottom_margin = 10 * mm
        self.font_size = 14
        self.space_before = 12

        self.styles = styles.getSampleStyleSheet()
        self.set_styles()

        self.font_path = settings.STATIC_ROOT / 'fonts'
        self.register_fonts()

        self.pdf_file = None
        self.items = []

    def register_fonts(self):
        for font_variant, font_file in self.FONT.items():
            registerFont(TTFont(font_variant, self.font_path / font_file))

        registerFontFamily(
            self.FONT_FAMILY,
            normal=f'{self.FONT_FAMILY}-Regular',
            bold=f'{self.FONT_FAMILY}-Bold',
            italic=f'{self.FONT_FAMILY}-Italic',
            boldItalic=f'{self.FONT_FAMILY}-BoldItalic',
        )

    def set_styles(self):
        self.styles.add(
            ParagraphStyle(
                name='regular',
                fontName=f'{self.FONT_FAMILY}-Regular',
                fontSize=self.font_size,
                leading=self.font_size + 1,
                spaceBefore=self.space_before,
                spaceAfter=self.space_before // 2,
                alignment=TA_LEFT,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='footer',
                fontName=f'{self.FONT_FAMILY}-Bold',
                fontSize=self.font_size,
                leading=self.font_size + 1,
                spaceBefore=self.space_before,
                spaceAfter=self.space_before // 2,
                alignment=TA_LEFT,
            )
        )

    @property
    def regular_style(self):
        return self.styles['regular']

    @property
    def footer_style(self):
        return self.styles['footer']

    def add_item(self, item):
        """Метод для добавления элементов файла"""
        self.items.append(item)

    def generate_body(self):
        """Метод для генерации текста из элементов"""
        return [Paragraph(item, self.regular_style) for item in self.items]

    def create(self):
        buffer = BytesIO()
        pdf_file = SimpleDocTemplate(
            buffer,
            title=self.title,
            author=self.author,
            subject=self.subject,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            pagesize=self.page_size,
        )
        pdf_file.build(self.generate_body())
        buffer.seek(0)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def get_content(self):
        """Метод для сохранения файла"""
        return self.create()
