"""
Обновление логотипа для APE Grupo
"""
from app import create_app, db
from app.models import Manufacturer
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

with app.app_context():
    # Получаем APE Grupo
    ape = Manufacturer.query.filter_by(slug='ape').first()
    
    if not ape:
        print("❌ APE Grupo не найден в базе")
        exit(1)
    
    print(f"Обрабатываем: {ape.name}")
    print(f"  Текущий логотип: {ape.logo}")
    
    # Получаем парсер
    parser = ManufacturerParserFactory.get_parser('ape')
    
    if parser:
        logo_path = parser.extract_logo()
        
        if logo_path:
            ape.logo = logo_path
            db.session.commit()
            print(f"  ✅ Логотип обновлен: {logo_path}")
        else:
            print("  ⚠️  Логотип не найден")
    else:
        print("  ❌ Парсер не найден")
