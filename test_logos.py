"""Тест логотипов в шаблонах"""
import re
import sys
sys.path.insert(0, '.')

from app import create_app

app = create_app()
with app.test_client() as c:
    r = c.get('/hersteller')
    html = r.data.decode()
    
    # Ищем все img теги
    imgs = re.findall(r'<img src="([^"]+)"[^>]*alt="([^"]+)"', html)
    print(f"Found {len(imgs)} images on /hersteller page:")
    for src, alt in imgs:
        ok = "OK" if "manufacturers/" in src else "BROKEN"
        print(f"  [{ok}] {alt}: {src}")
    
    # Проверяем, что нет старых patterns
    old_pattern = re.findall(r"uploads/[a-z].*?\.(?:gif|svg|png|jpg|ico)", html)
    new_pattern = re.findall(r"uploads/manufacturers/[a-z].*?\.(?:gif|svg|png|jpg|ico)", html)
    
    print(f"\nOld pattern (uploads/filename): {len(old_pattern) - len(new_pattern)}")
    print(f"New pattern (uploads/manufacturers/filename): {len(new_pattern)}")
