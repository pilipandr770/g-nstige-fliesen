#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Полностью удалить производителя Gazzini из базы данных
"""

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent, ManufacturerSyncJob

app = create_app()

with app.app_context():
    # Найти Gazzini
    gazzini = Manufacturer.query.filter_by(slug='gazzini').first()
    
    if not gazzini:
        print("✅ Gazzini уже удален из базы данных")
        exit(0)
    
    print(f"🗑️  Найден: {gazzini.name} (ID: {gazzini.id})")
    print(f"   Удаление из базы данных...")
    
    # Удалить все связанные данные
    
    # 1. Удалить контент
    content_items = ManufacturerContent.query.filter_by(
        manufacturer_id=gazzini.id
    ).all()
    print(f"   - Удаление {len(content_items)} элементов контента...")
    for item in content_items:
        db.session.delete(item)
    
    # 2. Удалить задачи синхронизации
    sync_jobs = ManufacturerSyncJob.query.filter_by(
        manufacturer_id=gazzini.id
    ).all()
    print(f"   - Удаление {len(sync_jobs)} задач синхронизации...")
    for job in sync_jobs:
        db.session.delete(job)
    
    # 3. Удалить самого производителя
    print(f"   - Удаление производителя...")
    db.session.delete(gazzini)
    
    db.session.commit()
    
    print(f"\n✅ ГОТОВО! Gazzini полностью удален из базы данных")
    
    # Проверка
    remaining = Manufacturer.query.filter_by(slug='gazzini').first()
    if remaining:
        print(f"❌ ОШИБКА: Gazzini все еще в базе!")
    else:
        print(f"✅ Проверка: Gazzini не найден в базе")
    
    total_manufacturers = Manufacturer.query.count()
    active_manufacturers = Manufacturer.query.filter_by(active=True).count()
    
    print(f"\n📊 Статистика:")
    print(f"   Всего производителей: {total_manufacturers}")
    print(f"   Активных: {active_manufacturers}")
