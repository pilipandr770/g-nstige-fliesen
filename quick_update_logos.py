"""
Быстрое обновление логотипов для всех производителей с парсерами
"""

from app import create_app, db
from app.models import Manufacturer
from app.services.manufacturer_parsers import ManufacturerParserFactory

def quick_update_logos():
    app = create_app()
    with app.app_context():
        # Список производителей с доступными парсерами
        slugs_with_parsers = ['aparici', 'dune', 'equipe']
        
        for slug in slugs_with_parsers:
            manufacturer = Manufacturer.query.filter_by(slug=slug).first()
            
            if not manufacturer:
                print(f"⚠️  {slug} не найден в БД")
                continue
            
            print(f"\n🏢 {manufacturer.name}")
            
            if manufacturer.logo:
                print(f"   ℹ️  Логотип уже есть: {manufacturer.logo}")
                continue
            
            parser = ManufacturerParserFactory.get_parser(slug)
            if not parser:
                continue
            
            try:
                logo_path = parser.extract_logo()
                if logo_path:
                    manufacturer.logo = logo_path
                    db.session.commit()
                    print(f"   ✅ Логотип добавлен: {logo_path}")
                else:
                    print(f"   ⚠️  Логотип не найден")
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")

if __name__ == '__main__':
    quick_update_logos()
