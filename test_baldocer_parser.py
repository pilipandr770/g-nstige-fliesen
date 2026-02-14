"""
Тест парсера Baldocer
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.manufacturer_parsers import ManufacturerParserFactory

def test_baldocer():
    """Тестирует парсер Baldocer"""
    print("="*80)
    print("ТЕСТ ПАРСЕРА BALDOCER")
    print("="*80)
    print()
    
    # Получаем парсер
    parser = ManufacturerParserFactory.get_parser('baldocer')
    if not parser:
        print("❌ Парсер не найден!")
        return
    
    print("✅ Парсер загружен\n")
    
    # 1. Тест извлечения логотипа
    print("1️⃣  ТЕСТ: Извлечение логотипа")
    print("-" * 80)
    logo = parser.extract_logo()
    if logo:
        print(f"✅ Логотип сохранен: {logo}\n")
    else:
        print("❌ Логотип не найден\n")
    
    # 2. Тест извлечения коллекций
    print("2️⃣  ТЕСТ: Извлечение коллекций")
    print("-" * 80)
    collections = parser.extract_collections()
    print(f"📦 Найдено коллекций: {len(collections)}\n")
    
    for idx, collection in enumerate(collections, 1):
        print(f"{idx}. {collection['title']}")
        print(f"   URL: {collection['url']}")
        print(f"   Изображение: {'✅ Да' if collection.get('image_url') else '❌ Нет'}")
        if collection.get('image_url'):
            print(f"   Путь: {collection['image_url']}")
        print()
    
    # 3. Тест извлечения проектов
    print("3️⃣  ТЕСТ: Извлечение проектов")
    print("-" * 80)
    projects = parser.extract_projects()
    print(f"📐 Найдено проектов: {len(projects)}\n")
    
    # 4. Тест извлечения блога
    print("4️⃣  ТЕСТ: Извлечение блога")
    print("-" * 80)
    blog_posts = parser.extract_blog_posts()
    print(f"📝 Найдено статей: {len(blog_posts)}\n")
    
    for idx, post in enumerate(blog_posts[:5], 1):
        print(f"{idx}. {post['title']}")
        print(f"   URL: {post['url']}")
        print(f"   Изображение: {'✅ Да' if post.get('image_url') else '❌ Нет'}")
        print()
    
    # Итоги
    print("="*80)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*80)
    print(f"✅ Логотип: {'Да' if logo else 'Нет'}")
    print(f"📦 Коллекции: {len(collections)}")
    print(f"📐 Проекты: {len(projects)}")
    print(f"📝 Блог: {len(blog_posts)}")
    print()
    
    if logo and len(collections) > 0:
        print("✅ ✅ ✅ ТЕСТ ПРОЙДЕН!")
    else:
        print("⚠️  Некоторые данные не получены")

if __name__ == '__main__':
    test_baldocer()
