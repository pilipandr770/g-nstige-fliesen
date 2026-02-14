"""
Скрипт для извлечения и обновления логотипов производителей
"""

from app import create_app, db
from app.models import Manufacturer
from app.services.manufacturer_parsers import ManufacturerParserFactory

def update_manufacturer_logos():
    """Обновляет логотипы для всех производителей"""
    app = create_app()
    with app.app_context():
        manufacturers = Manufacturer.query.all()
        
        print(f"\n📋 Найдено {len(manufacturers)} производителей")
        print("=" * 60)
        
        updated = 0
        skipped = 0
        failed = 0
        
        for manufacturer in manufacturers:
            print(f"\n🏢 {manufacturer.name} ({manufacturer.slug})")
            
            # Проверяем есть ли уже логотип
            if manufacturer.logo:
                print(f"   ℹ️  Логотип уже есть: {manufacturer.logo}")
                response = input("   Обновить? (y/N): ")
                if response.lower() not in ['y', 'yes', 'да']:
                    skipped += 1
                    continue
            
            # Пытаемся получить парсер
            parser = ManufacturerParserFactory.get_parser(manufacturer.slug)
            
            if not parser:
                print(f"   ⚠️  Парсер не найден, пропускаем")
                skipped += 1
                continue
            
            try:
                # Извлекаем логотип
                logo_path = parser.extract_logo()
                
                if logo_path:
                    manufacturer.logo = logo_path
                    db.session.commit()
                    print(f"   ✅ Логотип обновлен: {logo_path}")
                    updated += 1
                else:
                    print(f"   ❌ Не удалось найти логотип")
                    failed += 1
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Обновлено: {updated}")
        print(f"⏭️  Пропущено: {skipped}")
        print(f"❌ Ошибок: {failed}")

if __name__ == '__main__':
    update_manufacturer_logos()
