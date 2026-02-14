"""
Обновление логотипа Etile в базе данных
"""
from app import create_app, db
from app.models import Manufacturer
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

with app.app_context():
    # Получаем Etile
    manufacturer = Manufacturer.query.filter_by(slug='etile').first()
    
    if not manufacturer:
        print("❌ Производитель Etile не найден в БД")
        exit(1)
    
    print(f"✅ Найден производитель: {manufacturer.name}")
    print(f"   Текущий логотип: {manufacturer.logo or 'Не установлен'}")
    print()
    
    # Получаем парсер
    parser = ManufacturerParserFactory.get_parser('etile')
    if not parser:
        print("❌ Парсер не найден")
        exit(1)
    
    # Извлекаем логотип
    print("🔍 Извлечение логотипа...")
    logo_path = parser.extract_logo()
    
    if logo_path:
        # Обновляем в БД
        manufacturer.logo = logo_path
        db.session.commit()
        
        print(f"✅ Логотип обновлен: {logo_path}")
        print(f"✅ Сохранено в БД")
    else:
        print("❌ Не удалось извлечь логотип")
