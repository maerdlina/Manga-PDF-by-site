import pytesseract
import os
import requests
from bs4 import BeautifulSoup

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

def download_image(img_url, chapter_number, page_number, folder):
    """Скачать изображение и сохранить в указанную папку."""
    response = requests.get(img_url)
    if response.status_code != 200:
        raise Exception(f"Ошибка при загрузке изображения: {response.status_code}")

    filename = f'capitolo_{chapter_number}_pagina_{page_number}.jpg'  # Формат имени файла
    file_path = os.path.join(folder, filename)  # Путь к файлу
    with open(file_path, 'wb') as f:
        f.write(response.content)
    print(f"Изображение сохранено как {file_path}")

def main():
    start_chapter = 75853
    end_chapter = 75856  # 117600
    pages_per_chapter = 35  # Замените на реальное количество страниц, если оно известно

    chapter_identifiers = {}

    # Извлекаем идентификаторы для всех глав в диапазоне
    for chapter_number in range(start_chapter, end_chapter + 1):
        try:
            chapter_id = extract_chapter_id_from_page(chapter_number)
            if chapter_id:
                chapter_identifiers[chapter_number] = chapter_id  # Добавляем идентификатор в словарь
        except Exception as e:
            print(f"Произошла ошибка при извлечении идентификатора для главы {chapter_number}: {e}")

    # Скачиваем изображения для каждой главы
    for chapter_number in range(start_chapter, end_chapter + 1):
        folder = str(chapter_number)  # Имя папки — номер главы
        os.makedirs(folder, exist_ok=True)

        try:
            for page_number in range(1, pages_per_chapter + 1):
                img_url = get_image_url(chapter_number, page_number, chapter_identifiers)
                print(f"Image URL for chapter {chapter_number}, page {page_number}: {img_url}")

                download_image(img_url, chapter_number, page_number, folder)

        except Exception as e:
            print(f"Произошла ошибка при обработке главы {chapter_number}: {e}")

if __name__ == "__main__":
    main()
