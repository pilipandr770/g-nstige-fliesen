#!/usr/bin/env python3
"""Проверка данных Casalgrande в базе"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent, ManufacturerSyncJob

app = create_app()

with app.app_context():
    print("=" * 70)
    print("ПРОВЕРКА ДАННЫХ CASALGRANDE")
    print("=" * 70)
    
    # 1. Проверяем, есть ли производитель
    manufacturer = Manufacturer.query.filter_by(slug='casalgrande').first()
    if not manufacturer:
        print("❌ Производитель 'casalgrande' НЕ НАЙДЕН в базе данных!")
        exit(1)
    
    print(f"\n✅ Производитель найден:")
    print(f"   ID: {manufacturer.id}")
    print(f"   Name: {manufacturer.name}")
    print(f"   Slug: {manufacturer.slug}")
    print(f"   Website: {manufacturer.website}")
    print(f"   Active: {manufacturer.active}")
    print(f"   Auto Sync: {manufacturer.auto_sync}")
    print(f"   Last Sync: {manufacturer.last_sync}")
    print(f"   Logo: {manufacturer.logo}")
    
    # 2. Проверяем синхронизации
    print(f"\n{'='*70}")
    print("ИСТОРИЯ СИНХРОНИЗАЦИЙ")
    print("=" * 70)
    
    jobs = ManufacturerSyncJob.query.filter_by(
        manufacturer_id=manufacturer.id
    ).order_by(ManufacturerSyncJob.created_at.desc()).limit(5).all()
    
    if not jobs:
        print("⚠️  Синхронизации не найдены")
    else:
        print(f"Найдено синхронизаций: {len(jobs)}\n")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. Job ID: {job.id}")
            print(f"   Status: {job.status}")
            print(f"   Created: {job.created_at}")
            print(f"   Started: {job.started_at}")
            print(f"   Finished: {job.finished_at}")
            print(f"   Added: {job.added_count}, Skipped: {job.skipped_count}")
            if job.error_message:
                print(f"   Error: {job.error_message}")
            if job.log:
                print(f"   Log:\n{job.log}")
            print()
    
    # 3. Проверяем контент
    print(f"\n{'='*70}")
    print("КОНТЕНТ В БАЗЕ ДАННЫХ")
    print("=" * 70)
    
    # Коллекции
    collections = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='collection'
    ).all()
    
    print(f"\n📦 КОЛЛЕКЦИИ: {len(collections)}")
    if collections:
        published_count = sum(1 for c in collections if c.published)
        with_images = sum(1 for c in collections if c.image_url)
        print(f"   Опубликовано: {published_count}/{len(collections)}")
        print(f"   С изображениями: {with_images}/{len(collections)}")
        
        print(f"\n   Примеры (первые 5):")
        for i, col in enumerate(collections[:5], 1):
            print(f"   {i}. {col.title}")
            print(f"      Published: {col.published}")
            print(f"      Image: {col.image_url or 'НЕТ'}")
            print(f"      Description: {col.description[:100] if col.description else 'НЕТ'}...")
            print()
    else:
        print("   ❌ Коллекции НЕ НАЙДЕНЫ!")
    
    # Проекты
    projects = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='project'
    ).all()
    
    print(f"\n🏗️  ПРОЕКТЫ: {len(projects)}")
    if projects:
        published_count = sum(1 for p in projects if p.published)
        with_images = sum(1 for p in projects if p.image_url)
        print(f"   Опубликовано: {published_count}/{len(projects)}")
        print(f"   С изображениями: {with_images}/{len(projects)}")
        
        print(f"\n   Примеры (первые 3):")
        for i, proj in enumerate(projects[:3], 1):
            print(f"   {i}. {proj.title}")
            print(f"      Published: {proj.published}")
            print(f"      Image: {proj.image_url or 'НЕТ'}")
            print()
    else:
        print("   ⚠️  Проекты не найдены")
    
    # Блог
    blogs = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='blog'
    ).all()
    
    print(f"\n📰 БЛОГ/НОВОСТИ: {len(blogs)}")
    if blogs:
        published_count = sum(1 for b in blogs if b.published)
        print(f"   Опубликовано: {published_count}/{len(blogs)}")
    
    # 4. Проверяем, будет ли контент показан на фронтенде
    print(f"\n{'='*70}")
    print("ПРОВЕРКА ФИЛЬТРОВ ФРОНТЕНДА")
    print("=" * 70)
    
    # Фильтр для коллекций (published=True + image_url not null)
    visible_collections = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='collection',
        published=True
    ).filter(
        ManufacturerContent.image_url.isnot(None),
        ManufacturerContent.image_url != ''
    ).all()
    
    print(f"\n✨ ВИДИМЫЕ НА ФРОНТЕНДЕ:")
    print(f"   Коллекции: {len(visible_collections)}")
    
    visible_projects = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='project',
        published=True
    ).filter(
        ManufacturerContent.image_url.isnot(None),
        ManufacturerContent.image_url != ''
    ).all()
    
    print(f"   Проекты: {len(visible_projects)}")
    
    visible_blogs = ManufacturerContent.query.filter_by(
        manufacturer_id=manufacturer.id,
        content_type='blog',
        published=True
    ).all()
    
    print(f"   Блог/Новости: {len(visible_blogs)}")
    
    # 5. Проверяем URL
    print(f"\n{'='*70}")
    print("ПУБЛИЧНЫЕ URL")
    print("=" * 70)
    print(f"\n🌐 Страница производителя:")
    print(f"   https://g-nstige-fliesen.onrender.com/hersteller/{manufacturer.slug}")
    print(f"\n🌐 Коллекции:")
    print(f"   https://g-nstige-fliesen.onrender.com/hersteller/{manufacturer.slug}/collection")
    print(f"\n🌐 Проекты:")
    print(f"   https://g-nstige-fliesen.onrender.com/hersteller/{manufacturer.slug}/project")
    
    # 6. Диагностика проблем
    print(f"\n{'='*70}")
    print("ДИАГНОСТИКА")
    print("=" * 70)
    
    issues = []
    
    if not manufacturer.active:
        issues.append("❌ Производитель не активен (active=False)")
    
    if not jobs:
        issues.append("⚠️  Синхронизация никогда не запускалась")
    elif jobs[0].status == 'failed':
        issues.append(f"❌ Последняя синхронизация завершилась с ошибкой: {jobs[0].error_message}")
    elif jobs[0].status == 'running':
        issues.append("⏳ Синхронизация в процессе...")
    elif jobs[0].status == 'queued':
        issues.append("⏳ Синхронизация в очереди...")
    
    if not collections:
        issues.append("❌ НЕТ коллекций в базе данных!")
    elif not visible_collections:
        no_images = sum(1 for c in collections if not c.image_url)
        not_published = sum(1 for c in collections if not c.published)
        issues.append(f"⚠️  Коллекции не видны на фронте: без изображений={no_images}, не опубликовано={not_published}")
    
    if issues:
        print("\n🔍 Обнаруженные проблемы:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n✅ Проблем не обнаружено! Контент должен отображаться.")
    
    print(f"\n{'='*70}")
