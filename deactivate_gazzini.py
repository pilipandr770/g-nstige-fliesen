#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Деактивировать производителя Gazzini
"""

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent, ManufacturerSyncJob

app = create_app()

with app.app_context():
    # Найти Gazzini
    gazzini = Manufacturer.query.filter_by(slug='gazzini').first()
    
    if not gazzini:
        print("❌ Gazzini не найден в базе данных")
        exit(0)
    
    print(f"✅ Найден: {gazzini.name} (ID: {gazzini.id})")
    
    # Удалить все коллекции
    collections = ManufacturerContent.query.filter_by(
        manufacturer_id=gazzini.id
    ).all()
    
    if collections:
        print(f"🗑️  Удаление {len(collections)} коллекций...")
        for item in collections:
            db.session.delete(item)
    
    # Деактивировать производителя
    gazzini.active = False
    gazzini.auto_sync = False
    
    db.session.commit()
    
    print(f"✅ Gazzini деактивирован")
    print(f"   - active = False (не отображается на сайте)")
    print(f"   - auto_sync = False (автосинхронизация отключена)")
    print(f"   - Коллекции удалены: {len(collections)}")
    
    # Проверка
    active_count = Manufacturer.query.filter_by(active=True).count()
    print(f"\n📊 Активных производителей: {active_count}")
