"""
Тестовый скрипт для проверки парсинга Aparici
"""

import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.manufacturer_parsers import ApariciParser

def main():
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ПАРСЕРА APARICI")
    print("=" * 60)
    
    parser = ApariciParser()
    
    # Тестируем извлечение коллекций
    print("\n🧪 Тестирование извлечения коллекций...")
    collections = parser.extract_collections()
    
    print(f"\n📊 Результаты: найдено {len(collections)} коллекций\n")
    
    for i, collection in enumerate(collections[:3], 1):
        print(f"--- Коллекция {i} ---")
        print(f"Название: {collection['title']}")
        print(f"Описание: {collection['description'][:100]}..." if collection['description'] else "Описание: Нет")
        print(f"Изображение: {collection['image_url']}")
        print(f"URL: {collection['source_url']}")
        print(f"Полный контент: {len(collection.get('full_content', ''))} символов")
        print()
    
    # Тестируем извлечение проектов
    print("\n🧪 Тестирование извлечения проектов...")
    projects = parser.extract_projects()
    
    print(f"\n📊 Результаты: найдено {len(projects)} проектов\n")
    
    for i, project in enumerate(projects[:3], 1):
        print(f"--- Проект {i} ---")
        print(f"Название: {project['title']}")
        print(f"Изображение: {project['image_url']}")
        print(f"URL: {project['source_url']}")
        print()

if __name__ == '__main__':
    main()
