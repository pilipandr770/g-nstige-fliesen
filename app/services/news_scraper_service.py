"""
News Scraper Service — fetches news from RSS feeds, manufacturer blogs,
and industry sources for automatic blog article generation.
"""
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

try:
    import feedparser
except ImportError:
    feedparser = None


class NewsScraperService:
    """Service for collecting news from various sources."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 15

    def fetch_rss_feed(self, url):
        """
        Parse an RSS/Atom feed and return news items.

        Args:
            url: RSS feed URL

        Returns:
            list of dicts with keys: title, content, source_url, published_date, image_url
        """
        if not feedparser:
            print("feedparser nicht installiert. RSS-Feeds werden uebersprungen.")
            return []

        try:
            feed = feedparser.parse(url)
            items = []

            for entry in feed.entries[:10]:
                content = ''
                if hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].get('value', '')

                # Clean HTML from content
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    content = soup.get_text(separator=' ', strip=True)

                # Try to get image
                image_url = ''
                if hasattr(entry, 'media_content') and entry.media_content:
                    image_url = entry.media_content[0].get('url', '')
                elif hasattr(entry, 'enclosures') and entry.enclosures:
                    for enc in entry.enclosures:
                        if enc.get('type', '').startswith('image/'):
                            image_url = enc.get('href', '')
                            break

                item = {
                    'title': entry.get('title', ''),
                    'content': content,
                    'source_url': entry.get('link', ''),
                    'image_url': image_url,
                    'published_date': entry.get('published', ''),
                }
                if item['title']:
                    items.append(item)

            return items

        except Exception as e:
            print(f"RSS-Feed-Fehler ({url}): {str(e)}")
            return []

    def fetch_webpage_news(self, url, selectors=None):
        """
        Scrape news from a webpage.

        Args:
            url: webpage URL
            selectors: optional dict with CSS selectors for article, title, content, image

        Returns:
            list of dicts with news items
        """
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            items = []
            default_selectors = {
                'article': 'article',
                'title': 'h2, h3, .title',
                'content': 'p, .summary, .excerpt',
                'image': 'img',
                'link': 'a',
            }
            sel = selectors or default_selectors

            articles = soup.select(sel.get('article', 'article'))[:10]

            for article in articles:
                title_el = article.select_one(sel.get('title', 'h2, h3'))
                title = title_el.get_text(strip=True) if title_el else ''

                content_el = article.select_one(sel.get('content', 'p'))
                content = content_el.get_text(strip=True) if content_el else ''

                img_el = article.select_one(sel.get('image', 'img'))
                image_url = ''
                if img_el:
                    image_url = img_el.get('src', '') or img_el.get('data-src', '')

                link_el = article.select_one(sel.get('link', 'a'))
                source_url = ''
                if link_el:
                    source_url = link_el.get('href', '')
                    if source_url and not source_url.startswith('http'):
                        from urllib.parse import urljoin
                        source_url = urljoin(url, source_url)

                if title and len(title) >= 5:
                    items.append({
                        'title': title,
                        'content': content,
                        'source_url': source_url,
                        'image_url': image_url,
                    })

            return items

        except Exception as e:
            print(f"Webseiten-Scraping-Fehler ({url}): {str(e)}")
            return []

    def fetch_manufacturer_news(self, manufacturer_slug):
        """
        Fetch news/blog from a manufacturer using existing parsers.

        Args:
            manufacturer_slug: manufacturer slug for parser selection

        Returns:
            list of news items
        """
        try:
            from .content_scraper_service import scraper_service
            all_content = scraper_service.extract_all_content(manufacturer_slug)
            blog_posts = all_content.get('blog_posts', [])

            items = []
            for post in blog_posts:
                items.append({
                    'title': post.get('title', ''),
                    'content': post.get('content', '') or post.get('full_content', ''),
                    'source_url': post.get('source_url', ''),
                    'image_url': post.get('image_url', ''),
                    'manufacturer': manufacturer_slug,
                })

            return items

        except Exception as e:
            print(f"Hersteller-News-Fehler ({manufacturer_slug}): {str(e)}")
            return []

    def fetch_all_news(self):
        """
        Aggregate news from all active NewsSource entries in the database.

        Returns:
            list of news items, deduplicated
        """
        from ..models import NewsSource
        sources = NewsSource.query.filter_by(active=True).all()

        all_items = []
        seen_urls = set()

        for source in sources:
            items = []

            if source.source_type == 'rss':
                items = self.fetch_rss_feed(source.url)
            elif source.source_type == 'webpage':
                items = self.fetch_webpage_news(source.url)
            elif source.source_type == 'manufacturer':
                if source.manufacturer:
                    items = self.fetch_manufacturer_news(source.manufacturer.slug)

            for item in items:
                url = item.get('source_url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    item['source_name'] = source.name
                    if source.manufacturer_id:
                        item['manufacturer_id'] = source.manufacturer_id
                    all_items.append(item)

            # Update last_fetched timestamp
            from .. import db
            source.last_fetched = datetime.utcnow()
            db.session.commit()

        return all_items


# Singleton
_news_scraper = None


def get_news_scraper():
    """Get or create news scraper service instance."""
    global _news_scraper
    if _news_scraper is None:
        _news_scraper = NewsScraperService()
    return _news_scraper
