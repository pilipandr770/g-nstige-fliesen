"""
Синхронизация контента Exagres с лучшей обработкой изображений
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ExagresParser
import requests
import os
from urllib.parse import urlparse
import hashlib

app = create_app()

with app.app_context():
    exagres = Manufacturer.query.filter_by(slug='exagres').first()
    if not exagres:
        print('❌ Exagres не найден')
        exit(1)
    
    print(f'🔄 Синхронизация Exagres...')
    
    # Удалим старый контент без изображений
    old_content = ManufacturerContent.query.filter_by(
        manufacturer_id=exagres.id
    ).all()
    
    print(f'Удаляю старые {len(old_content)} элементов Exagres...')
    for item in old_content:
        db.session.delete(item)
    db.session.commit()
    
    # Получаем новый парсер
    parser_class = ExagresParser
    parser = parser_class()
    
    # Извлекаем коллекции с лучшей обработкой изображений
    print('\n🔍 Парсинг коллекций Exagres с лучшей обработкой...')
    
    try:
        collections = parser.extract_collections()
        print(f'Найдено коллекций: {len(collections)}')
        
        # Добавляем только те что с изображениями
        added_count = 0
        for coll in collections:
            if not coll.get('image_url'):
                print(f"⚠️  Пропускаю без картинки: {coll['title']}")
                continue
            
            # Проверяем не существует ли уже
            existing = ManufacturerContent.query.filter_by(
                manufacturer_id=exagres.id,
                title=coll['title']
            ).first()
            
            if existing:
                print(f"ℹ️  Уже существует: {coll['title']}")
                continue
            
            # Добавляем
            content = ManufacturerContent(
                manufacturer_id=exagres.id,
                content_type='collection',
                title=coll['title'],
                subtitle=coll.get('subtitle', ''),
                description=coll.get('description', ''),
                full_content=coll.get('full_content', ''),
                technical_specs=coll.get('technical_specs', ''),
                image_url=coll['image_url'],
                source_url=coll.get('source_url', ''),
                published=True
            )
            db.session.add(content)
            added_count += 1
            print(f"✓ Добавлена коллекция: {coll['title']}")
        
        db.session.commit()
        print(f'\n✅ Добавлено коллекций: {added_count}')
        
        # Проверим статус
        all_content = ManufacturerContent.query.filter_by(manufacturer_id=exagres.id).all()
        with_images = len([c for c in all_content if c.image_url])
        print(f'\n📊 Статус Exagres:')
        print(f'   Всего контента: {len(all_content)}')
        print(f'   С картинками: {with_images}')
        print(f'   Без картинок: {len(all_content) - with_images}')
        
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()
