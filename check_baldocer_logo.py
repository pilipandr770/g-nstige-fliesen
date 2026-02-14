"""
Проверка логотипа Baldocer в БД
"""
from app import create_app, db
from app.models import Manufacturer

app = create_app()

with app.app_context():
    baldocer = Manufacturer.query.filter_by(slug='baldocer').first()
    
    if baldocer:
        print(f"Производитель: {baldocer.name}")
        print(f"Slug: {baldocer.slug}")
        print(f"Логотип в БД: {baldocer.logo}")
        print(f"Логотип установлен: {'ДА' if baldocer.logo else 'НЕТ'}")
        
        # Проверим файл
        if baldocer.logo:
            import os
            logo_path = os.path.join('app', 'static', 'uploads', baldocer.logo)
            exists = os.path.exists(logo_path)
            print(f"Файл существует: {'ДА' if exists else 'НЕТ'}")
            if exists:
                size = os.path.getsize(logo_path)
                print(f"Размер файла: {size} байт")
    else:
        print("Baldocer не найден в БД!")
