"""
Проверка производительности приложения
"""
from app import create_app, db
from app.models import ManufacturerContent
import time
import os
import glob

app = create_app()
with app.app_context():
    total_records = ManufacturerContent.query.count()
    
    by_type = {}
    for ct in ['collection', 'project', 'blog']:
        count = ManufacturerContent.query.filter_by(content_type=ct).count()
        by_type[ct] = count
    
    print('ManufacturerContent table:')
    print(f'  Total records: {total_records}')
    print(f'  Collections: {by_type.get("collection", 0)}')
    print(f'  Projects: {by_type.get("project", 0)}')
    print(f'  Blog: {by_type.get("blog", 0)}')
    
    print()
    print('Query performance test:')
    
    start = time.time()
    items = ManufacturerContent.query.all()
    elapsed = time.time() - start
    print(f'  Load all records: {elapsed:.3f}s')
    
    print()
    print('Image file analysis:')
    
    total_size = 0
    file_count = 0
    for f in glob.glob('app/static/uploads/manufacturers/*'):
        try:
            size = os.path.getsize(f)
            total_size += size
            file_count += 1
        except:
            pass
    
    print(f'  Total image files: {file_count}')
    print(f'  Total size: {total_size / 1024 / 1024:.1f} MB')
    
    # Check for large images
    print()
    print('Largest images:')
    files_with_size = []
    for f in glob.glob('app/static/uploads/manufacturers/*'):
        try:
            size = os.path.getsize(f)
            files_with_size.append((os.path.basename(f), size))
        except:
            pass
    
    files_with_size.sort(key=lambda x: x[1], reverse=True)
    for name, size in files_with_size[:10]:
        print(f'  {name}: {size / 1024:.0f} KB')
