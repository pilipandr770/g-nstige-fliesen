#!/usr/bin/env python3
"""Реальная синхронизация Casalgrande с сохранением в БД"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

with app.app_context():
    print("=" * 70)
    print("РЕАЛЬНАЯ СИНХРОНИЗАЦИЯ CASALGRANDE")
    print("=" * 70)
    
    # Получаем производителя
    manufacturer = Manufacturer.query.filter_by(slug='casalgrande').first()
    if not manufacturer:
        print("❌ Производитель не найден!")
        exit(1)
    
    print(f"\n✅ Производитель: {manufacturer.name} (ID: {manufacturer.id})")
    
    # Удаляем старый контент
    deleted = ManufacturerContent.query.filter_by(manufacturer_id=manufacturer.id).delete()
    db.session.commit()
    print(f"🗑️  Удалено старых записей: {deleted}")
    
    # Получаем парсер
    parser = ManufacturerParserFactory.get_parser('casalgrande')
    if not parser:
        print("❌ Парсер не найден!")
        exit(1)
    
    print(f"\n{'='*70}")
    print("ИЗВЛЕЧЕНИЕ КОЛЛЕКЦИЙ")
    print("=" * 70)
    
    # Извлекаем коллекции
    collections = parser.extract_collections()
    print(f"\n📦 Извлечено коллекций: {len(collections)}")
    
    # Сохраняем коллекции
    added = 0
    skipped = 0
    
    print(f"\n{'='*70}")
    print("СОХРАНЕНИЕ В БАЗУ ДАННЫХ")
    print("=" * 70)
    
    for col in collections:
        # Проверки
        if not col.get('image_url'):
            skipped += 1
            continue
        
        title = col.get('title', '')
        if not title or len(title) < 2:
            skipped += 1
            continue
        
        # Создаем запись
        content = ManufacturerContent(
            manufacturer_id=manufacturer.id,
            content_type='collection',
            title=title,
            description=col.get('description', ''),
            full_content=col.get('full_content', ''),
            technical_specs=col.get('technical_specs', ''),
            image_url=col.get('image_url', ''),
            source_url=col.get('url', ''),
            published=True
        )
        db.session.add(content)
        added += 1
        
        if added % 10 == 0:
            print(f"  Сохранено: {added}...")
    
    # Коммитим
    db.session.commit()
    
    print(f"\n✅ ГОТОВО!")
    print(f"   Добавлено: {added}")
    print(f"   Пропущено: {skipped}")
    
    # Проверяем результат
    print(f"\n{'='*70}")
    print("ПРОВЕРКА РЕЗУЛЬТАТА")
    print("=" * 70)
    
    total = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='collection'
    ).count()
    
    published_count = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='collection',
        published=True
    ).count()
    
    visible = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='collection',
        published=True
    ).filter(
        ManufacturerContent.image_url.isnot(None),
        ManufacturerContent.image_url != ''
    ).count()
    
    print(f"\n📊 Статистика в БД:")
    print(f"   Всего коллекций: {total}")
    print(f"   Опубликовано: {published_count}")
    print(f"   Видимых на фронте: {visible}")
    
    if visible > 0:
        print(f"\n✅ УСПЕХ! Коллекции должны отображаться на странице!")
        print(f"\n🌐 Проверьте: https://g-nstige-fliesen.onrender.com/hersteller/casalgrande")
    else:
        print(f"\n❌ ПРОБЛЕМА: Коллекции не будут видны на фронте!")
    
    print(f"\n{'='*70}")
