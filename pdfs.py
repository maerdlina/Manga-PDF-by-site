import pytesseract
import os
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
import tempfile

# Укажите полный путь к tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_chapter_id_from_url(url):
    """Извлечь chapter_id из URL изображения."""
    base_part = "https://cdn-s.manga-italia.com/72c9ca30d2e6127f691e153d3d1865af/"
    end_part = "/1.webp"

    # Проверяем, начинается ли URL с базовой части и содержит ли конечную часть
    if url.startswith(base_part) and end_part in url:
        # Извлекаем часть между базовой и конечной частями
        after_base = url[len(base_part):]
        chapter_id = after_base.split(end_part)[0]  # Извлекаем часть до конечной части
        return chapter_id
    return None

def extract_chapter_id_from_page(chapter_number):
    """Извлечь уникальный идентификатор главы с первой страницы."""
    url = f"https://scanita.org/scan/{chapter_number}/1"  # Страница с изображением для первой страницы главы
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Ошибка при загрузке страницы: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    img_div = soup.find('div', class_='col text-center book-page')

    if img_div:
        img_tag = img_div.find('img')
        if img_tag and 'src' in img_tag.attrs:
            img_src = img_tag['src']
            chapter_id = extract_chapter_id_from_url(img_src)  # Извлекаем chapter_id из URL изображения
            return chapter_id
    return None

def get_image_url(chapter_number, page_number, chapter_identifiers):
    """Сформировать URL изображения для заданной главы и страницы."""
    # Получаем уникальный идентификатор для текущей главы
    chapter_id = chapter_identifiers.get(chapter_number)
    if not chapter_id:
        raise Exception(f"Идентификатор для главы {chapter_number} не найден")

    # Формируем URL изображения
    img_url = f"https://cdn-s.manga-italia.com/72c9ca30d2e6127f691e153d3d1865af/{chapter_id}/{page_number}.webp?token=GENERATED_TOKEN&expires=GENERATED_EXPIRE_TIME"
    return img_url

def download_image(img_url):
    """Скачать изображение и преобразовать в формат для PDF."""
    try:
        response = requests.get(img_url)
        if response.status_code != 200:
            raise Exception(f"Ошибка при загрузке изображения: {response.status_code}")

        # Открываем изображение из байтового потока
        img = Image.open(BytesIO(response.content))

        # Преобразуем изображение в формат RGB, чтобы оно было совместимо с PDF
        img = img.convert('RGB')
        return img
    except Exception as e:
        print(f"Ошибка при загрузке или обработке изображения: {e}")
        return None

def create_pdf_for_chapter(chapter_number, images, output_folder, base_chapter_number=75852):
    """Создать PDF файл для главы, используя изображения."""
    adjusted_chapter_number = chapter_number - base_chapter_number
    pdf_filename = os.path.join(output_folder, f"Onepunchman {adjusted_chapter_number}.pdf")
    c = None

    for img in images:
        if img:
            img_width, img_height = img.size
            # Если это первая страница, создаем объект canvas
            if not c:
                c = canvas.Canvas(pdf_filename, pagesize=(img_width, img_height))

            # Устанавливаем размер страницы под размер изображения
            c.setPageSize((img_width, img_height))

            # Сохраняем изображение во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_img_file:
                img.save(temp_img_file, 'JPEG')
                temp_img_path = temp_img_file.name

            # Добавляем изображение на страницу PDF
            c.drawImage(temp_img_path, 0, 0, width=img_width, height=img_height)
            c.showPage()  # Добавляем новую страницу для следующего изображения

            # Удаляем временный файл
            os.remove(temp_img_path)

    if c:
        c.save()  # Сохраняем PDF
        print(f"PDF для главы {chapter_number} сохранен как {pdf_filename}")
    else:
        print(f"Не удалось создать PDF для главы {chapter_number}: изображения отсутствуют.")

def main():
    start_chapter = 75853
    end_chapter = 75870
    pages_per_chapter = 100  # Предполагаемое максимальное количество страниц

    chapter_identifiers = {}

    # Извлекаем идентификаторы для всех глав в диапазоне
    for chapter_number in range(start_chapter, end_chapter + 1):
        try:
            chapter_id = extract_chapter_id_from_page(chapter_number)
            if chapter_id:
                chapter_identifiers[chapter_number] = chapter_id  # Добавляем идентификатор в словарь
        except Exception as e:
            print(f"Произошла ошибка при извлечении идентификатора для главы {chapter_number}: {e}")

    output_folder = "pdf_files"
    os.makedirs(output_folder, exist_ok=True)

    # Создаем PDF для каждой главы
    for chapter_number in range(start_chapter, end_chapter + 1):
        images = []
        try:
            for page_number in range(1, pages_per_chapter + 1):
                img_url = get_image_url(chapter_number, page_number, chapter_identifiers)
                print(f"Image URL for chapter {chapter_number}, page {page_number}: {img_url}")

                img = download_image(img_url)  # Загружаем изображение
                if img:
                    images.append(img)  # Добавляем изображение в список
                else:
                    print(f"Прекращение загрузки для главы {chapter_number}, так как изображение {page_number} отсутствует.")
                    break  # Прерываем цикл поиска страниц

            # Создаем PDF для главы только если есть изображения
            if images:
                create_pdf_for_chapter(chapter_number, images, output_folder)
            else:
                print(f"Для главы {chapter_number} не удалось загрузить изображения.")

        except Exception as e:
            print(f"Произошла ошибка при обработке главы {chapter_number}: {e}")

if __name__ == "__main__":
    main()
