"""
Обновление логотипа для La Fabbrica
"""
from app import create_app, db
from app.models import Manufacturer
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

with app.app_context():
    # Получаем La Fabbrica
    lafabbrica = Manufacturer.query.filter_by(slug='lafabbrica').first()
    
    if not lafabbrica:
        print("❌ La Fabbrica не найден в базе")
        exit(1)
    
    print(f"Обрабатываем: {lafabbrica.name}")
    print(f"  Текущий логотип: {lafabbrica.logo}")
    
    # Получаем парсер
    parser = ManufacturerParserFactory.get_parser('lafabbrica')
    
    if parser:
        logo_path = parser.extract_logo()
        
        if logo_path:
            lafabbrica.logo = logo_path  
            db.session.commit()
            print(f"  ✅ Логотип обновлен: {logo_path}")
        else:
            print("  ⚠️  Логотип не найден")
    else:
        print("  ❌ Парсер не найден")
