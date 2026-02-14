#!/usr/bin/env python
"""Быстрая синхронизация коллекций и проектов (без блога) для оставшихся производителей"""

import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

# Производители которые нужно доделать
MANUFACTURERS = [
    'halcon',           # 0 - нужно восстановить
    'casalgrande',      # 260 - доделать
    'dune',             # 79 - доделать
    'equipe',           # 102 - доделать  
    'exagres',          # 45 - доделать
    'gazzini',          # 10 - без изображ
]

with app.app_context():
    for slug in MANUFACTURERS:
        print(f"\n{'='*60}")
        print(f"Синхронизация: {slug}")
        print(f"{'='*60}")
        
        mfr = Manufacturer.query.filter_by(slug=slug).first()
        if not mfr:
            print(f"❌ Не найден")
            continue
        
        # Удаляем старый контент
        old = ManufacturerContent.query.filter_by(manufacturer_id=mfr.id).count()
        if old > 0:
            ManufacturerContent.query.filter_by(manufacturer_id=mfr.id).delete()
            db.session.commit()
            print(f"✓ Удалено {old} старых элементов")
        
        parser = ManufacturerParserFactory.get_parser(slug)
        if not parser:
            print(f"❌ Парсер не найден")
            continue
        
        # Коллекции
        try:
            print("\nЗагрузка коллекций...")
            collections = parser.extract_collections()
            for coll in collections:
                content = ManufacturerContent(
                    manufacturer_id=mfr.id,
                    title=coll.get('title', ''),
                    content_type='collection',
                    description=coll.get('description', ''),
                    image_url=coll.get('image_url') or '',
                    source_url=coll.get('source_url', '')
                )
                db.session.add(content)
            db.session.commit()
            print(f"✓ Добавлено коллекций: {len(collections)}")
        except Exception as e:
            print(f"❌ Коллекции: {e}")
            db.session.rollback()
        
        # Проекты
        try:
            print("\nЗагрузка проектов...")
            projects = parser.extract_projects()
            for proj in projects:
                content = ManufacturerContent(
                    manufacturer_id=mfr.id,
                    title=proj.get('title', ''),
                    content_type='project',
                    description=proj.get('description', ''),
                    image_url=proj.get('image_url') or '',
                    source_url=proj.get('source_url', '')
                )
                db.session.add(content)
            db.session.commit()
            print(f"✓ Добавлено проектов: {len(projects)}")
        except Exception as e:
            print(f"❌ Проекты: {e}")
            db.session.rollback()

print("\n" + "="*60)
print("✅ ГОТОВО!")
print("="*60)
