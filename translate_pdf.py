import os
from PyPDF2 import PdfReader, PdfWriter  # Updated imports
from deep_translator import GoogleTranslator
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Установка языкового пары для перевода
src_lang = 'auto'  # Исходный язык (автоопределение)
dst_lang = 'ru'  # Язык, на который будет производиться перевод

# Путь к исходному PDF файлу
input_pdf ='./pdf_files/Onepunchman 1.pdf'

# Путь к выходному PDF файлу
output_pdf = 'Onepunchman 1 translated.pdf'

# Создание объекта PdfReader для чтения исходного PDF файла
pdf = PdfReader(input_pdf)

# Создание объекта PdfWriter для записи переведенного PDF
output = PdfWriter()

# Цикл по страницам исходного PDF файла
for page_num in range(len(pdf.pages)):
    page = pdf.pages[page_num]

    # Извлечение текста с текущей страницы
    text = page.extract_text().strip()

    # Перевод текста с помощью Google Translator
    translated_text = GoogleTranslator(source=src_lang, target=dst_lang).translate(text)

    # Создание нового PDF с отформатированным текстом
    new_pdf = canvas.Canvas(f'page_{page_num + 1}.pdf', pagesize=letter)

    # Добавление переведенного текста на страницу
    stylesheet = getSampleStyleSheet()
    translated_paragraph = Paragraph(translated_text, stylesheet['BodyText'])
    translated_paragraph.wrapOn(new_pdf, 500, 500)  # Ограничение размеров текста
    translated_paragraph.drawOn(new_pdf, 50, 500)  # Положение текста

    # Закрытие нового PDF файла
    new_pdf.save()

    # Чтение нового PDF файла и добавление его страниц в выходной PDF
    with open(f'page_{page_num + 1}.pdf', 'rb') as f:
        translated_page = PdfReader(f)
        output.add_page(translated_page.pages[0])  # Updated to use add_page

# Запись переведенного PDF файла
with open(output_pdf, 'wb') as f:
    output.write(f)

# Удаление временных файлов
for page_num in range(len(pdf.pages)):
    os.remove(f'page_{page_num + 1}.pdf')

print(f'Переведенный PDF сохранен в файл: {output_pdf}')
