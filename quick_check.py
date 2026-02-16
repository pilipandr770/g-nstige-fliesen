#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent

app = create_app()

with app.app_context():
    m = Manufacturer.query.filter_by(slug='casalgrande').first()
    if m:
        total = ManufacturerContent.query.filter_by(
            manufacturer_id=m.id, 
            content_type='collection'
        ).count()
        published = ManufacturerContent.query.filter_by(
            manufacturer_id=m.id, 
            content_type='collection',
            published=True
        ).count()
        with_images = ManufacturerContent.query.filter_by(
            manufacturer_id=m.id, 
            content_type='collection'
        ).filter(ManufacturerContent.image_url.isnot(None)).count()
        
        print(f"📊 Casalgrande:")
        print(f"   Всего: {total}")
        print(f"   Опубликовано: {published}")
        print(f"   С изображениями: {with_images}")
