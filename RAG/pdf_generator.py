"""
Генератор PDF документов для реферативных переводов
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
import re
from datetime import datetime
from typing import Optional


class PDFGenerator:
    """Генератор PDF с поддержкой кириллицы и красивым форматированием."""
    
    def __init__(self):
        self.fonts_registered = False
        print("[PDF_GENERATOR] PDFGenerator initialized")
    
    def _register_fonts(self):
        """Регистрирует шрифты для поддержки кириллицы."""
        if self.fonts_registered:
            return
        
        try:
            # Пытаемся использовать системные шрифты DejaVu (есть в большинстве Linux систем)
            fonts_to_try = [
                # Linux paths
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                # Docker Alpine paths
                '/usr/share/fonts/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
            ]
            
            regular_font = None
            bold_font = None
            
            for font_path in fonts_to_try:
                if os.path.exists(font_path):
                    if 'Bold' in font_path:
                        bold_font = font_path
                    else:
                        regular_font = font_path
            
            if regular_font:
                pdfmetrics.registerFont(TTFont('DejaVuSans', regular_font))
                print(f"[PDF_GENERATOR] Registered font: DejaVuSans from {regular_font}")
            
            if bold_font:
                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font))
                print(f"[PDF_GENERATOR] Registered font: DejaVuSans-Bold from {bold_font}")
            
            self.fonts_registered = True
            print("[PDF_GENERATOR] Fonts registered successfully")
            
        except Exception as e:
            print(f"[PDF_GENERATOR] Warning: Could not register fonts: {e}")
            print("[PDF_GENERATOR] Using default fonts (Cyrillic may not work properly)")
            self.fonts_registered = False
    
    def _create_styles(self):
        """Создает стили для документа."""
        styles = getSampleStyleSheet()
        
        # Определяем шрифт
        font_name = 'DejaVuSans' if self.fonts_registered else 'Helvetica'
        bold_font = 'DejaVuSans-Bold' if self.fonts_registered else 'Helvetica-Bold'
        
        # Стиль для заголовка
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=bold_font
        ))
        
        # Стиль для подзаголовков
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=12,
            fontName=bold_font
        ))
        
        # Стиль для основного текста
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName=font_name
        ))
        
        # Стиль для метаданных
        styles.add(ParagraphStyle(
            name='Metadata',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#7f8c8d'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName=font_name
        ))
        
        return styles
    
    def _parse_markdown_to_pdf_elements(self, text: str, styles):
        """
        Преобразует Markdown-подобный текст в элементы PDF.
        Обрабатывает заголовки, списки, жирный текст и т.д.
        """
        elements = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Пустая строка
            if not line:
                elements.append(Spacer(1, 0.3*cm))
                i += 1
                continue
            
            # Заголовок уровня 1 (## Заголовок)
            if line.startswith('## '):
                title = line[3:].strip()
                elements.append(Spacer(1, 0.5*cm))
                elements.append(Paragraph(title, styles['CustomHeading']))
                i += 1
                continue
            
            # Заголовок уровня 2 (### Подзаголовок)
            if line.startswith('### '):
                subtitle = line[4:].strip()
                elements.append(Spacer(1, 0.3*cm))
                elements.append(Paragraph(f"<b>{subtitle}</b>", styles['CustomBody']))
                i += 1
                continue
            
            # Маркированный список
            if line.startswith('- ') or line.startswith('* '):
                bullet_text = line[2:].strip()
                # Обработка жирного текста **text**
                bullet_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', bullet_text)
                elements.append(Paragraph(f"• {bullet_text}", styles['CustomBody']))
                i += 1
                continue
            
            # Нумерованный список
            if re.match(r'^\d+\.\s', line):
                list_text = re.sub(r'^\d+\.\s', '', line)
                # Обработка жирного текста
                list_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', list_text)
                elements.append(Paragraph(list_text, styles['CustomBody']))
                i += 1
                continue
            
            # Обычный текст
            # Обработка жирного текста **text**
            line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            elements.append(Paragraph(line, styles['CustomBody']))
            i += 1
        
        return elements
    
    def generate_referat_pdf(
        self,
        referat_text: str,
        filename: str,
        output_path: str,
        original_filename: str,
        chunk_count: int,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Генерирует PDF файл реферативного перевода.
        
        Args:
            referat_text: текст реферативного перевода
            filename: имя выходного PDF файла
            output_path: путь для сохранения PDF
            original_filename: имя исходного документа
            chunk_count: количество фрагментов в документе
            metadata: дополнительные метаданные
            
        Returns:
            Полный путь к созданному PDF файлу
        """
        print(f"[PDF_GENERATOR] Generating PDF: {filename}")
        
        # Регистрируем шрифты
        self._register_fonts()
        
        # Создаем директорию если не существует
        os.makedirs(output_path, exist_ok=True)
        
        # Полный путь к файлу
        pdf_path = os.path.join(output_path, filename)
        
        # Создаем PDF документ
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Получаем стили
        styles = self._create_styles()
        
        # Создаем содержимое документа
        story = []
        
        # Заголовок
        story.append(Paragraph("Реферативный перевод", styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Метаданные
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        metadata_text = f"<b>Исходный документ:</b> {original_filename}<br/>"
        metadata_text += f"<b>Дата создания:</b> {current_date}<br/>"
        metadata_text += f"<b>Объем исходного документа:</b> {chunk_count} фрагментов"
        
        if metadata and metadata.get('language'):
            metadata_text += f"<br/><b>Язык:</b> {metadata['language']}"
        
        story.append(Paragraph(metadata_text, styles['Metadata']))
        story.append(Spacer(1, 0.8*cm))
        
        # Горизонтальная линия
        from reportlab.platypus import HRFlowable
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e0e0e0')))
        story.append(Spacer(1, 0.5*cm))
        
        # Основной текст реферата
        pdf_elements = self._parse_markdown_to_pdf_elements(referat_text, styles)
        story.extend(pdf_elements)
        
        # Строим PDF
        try:
            doc.build(story)
            print(f"[PDF_GENERATOR] PDF generated successfully: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"[PDF_GENERATOR] Error generating PDF: {e}")
            raise


# Глобальный экземпляр генератора
_pdf_generator_instance = None


def get_pdf_generator() -> PDFGenerator:
    """Получить глобальный экземпляр PDF генератора."""
    global _pdf_generator_instance
    if _pdf_generator_instance is None:
        _pdf_generator_instance = PDFGenerator()
    return _pdf_generator_instance

