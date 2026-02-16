#!/usr/bin/env python3
"""Симуляция полной синхронизации Casalgrande"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.content_scraper_service import scraper_service

app = create_app()

with app.app_context():
    print("=" * 70)
    print("СИМУЛЯЦИЯ СИНХРОНИЗАЦИИ CASALGRANDE")
    print("=" * 70)
    
    manufacturer = Manufacturer.query.filter_by(slug='casalgrande').first()
    if not manufacturer:
        print("❌ Производитель не найден!")
        exit(1)
    
    print(f"\n✅ Производитель: {manufacturer.name} (ID: {manufacturer.id})")
    
    # Извлекаем контент
    print(f"\n{'='*70}")
    print("ИЗВЛЕЧЕНИЕ КОНТЕНТА")
    print("=" * 70)
    
    try:
        all_content = scraper_service.extract_all_content('casalgrande')
    except Exception as e:
        print(f"❌ Ошибка извлечения: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    collections = all_content.get('collections', [])
    projects = all_content.get('projects', [])
    blog_posts = all_content.get('blog_posts', [])
    
    print(f"\n📦 Извлечено:")
    print(f"   Коллекции: {len(collections)}")
    print(f"   Проекты: {len(projects)}")
    print(f"   Блог: {len(blog_posts)}")
    
    # Проверяем структуру первой коллекции
    if collections:
        print(f"\n{'='*70}")
        print("СТРУКТУРА ПЕРВОЙ КОЛЛЕКЦИИ")
        print("=" * 70)
        first_col = collections[0]
        print(f"\nКлючи: {list(first_col.keys())}")
        print(f"\nДанные:")
        for key, value in first_col.items():
            if key == 'description' and value:
                print(f"  {key}: {value[:100]}...")
            elif key == 'full_content' and value:
                print(f"  {key}: {len(value)} символов")
            else:
                print(f"  {key}: {value}")
    
    # Симулируем сохранение (без commit)
    print(f"\n{'='*70}")
    print("СИМУЛЯЦИЯ СОХРАНЕНИЯ")
    print("=" * 70)
    
    def simulate_save_batch(items, content_type, require_image):
        added = 0
        skipped = 0
        skip_reasons = {'no_image': 0, 'no_title': 0}
        
        for item in items:
            # Проверка изображения
            if require_image and not item.get("image_url"):
                skipped += 1
                skip_reasons['no_image'] += 1
                continue
            
            # Проверка заголовка
            title = item.get("title", "")
            if not title or len(title) < 2:
                skipped += 1
                skip_reasons['no_title'] += 1
                continue
            
            added += 1
        
        return added, skipped, skip_reasons
    
    # Симулируем сохранение коллекций
    added, skipped, reasons = simulate_save_batch(collections, 'collection', require_image=True)
    print(f"\n📦 Коллекции:")
    print(f"   Будет добавлено: {added}")
    print(f"   Будет пропущено: {skipped}")
    if reasons['no_image']:
        print(f"      - Без изображения: {reasons['no_image']}")
    if reasons['no_title']:
        print(f"      - Без заголовка: {reasons['no_title']}")
    
    # Симулируем сохранение проектов
    added, skipped, reasons = simulate_save_batch(projects, 'project', require_image=True)
    print(f"\n🏗️  Проекты:")
    print(f"   Будет добавлено: {added}")
    print(f"   Будет пропущено: {skipped}")
    if reasons['no_image']:
        print(f"      - Без изображения: {reasons['no_image']}")
    if reasons['no_title']:
        print(f"      - Без заголовка: {reasons['no_title']}")
    
    # Симулируем сохранение блога
    added, skipped, reasons = simulate_save_batch(blog_posts, 'blog', require_image=False)
    print(f"\n📰 Блог:")
    print(f"   Будет добавлено: {added}")
    print(f"   Будет пропущено: {skipped}")
    if reasons['no_title']:
        print(f"      - Без заголовка: {reasons['no_title']}")
    
    # Проверяем коллекции без изображений
    if collections:
        print(f"\n{'='*70}")
        print("АНАЛИЗ КОЛЛЕКЦИЙ БЕЗ ИЗОБРАЖЕНИЙ")
        print("=" * 70)
        
        no_image = [c for c in collections if not c.get('image_url')]
        if no_image:
            print(f"\nКоллекции без изображений ({len(no_image)}):")
            for i, col in enumerate(no_image[:5], 1):
                print(f"  {i}. {col.get('title', 'NO TITLE')}")
                print(f"     URL: {col.get('url', 'NO URL')}")
        else:
            print("\n✅ Все коллекции имеют изображения!")
    
    print(f"\n{'='*70}")
