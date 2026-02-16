#!/usr/bin/env python3
"""Быстрая проверка коллекций Casalgrande"""

import os
from dotenv import load_dotenv
load_dotenv()

from app.services.manufacturer_parsers import ManufacturerParserFactory

print("=" * 70)
print("ПРОВЕРКА КОЛЛЕКЦИЙ CASALGRANDE")
print("=" * 70)

parser = ManufacturerParserFactory.get_parser('casalgrande')

# Извлекаем только коллекции (быстро)
collections = parser.extract_collections()

print(f"\nВсего коллекций: {len(collections)}")

# Проверяем структуру
if collections:
    print(f"\nПервая коллекция:")
    first = collections[0]
    for key, value in first.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: {value[:100]}...")
        else:
            print(f"  {key}: {value}")
    
    # Считаем коллекции с/без изображений
    with_images = [c for c in collections if c.get('image_url')]
    without_images = [c for c in collections if not c.get('image_url')]
    
    print(f"\nС изображениями: {len(with_images)}")
    print(f"Без изображений: {len(without_images)}")
    
    if without_images:
        print(f"\nПримеры без изображений (первые 5):")
        for i, col in enumerate(without_images[:5], 1):
            print(f"  {i}. {col.get('title', 'NO TITLE')}")
    
    # Проверяем, будут ли они сохранены
    print(f"\n{'='*70}")
    print("СИМУЛЯЦИЯ СОХРАНЕНИЯ (require_image=True)")
    print("=" * 70)
    
    added = 0
    skipped_no_image = 0
    skipped_no_title = 0
    
    for col in collections:
        if not col.get('image_url'):
            skipped_no_image += 1
            continue
        title = col.get('title', '')
        if not title or len(title) < 2:
            skipped_no_title += 1
            continue
        added += 1
    
    print(f"\nБудет добавлено: {added}")
    print(f"Будет пропущено всего: {skipped_no_image + skipped_no_title}")
    print(f"  - Без изображения: {skipped_no_image}")
    print(f"  - Без заголовка: {skipped_no_title}")
    
    if added == 0:
        print(f"\n❌ ПРОБЛЕМА: Ни одна коллекция не будет сохранена!")
    elif added < len(collections) * 0.5:
        print(f"\n⚠️  ПРОБЛЕМА: Сохранится менее 50% коллекций ({added}/{len(collections)})")
    else:
        print(f"\n✅ ОК: Большинство коллекций будет сохранено ({added}/{len(collections)})")

print(f"\n{'='*70}")
