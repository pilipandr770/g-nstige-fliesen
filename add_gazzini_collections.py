#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Временное решение для Gazzini - добавляем коллекции и загружаем изображения вручную
Сайт Gazzini использует SG Captcha, поэтому автоматический парсинг невозможен.
"""

import os
import requests
from app import create_app, db
from app.models import Manufacturer, ManufacturerContent

app = create_app()

# Коллекции Gazzini с прямыми ссылками на изображения (если доступны)
# Эти URL нужно получить вручную из браузера
collections_to_add = [
    {
        'title': 'Amalfi Lux',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/amalfi-lux/',
        'description': 'Luxuriöse Fliesenkollektion Amalfi Lux von Gazzini. Elegante Designs für anspruchsvolle Räume.',
        'image_url': None  # Будет заполнено позже
    },
    {
        'title': 'Antique Portofino',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/antique-portofino/',
        'description': 'Antique Portofino Fliesenkollektion von Gazzini. Vintage-inspirierte Fliesen mit mediterranem Charme.',
        'image_url': None
    },
    {
        'title': 'Artwork',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/artwork/',
        'description': 'Artwork Fliesenkollektion von Gazzini. Künstlerische Designs für einzigartige Wandgestaltung.',
        'image_url': None
    },
    {
        'title': 'Atelier',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/atelier/',
        'description': 'Atelier Fliesenkollektion von Gazzini. Handwerkliche Qualität trifft auf modernes Design.',
        'image_url': None
    },
    {
        'title': 'Atlantic Blue',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/atlantic-blue/',
        'description': 'Atlantic Blue Fliesenkollektion von Gazzini. Tiefblaue Farbtöne inspiriert vom Ozean.',
        'image_url': None
    },
    {
        'title': 'Avenue White',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/avenue-white/',
        'description': 'Avenue White Fliesenkollektion von Gazzini. Reinweiße Eleganz für zeitlose Räume.',
        'image_url': None
    },
    {
        'title': 'Blauwsteen',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/blauwsteen/',
        'description': 'Blauwsteen Fliesenkollektion von Gazzini. Belgischer Blaustein-Look in Feinsteinzeug.',
        'image_url': None
    },
    {
        'title': 'Briques',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/briques/',
        'description': 'Briques Fliesenkollektion von Gazzini. Authentische Ziegeloptik für industriellen Charme.',
        'image_url': None
    },
    {
        'title': 'Calacatta Emerald',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/calacatta-emerald/',
        'description': 'Calacatta Emerald Fliesenkollektion von Gazzini. Marmoroptik mit smaragdgrünen Akzenten.',
        'image_url': None
    },
    {
        'title': 'Calacatta Oro',
        'url': 'https://www.ceramicagazzini.it/de/kollektionen/calacatta-oro/',
        'description': 'Calacatta Oro Fliesenkollektion von Gazzini. Luxuriöse gold-weiße Marmorimitationen.',
        'image_url': None
    },
]

print("=" * 70)
print("GAZZINI KOLLEKTIONEN MANUELL HINZUFÜGEN")
print("=" * 70)
print("\n⚠️  HINWEIS: Gazzini Website verwendet SG Captcha Schutz")
print("   Automatisches Scraping ist nicht möglich.")
print("   Kollektionen werden OHNE Bilder hinzugefügt (published=False)")
print("\n📋 Sie müssen Bilder manuell hinzufügen:")
print("   1. Besuchen Sie jede Kollektionsseite im Browser")
print("   2. Speichern Sie ein Bild pro Kollektion")
print("   3. Laden Sie es im Admin-Panel hoch\n")

with app.app_context():
    # Найти Gazzini
    gazzini = Manufacturer.query.filter_by(slug='gazzini').first()
    
    if not gazzini:
        print("❌ Gazzini Hersteller nicht gefunden in der Datenbank")
        exit(1)
    
    print(f"✅ Gefunden: {gazzini.name} (ID: {gazzini.id})")
    print(f"   Website: {gazzini.website}\n")
    
    # Проверить существующие коллекции
    existing = ManufacturerContent.query.filter_by(
        manufacturer_id=gazzini.id,
        content_type='collection'
    ).all()
    
    if existing:
        print(f"📦 Vorhandene Kollektionen: {len(existing)}")
        for item in existing:
            status = "✓" if item.image_url else "✗"
            pub = "Pub" if item.published else "Unpub"
            print(f"   {status} [{pub}] {item.title}")
        
        response = input("\n🗑️  Möchten Sie diese löschen und neu erstellen? (j/n): ")
        if response.lower() == 'j':
            for item in existing:
                db.session.delete(item)
            db.session.commit()
            print("   ✓ Gelöscht")
        else:
            print("   ✓ Behalten - Skript beendet")
            exit(0)
    
    # Добавить новые коллекции
    print(f"\n➕ Füge {len(collections_to_add)} Kollektionen hinzu...")
    added = 0
    
    for coll in collections_to_add:
        content = ManufacturerContent(
            manufacturer_id=gazzini.id,
            content_type='collection',
            title=coll['title'],
            description=coll['description'],
            source_url=coll['url'],
            published=False,  # Unpublished until images are added
            image_url=coll.get('image_url')
        )
        db.session.add(content)
        added += 1
        print(f"   ✓ {coll['title']}")
    
    db.session.commit()
    
    print(f"\n✅ FERTIG!")
    print(f"   Hinzugefügt: {added} Kollektionen")
    print(f"   Status: UNVERÖFFENTLICHT (published=False)")
    print(f"\n📝 NÄCHSTE SCHRITTE:")
    print(f"   1. Gehen Sie zu: https://www.ceramicagazzini.it/de/kollektionen/")
    print(f"   2. Öffnen Sie jede Kollektion und speichern Sie 1 Bild")
    print(f"   3. Platzieren Sie Bilder in: app/static/uploads/manufacturers/")
    print(f"      Format: gazzini_[kollektionsname].jpg")
    print(f"   4. Führen Sie update_gazzini_images.py aus (wird erstellt)")
    
    # Проверим результат
    total = ManufacturerContent.query.filter_by(
        manufacturer_id=gazzini.id,
        content_type='collection'
    ).count()
    
    published_count = ManufacturerContent.query.filter_by(
        manufacturer_id=gazzini.id,
        content_type='collection',
        published=True
    ).count()
    
    with_images = ManufacturerContent.query.filter_by(
        manufacturer_id=gazzini.id,
        content_type='collection'
    ).filter(ManufacturerContent.image_url.isnot(None)).count()
    
    print(f"\n📊 Datenbank-Status:")
    print(f"   Gesamt: {total}")
    print(f"   Mit Bildern: {with_images}")
    print(f"   Veröffentlicht: {published_count}")

