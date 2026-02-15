"""
Test script for Content Processor
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.content_processor import get_content_processor


def test_collection_description():
    """Тест обработки описания коллекции"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Обработка описания коллекции")
    print("="*60)
    
    processor = get_content_processor()
    
    # Пример сырого текста с сайта производителя (на испанском/английском)
    raw_text = """
    Discover our amazing new ceramic tile collection with stunning marble effect.
    Perfect for bathrooms and kitchens. Available in multiple formats.
    This serie offers exceptional quality and durability. Contact us today to learn more!
    """
    
    result = processor.process_collection_description(
        raw_text=raw_text,
        collection_name="Carrara Premium",
        manufacturer_name="Aparici"
    )
    
    print("\n📥 ВХОД (сырой текст):")
    print(raw_text)
    
    print("\n📤 ВЫХОД (обработанный):")
    print("\n1️⃣ KURZBESCHREIBUNG:")
    print(result['description'])
    
    print("\n2️⃣ VOLLTEXT (HTML):")
    print(result['full_content'])
    
    print("\n✅ Тест завершен!\n")


def test_project_description():
    """Тест обработки описания проекта"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Обработка описания проекта")
    print("="*60)
    
    processor = get_content_processor()
    
    raw_text = """
    Luxury hotel project in Barcelona. Used our premium porcelain tiles 
    throughout the lobby and guest rooms. Modern design with natural stone effect.
    Architect: Studio XYZ. Completed 2023.
    """
    
    result = processor.process_project_description(
        raw_text=raw_text,
        project_name="Hotel Vista Barcelona",
        manufacturer_name="Aparici"
    )
    
    print("\n📥 ВХОД (сырой текст):")
    print(raw_text)
    
    print("\n📤 ВЫХОД (обработанный):")
    print("\n1️⃣ KURZBESCHREIBUNG:")
    print(result['description'])
    
    print("\n2️⃣ VOLLTEXT (HTML):")
    print(result['full_content'])
    
    print("\n✅ Тест завершен!\n")


def test_minimal_text():
    """Тест с минимальным текстом (проверка fallback)"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Минимальный текст (Fallback)")
    print("="*60)
    
    processor = get_content_processor()
    
    # Очень короткий текст
    raw_text = "New collection"
    
    result = processor.process_collection_description(
        raw_text=raw_text,
        collection_name="Modern Line",
        manufacturer_name="Test Brand"
    )
    
    print("\n📥 ВХОД:")
    print(f"'{raw_text}'")
    
    print("\n📤 ВЫХОД (fallback):")
    print("\n1️⃣ DESCRIPTION:")
    print(result['description'])
    
    print("\n2️⃣ FULL CONTENT:")
    print(result['full_content'])
    
    print("\n✅ Тест завершен!\n")


def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ CONTENT PROCESSOR")
    print("="*60)
    print("\nМодель: gpt-4o-mini")
    print("Язык выхода: Deutsch (German)")
    print("Локализация: Frankfurt am Main\n")
    
    try:
        # Проверяем наличие API ключа
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  ВНИМАНИЕ: OPENAI_API_KEY не установлен!")
            print("Установите переменную окружения для работы с OpenAI API")
            return
        
        # Запускаем тесты
        test_collection_description()
        test_project_description()
        test_minimal_text()
        
        print("\n" + "="*60)
        print("✅ ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!")
        print("="*60)
        print("\n💡 Подсказка: Проверьте качество немецких текстов выше.")
        print("   Они должны быть:")
        print("   - На немецком языке")
        print("   - Без маркетинговых клише")
        print("   - С упоминанием Frankfurt/Showroom")
        print("   - Профессиональными и информативными\n")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
