from io import BytesIO

from django.conf import settings

from reportlab.lib import colors, styles
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


class PDFFile:
    """Класс PDF-файла из элементов"""

    FONT_FAMILY = 'Montserrat'
    FONT = {
        f'{FONT_FAMILY}-Regular': f'{FONT_FAMILY}-Regular.ttf',
        f'{FONT_FAMILY}-Bold': f'{FONT_FAMILY}-Bold.ttf',
        f'{FONT_FAMILY}-Italic': f'{FONT_FAMILY}-Italic.ttf',
        f'{FONT_FAMILY}-BoldItalic': f'{FONT_FAMILY}-BoldItalic.ttf',
    }

    def __init__(self):
        self.title = 'Продуктовый помощник'
        self.author = 'Roman Petrakov'
        self.subject = 'Список покупок'
        self.page_size = A4
        self.left_margin = 10 * mm
        self.right_margin = 10 * mm
        self.top_margin = 10 * mm
        self.bottom_margin = 10 * mm
        self.space_before = 12
        self.footer_height = 30 * mm
        self.body_fontsize = 12
        self.header_fontsize = 16
        self.footer_fontsize = 12
        self.offset_multiplier = 2
        self.leading_add = 1
        # инициализация стилей reportlab и установка их в дефолтное значение
        self.styles = styles.getSampleStyleSheet()
        self.set_styles()
        # регистрация фонтов
        self.font_path = settings.STATIC_ROOT / 'fonts'
        self.register_fonts()

        self.pdf_file = None
        self.items = []

    def register_fonts(self):
        """Загрузка и регистрация TTF фонтов"""
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
        """Задание стилей"""
        self.styles.add(
            ParagraphStyle(
                name='regular',
                fontName=f'{self.FONT_FAMILY}-Regular',
                fontSize=self.body_fontsize,
                leading=self.body_fontsize + self.leading_add,
                spaceBefore=self.space_before,
                spaceAfter=self.space_before // self.offset_multiplier,
                alignment=TA_LEFT,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='footer',
                fontName=f'{self.FONT_FAMILY}-Bold',
                fontSize=self.body_fontsize,
                leading=self.body_fontsize + self.leading_add,
                spaceBefore=self.space_before,
                spaceAfter=self.space_before // self.offset_multiplier,
                alignment=TA_LEFT,
            )
        )

    @property
    def regular_style(self):
        """Возвращает стиль основной страницы"""
        return self.styles['regular']

    @property
    def footer_style(self):
        """Возвращает стиль футера"""
        return self.styles['footer']

    @property
    def table_style(self):
        """Возвращает стиль таблицы"""
        return TableStyle(
            [
                ('FONTNAME', (0, 0), (-1, -1), f'{self.FONT_FAMILY}-Regular'),
                ('FONTSIZE', (0, 0), (-1, -1), self.body_fontsize),
                (
                    'LEADING',
                    (0, 0),
                    (-1, -1),
                    self.body_fontsize + self.leading_add,
                ),
            ]
        )

    def add_item(self, item):
        """Метод для добавления элементов файла"""
        self.items.append(item)

    def generate_body(self):
        """Метод для генерации текста из элементов"""
        return [Paragraph(item, self.regular_style) for item in self.items]

    def generate_table(self):
        """Метод для генерации таблицы из элементов"""
        return [Table(self.items, style=self.table_style)]

    def generate_footer(self, canvas, doc):
        """Генерирует футер для страниц"""
        canvas.setFillColor(colors.black)
        # Default: x=0, y=0, width=page width, height=footer height
        canvas.rect(0, 0, self.page_size[0], self.footer_height, fill=True)
        canvas.setFillColor(colors.white)
        canvas.setFont('Montserrat-Bold', self.footer_fontsize)
        canvas.drawString(
            self.bottom_margin // self.offset_multiplier * mm,
            self.bottom_margin // self.offset_multiplier * mm,
            f'{self.title}',
        )
        canvas.drawString(
            self.page_size[0]
            - self.bottom_margin // self.offset_multiplier * mm,
            self.bottom_margin // self.offset_multiplier * mm,
            f'{doc.page}',
        )

    def template_first_page(self, canvas, doc):
        """Устанавливает шаблон первой страницы"""
        canvas.saveState()
        canvas.setFont('Montserrat-Bold', self.header_fontsize)
        canvas.drawCentredString(
            self.page_size[0] // self.offset_multiplier,
            self.page_size[1] - self.top_margin // self.offset_multiplier * mm,
            'Список покупок',
        )
        self.generate_footer(canvas, doc)
        canvas.restoreState()

    def template_later_pages(self, canvas, doc):
        """Устанавливает шаблон последующих страниц"""
        canvas.saveState()
        self.generate_footer(canvas, doc)
        canvas.restoreState()

    def create(self):
        """Создание файла, заполнение шаблона"""
        buffer = BytesIO()
        pdf_file = SimpleDocTemplate(
            buffer,
            title=self.title,
            author=self.author,
            subject=self.subject,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=self.top_margin * self.offset_multiplier,
            bottomMargin=self.footer_height + self.bottom_margin,
            pagesize=self.page_size,
        )
        # Создание файла из таблицы, используя шаблоны первой и последующих
        # страниц
        pdf_file.build(
            self.generate_table(),
            onFirstPage=self.template_first_page,
            onLaterPages=self.template_later_pages,
        )
        buffer.seek(0)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf  # noqa: R504

    def get_content(self):
        """Метод для сохранения файла"""
        return self.create()
