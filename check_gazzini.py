#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from app import create_app, db
from app.models import Manufacturer, ManufacturerContent, ManufacturerSyncJob
from app.services.manufacturer_parsers import GazziniParser

app = create_app()

with app.app_context():
    # Найти производителя Gazzini
    gazzini = Manufacturer.query.filter_by(slug='gazzini').first()
    
    if not gazzini:
        print("❌ Производитель Gazzini не найден в БД")
        exit(1)
    
    print(f"✅ Найден производитель: {gazzini.name} (ID: {gazzini.id})")
    print(f"   URL: {gazzini.website}")
    
    # Проверить коллекции в БД
    collections = ManufacturerContent.query.filter_by(
        manufacturer_id=gazzini.id,
        content_type='collection'
    ).all()
    
    published = [c for c in collections if c.published]
    with_images = [c for c in collections if c.image_url]
    visible = [c for c in collections if c.published and c.image_url]
    
    print(f"\n📊 Коллекции в БД:")
    print(f"   Всего: {len(collections)}")
    print(f"   Опубликовано: {len(published)}")
    print(f"   С изображениями: {len(with_images)}")
    print(f"   Видимых на фронте: {len(visible)}")
    
    if visible:
        print(f"\n📋 Примеры видимых коллекций:")
        for c in visible[:3]:
            print(f"   - {c.title}")
            print(f"     URL: {c.source_url}")
            print(f"     Фото: {c.image_url}")
    
    # Проверить последние задачи синхронизации
    sync_jobs = ManufacturerSyncJob.query.filter_by(
        manufacturer_id=gazzini.id
    ).order_by(ManufacturerSyncJob.created_at.desc()).limit(5).all()
    
    print(f"\n🔄 Последние 5 задач синхронизации:")
    for job in sync_jobs:
        status_symbol = "✅" if job.status == "completed" else "❌" if job.status == "failed" else "⏳"
        print(f"{status_symbol} {job.created_at.strftime('%Y-%m-%d %H:%M')} - {job.status}")
        print(f"   Добавлено: {job.added_count}, Пропущено: {job.skipped_count}")
        if job.error_message:
            print(f"   Ошибка: {job.error_message}")
    
    # Протестировать парсер
    print(f"\n🔧 Тест парсера GazziniParser:")
    try:
        parser = GazziniParser()
        collections_parsed = parser.extract_collections()
        
        print(f"   Извлечено коллекций: {len(collections_parsed)}")
        
        with_images_parsed = [c for c in collections_parsed if c.get('image_url')]
        print(f"   С изображениями: {len(with_images_parsed)}")
        
        if collections_parsed:
            print(f"\n📋 Примеры извлеченных коллекций:")
            for c in collections_parsed[:3]:
                print(f"   - {c.get('title', 'NO TITLE')}")
                print(f"     URL: {c.get('url', 'NO URL')}")
                print(f"     Фото: {c.get('image_url', 'NO IMAGE')}")
        
    except Exception as e:
        print(f"   ❌ Ошибка парсера: {e}")
        import traceback
        traceback.print_exc()
