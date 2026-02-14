#!/usr/bin/env python
"""Полная пересинхронизация всех производителей"""

import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Manufacturer, ManufacturerContent
from app.services.manufacturer_parsers import ManufacturerParserFactory

app = create_app()

# Производители для пересинхронизации (по приоритету проблемности)
MANUFACTURERS_TO_SYNC = [
    'lafabbrica',      # 0 контента - нужно восстановить
    'casalgrande',     # 61% с изображениями
    'dune',            # 86% с изображениями
    'equipe',          # 85% с изображениями
    'exagres',         # 68% с изображениями
    'gazzini',         # 0% с изображениями
    'halcon',          # 70% с изображениями
    'unicom-starker',  # 0% с изображениями
]

def sync_manufacturer(slug):
    """Пересинхронизирует одного производителя"""
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"СИНХРОНИЗАЦИЯ: {slug}")
        print(f"{'='*60}")
        
        # Получаем производителя
        mfr = Manufacturer.query.filter_by(slug=slug).first()
        if not mfr:
            print(f"❌ Производитель {slug} не найден!")
            return False
        
        print(f"Производитель: {mfr.name}")
        
        # Удаляем старый контент
        old_count = ManufacturerContent.query.filter_by(manufacturer_id=mfr.id).count()
        if old_count > 0:
            print(f"\n🗑️  Удаление старого контента ({old_count} элементов)...")
            ManufacturerContent.query.filter_by(manufacturer_id=mfr.id).delete()
            db.session.commit()
            print(f"  ✓ Удалено")
        
        # Получаем парсер
        parser = ManufacturerParserFactory.get_parser(slug)
        if not parser:
            print(f"❌ Парсер для {slug} не найден!")
            return False
        
        # Синхронизируем контент
        total_added = 0
        
        # Коллекции
        try:
            print("\n📥 Загрузка коллекций...")
            collections = parser.extract_collections()
            print(f"  Найдено: {len(collections)}")
            
            for coll in collections:
                content = ManufacturerContent(
                    manufacturer_id=mfr.id,
                    title=coll.get('title', ''),
                    content_type='collection',
                    description=coll.get('description', ''),
                    image_url=coll.get('image_url') or '',
                    source_url=coll.get('source_url', '')
                )
                db.session.add(content)
            
            db.session.commit()
            print(f"  ✓ Добавлено: {len(collections)}")
            total_added += len(collections)
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
        
        # Проекты
        try:
            print("\n📥 Загрузка проектов...")
            projects = parser.extract_projects()
            print(f"  Найдено: {len(projects)}")
            
            for proj in projects:
                content = ManufacturerContent(
                    manufacturer_id=mfr.id,
                    title=proj.get('title', ''),
                    content_type='project',
                    description=proj.get('description', ''),
                    image_url=proj.get('image_url') or '',
                    source_url=proj.get('source_url', '')
                )
                db.session.add(content)
            
            db.session.commit()
            print(f"  ✓ Добавлено: {len(projects)}")
            total_added += len(projects)
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
        
        # Блог
        try:
            print("\n📥 Загрузка блог-постов...")
            blog_posts = parser.extract_blog_posts()
            print(f"  Найдено: {len(blog_posts)}")
            
            for post in blog_posts:
                content = ManufacturerContent(
                    manufacturer_id=mfr.id,
                    title=post.get('title', ''),
                    content_type='blog_post',
                    description=post.get('description', ''),
                    image_url=post.get('image_url') or '',
                    source_url=post.get('source_url', '')
                )
                db.session.add(content)
            
            db.session.commit()
            print(f"  ✓ Добавлено: {len(blog_posts)}")
            total_added += len(blog_posts)
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
        
        print(f"\n✅ ИТОГО добавлено: {total_added} элементов")
        return True

# Запуск синхронизации
if __name__ == '__main__':
    print("\n" + "="*60)
    print("ПОЛНАЯ ПЕРЕСИНХРОНИЗАЦИЯ ПРОИЗВОДИТЕЛЕЙ")
    print("="*60)
    
    results = {}
    for slug in MANUFACTURERS_TO_SYNC:
        try:
            results[slug] = sync_manufacturer(slug)
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА для {slug}: {e}")
            results[slug] = False
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*60)
    
    for slug, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {slug}")
    
    print("="*60)
