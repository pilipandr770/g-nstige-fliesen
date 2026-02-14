"""
Обновление логотипа только для Aparici
"""

from app import create_app, db
from app.models import Manufacturer
from app.services.manufacturer_parsers import ApariciParser

def update_aparici_logo():
    app = create_app()
    with app.app_context():
        manufacturer = Manufacturer.query.filter_by(slug='aparici').first()
        
        if not manufacturer:
            print("❌ Aparici не найден в базе данных")
            return
        
        print(f"🏢 {manufacturer.name}")
        print(f"   Текущий логотип: {manufacturer.logo or 'отсутствует'}")
        
        parser = ApariciParser()
        logo_path = parser.extract_logo()
        
        if logo_path:
            manufacturer.logo = logo_path
            db.session.commit()
            print(f"   ✅ Логотип обновлен: {logo_path}")
        else:
            print(f"   ❌ Не удалось найти логотип")

if __name__ == '__main__':
    update_aparici_logo()
