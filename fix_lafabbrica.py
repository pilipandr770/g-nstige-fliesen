#!/usr/bin/env python
"""Пересинхронизация La Fabbrica с исправленным парсером"""

import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

with app.app_context():
    print("=" * 60)
    print("ПЕРЕСИНХРОНИЗАЦИЯ LA FABBRICA")
    print("=" * 60)
    
    # Получаем La Fabbrica
    mfr = Manufacturer.query.filter_by(slug='lafabbrica').first()
    if not mfr:
        print("❌ La Fabbrica не найдена!")
        sys.exit(1)
    
    print(f"\nМанufacturer: {mfr.name}")
    
    # Удаляем старый контент
    old_content = ManufacturerContent.query.filter_by(manufacturer_id=mfr.id).all()
    print(f"\n🗑️  Удаление старого контента ({len(old_content)} элементов)...")
    for content in old_content:
        db.session.delete(content)
    db.session.commit()
    print("  ✓ Старый контент удален")
    
    # Получаем парсер
    parser = ManufacturerParserFactory.get_parser('lafabbrica')
    if not parser:
        print("❌ Парсер для La Fabbrica не найден!")
        sys.exit(1)
    
    # Извлекаем коллекции
    print("\n📥 Извлечение коллекций...")
    collections = parser.extract_collections()
    print(f"  ✓ Найдено коллекций: {len(collections)}")
    
    # Сохраняем коллекции
    for coll in collections:
        content = ManufacturerContent(
            manufacturer_id=mfr.id,
            title=coll.get('title'),
            content_type='collection',
            description=coll.get('description', ''),
            image_url=coll.get('image_url') or '',
            source_url=coll.get('source_url', '')
        )
        db.session.add(content)
    
    db.session.commit()
    print(f"  ✓ Сохранено коллекций: {len(collections)}")
    
    # Извлекаем проекты
    print("\n📥 Извлечение проектов...")
    projects = parser.extract_projects()
    print(f"  ✓ Найдено проектов: {len(projects)}")
    
    # Сохраняем проекты
    for proj in projects:
        content = ManufacturerContent(
            manufacturer_id=mfr.id,
            title=proj.get('title'),
            content_type='project',
            description=proj.get('description', ''),
            image_url=proj.get('image_url') or '',
            source_url=proj.get('source_url', '')
        )
        db.session.add(content)
    
    db.session.commit()
    print(f"  ✓ Сохранено проектов: {len(projects)}")
    
    # Извлекаем блог
    print("\n📥 Извлечение блог-постов...")
    blog_posts = parser.extract_blog_posts()
    print(f"  ✓ Найдено блог-постов: {len(blog_posts)}")
    
    # Сохраняем блог
    for post in blog_posts:
        content = ManufacturerContent(
            manufacturer_id=mfr.id,
            title=post.get('title'),
            content_type='blog_post',
            description=post.get('description', ''),
            image_url=post.get('image_url') or '',
            source_url=post.get('source_url', '')
        )
        db.session.add(content)
    
    db.session.commit()
    print(f"  ✓ Сохранено блог-постов: {len(blog_posts)}")
    
    # Итоговый статус
    total_new = len(collections) + len(projects) + len(blog_posts)
    print("\n" + "=" * 60)
    print(f"✅ ГОТОВО!")
    print(f"  Всего добавлено контента: {total_new}")
    print("=" * 60)
