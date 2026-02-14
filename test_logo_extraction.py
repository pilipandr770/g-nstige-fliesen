"""
Тестирование извлечения логотипа Aparici
"""

from app.services.manufacturer_parsers import ApariciParser

def test_logo():
    parser = ApariciParser()
    
    print("=" * 60)
    print("ТЕСТ ИЗВЛЕЧЕНИЯ ЛОГОТИПА APARICI")
    print("=" * 60)
    
    logo_path = parser.extract_logo()
    
    print(f"\n📊 Результат:")
    if logo_path:
        print(f"✅ Логотип найден: {logo_path}")
    else:
        print(f"❌ Логотип не найден")

if __name__ == '__main__':
    test_logo()
