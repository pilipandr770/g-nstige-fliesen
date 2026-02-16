#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Отключить автосинхронизацию для Casalgrande и восстановить коллекции
"""

from app import create_app, db
from app.models import Manufacturer

app = create_app()

with app.app_context():
    # Найти Casalgrande
    casalgrande = Manufacturer.query.filter_by(slug='casalgrande').first()
    
    if not casalgrande:
        print("❌ Casalgrande не найден")
        exit(1)
    
    print(f"✅ Найден: {casalgrande.name} (ID: {casalgrande.id})")
    print(f"   Текущий статус auto_sync: {casalgrande.auto_sync}")
    
    # Отключить автосинхронизацию
    casalgrande.auto_sync = False
    
    db.session.commit()
    
    print(f"\n✅ Автосинхронизация отключена!")
    print(f"   auto_sync = False")
    print(f"\n⚠️  ВАЖНО: Используйте ручную синхронизацию:")
    print(f"   python resync_casalgrande.py")
