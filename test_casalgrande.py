#!/usr/bin/env python3
"""Test script for Casalgrande parser"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
if not os.environ.get('OPENAI_API_KEY'):
    print("❌ OPENAI_API_KEY not found in environment")
    sys.exit(1)

from app.services.manufacturer_parsers import ManufacturerParserFactory

def test_casalgrande():
    """Test Casalgrande parser functionality"""
    
    print("=" * 60)
    print("TESTING CASALGRANDE PARSER")
    print("=" * 60)
    
    # Get parser instance
    parser = ManufacturerParserFactory.get_parser('casalgrande')
    if not parser:
        print("❌ Parser not found for 'casalgrande'")
        return
    
    print(f"✅ Parser found: {parser.__class__.__name__}")
    print(f"   Base URL: {parser.base_url}")
    print(f"   Slug: {parser.slug}")
    print()
    
    # Test 1: Extract collections
    print("=" * 60)
    print("TEST 1: Extracting Collections")
    print("=" * 60)
    try:
        collections = parser.extract_collections()
        print(f"✅ Extracted {len(collections)} collections")
        
        if collections:
            print("\n📦 Sample collections (first 3):")
            for i, col in enumerate(collections[:3], 1):
                print(f"\n  {i}. {col.get('title', 'NO TITLE')}")
                print(f"     URL: {col.get('url', 'NO URL')}")
                print(f"     Image: {col.get('image_url', 'NO IMAGE')}")
                print(f"     Description: {col.get('description', 'NO DESCRIPTION')[:100]}...")
        else:
            print("⚠️  No collections found!")
            
    except Exception as e:
        print(f"❌ Error extracting collections: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 2: Extract collection details (if we have collections)
    if collections and len(collections) > 0:
        print("=" * 60)
        print("TEST 2: Extracting Collection Detail")
        print("=" * 60)
        test_url = collections[0]['url']
        print(f"Testing URL: {test_url}")
        try:
            detail = parser.extract_collection_detail(test_url)
            if detail:
                print(f"✅ Collection detail extracted")
                print(f"   Title: {detail.get('title', 'NO TITLE')}")
                print(f"   Description length: {len(detail.get('description', ''))}")
                print(f"   Full content length: {len(detail.get('full_content', ''))}")
                print(f"   Images: {len(detail.get('images', []))}")
                if detail.get('description'):
                    print(f"   Description preview: {detail['description'][:200]}...")
            else:
                print("⚠️  No detail extracted")
        except Exception as e:
            print(f"❌ Error extracting detail: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    
    # Test 3: Extract projects
    print("=" * 60)
    print("TEST 3: Extracting Projects")
    print("=" * 60)
    try:
        projects = parser.extract_projects()
        print(f"✅ Extracted {len(projects)} projects")
        
        if projects:
            print("\n🏗️  Sample projects (first 3):")
            for i, proj in enumerate(projects[:3], 1):
                print(f"\n  {i}. {proj.get('title', 'NO TITLE')}")
                print(f"     URL: {proj.get('url', 'NO URL')}")
                print(f"     Image: {proj.get('image_url', 'NO IMAGE')}")
                print(f"     Description: {proj.get('description', 'NO DESCRIPTION')[:100]}...")
        else:
            print("⚠️  No projects found!")
            
    except Exception as e:
        print(f"❌ Error extracting projects: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 4: Extract blog posts
    print("=" * 60)
    print("TEST 4: Extracting Blog Posts")
    print("=" * 60)
    try:
        posts = parser.extract_blog_posts()
        print(f"✅ Extracted {len(posts)} blog posts")
        
        if posts:
            print("\n📰 Sample posts (first 3):")
            for i, post in enumerate(posts[:3], 1):
                print(f"\n  {i}. {post.get('title', 'NO TITLE')}")
                print(f"     URL: {post.get('url', 'NO URL')}")
        else:
            print("⚠️  No blog posts found!")
            
    except Exception as e:
        print(f"❌ Error extracting blog posts: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_casalgrande()
