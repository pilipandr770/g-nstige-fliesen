"""
Blog Generator Service — AI-powered blog article generation using OpenAI API.
Collects news from manufacturers and industry sources, generates SEO-optimized
articles in German, targeting customers for the Frankfurt tile showroom.
"""
import os
import json
from datetime import datetime
from openai import OpenAI
from slugify import slugify


class BlogGeneratorService:
    """Service for generating SEO-optimized blog articles using OpenAI."""

    CATEGORIES = [
        'Neue Kollektionen',
        'Design-Trends',
        'Fliesen-Ratgeber',
        'Projekte & Referenzen',
        'Pflege & Wartung',
        'Showroom News',
    ]

    CATEGORY_KEYWORDS = {
        'Neue Kollektionen': ['kollektion', 'collection', 'serie', 'neu', 'launch', 'neuheit'],
        'Design-Trends': ['trend', 'design', 'stil', 'farbe', 'muster', 'modern', 'inspiration'],
        'Fliesen-Ratgeber': ['ratgeber', 'tipps', 'pflege', 'verlegen', 'auswahl', 'material'],
        'Projekte & Referenzen': ['projekt', 'referenz', 'realisier', 'hotel', 'bad', 'kueche'],
        'Pflege & Wartung': ['pflege', 'reinig', 'wartung', 'schutz', 'impraegn'],
        'Showroom News': ['showroom', 'event', 'messe', 'ausstellung', 'eroeffnung'],
    }

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = "gpt-4o-mini"

    def _get_system_prompt(self):
        """System prompt for article generation."""
        return """Du bist ein erfahrener Content-Redakteur fuer einen Fliesen Showroom in Frankfurt am Main.

AKTUELLE INFORMATION:
- Heutiges Datum: Februar 2026
- Alle Artikel muessen aktuell und relevant fuer 2026 sein
- Wenn Quellinformationen aeltere Jahreszahlen enthalten (z.B. 2023, 2024), aktualisiere sie auf 2026 oder verwende zeitlose Formulierungen

SHOWROOM-INFO:
- Name: guenstige-fliesen.de (Hermitage Home & Design GmbH & Co KG)
- Adresse: Hanauer Landstrasse 421, 60314 Frankfurt am Main
- Telefon: 069 90475570
- E-Mail: info@hermitage-frankfurt.de
- Oeffnungszeiten: Mo-Fr 09:00-18:00, Sa 10:00-14:00

SHOWROOM VORTEILE (in CTA einbauen):
- Kostenlose Parkplaetze direkt vor Ort
- Individuelle Beratung und persoenliche Betreuung
- Professionelle Fachberatung zu allen Fliesenfragen
- Grosse Ausstellung mit vielen Musterfliesen zum Anfassen

AUFGABE: Erstelle einen SEO-optimierten Blogartikel auf Deutsch basierend auf den bereitgestellten Informationen.

ANFORDERUNGEN:
1. title: Max. 60 Zeichen, enthaelt das Hauptkeyword, ansprechend fuer Leser
2. meta_title: SEO-optimierter Titel, max. 60 Zeichen, optimiert fuer Google-Suchergebnisse
3. meta_description: Max. 155 Zeichen, enthaelt Hauptkeyword und Call-to-Action, ueberzeugt zum Klicken
4. excerpt: Kurze Zusammenfassung, max. 200 Zeichen, fuer die Blog-Uebersicht
5. content: 600-1000 Woerter, gut strukturiert:
   - Verwende HTML-Tags: <h2>, <h3>, <p>, <ul>, <li>, <strong>
   - Beginne NICHT mit <h1> (wird separat angezeigt)
   - Mindestens 2-3 Zwischenueberschriften (<h2>) mit relevanten Keywords
   - Natuerlicher, informativer Schreibstil mit SEO-Keywords (aber nicht uebertreiben)
   - Verwende lokale Keywords: "Frankfurt", "Frankfurt am Main", "Rhein-Main-Gebiet"
   - Mindestens einen CTA zum Besuch des Showrooms einbauen (z.B. in der Mitte des Artikels)
   - Am Ende: Starker Absatz mit Einladung zum Showroom, erwaehne IMMER:
     * Die korrekte Adresse: Hanauer Landstrasse 421, 60314 Frankfurt am Main
     * Kostenlose Parkplaetze
     * Individuelle Beratung
     * Telefon: 069 90475570
     * Oeffnungszeiten
6. category: Eine der folgenden Kategorien (waehle die passendste):
   - Neue Kollektionen
   - Design-Trends
   - Fliesen-Ratgeber
   - Projekte & Referenzen
   - Pflege & Wartung
   - Showroom News
7. tags: 3-5 relevante deutsche Keywords, kommagetrennt, SEO-optimiert

SEO-OPTIMIERUNG:
- Verwende das Hauptkeyword im ersten Absatz
- Nutze Variationen des Keywords im Text
- Strukturiere den Text logisch mit klaren Ueberschriften
- Schreibe fuer Menschen, nicht fuer Suchmaschinen
- Vermeide Keyword-Stuffing

WICHTIG: Antworte ausschliesslich im JSON-Format:
{
    "title": "...",
    "meta_title": "...",
    "meta_description": "...",
    "excerpt": "...",
    "content": "...",
    "category": "...",
    "tags": "keyword1, keyword2, keyword3"
}"""

    def generate_article(self, source_content, category=None):
        """
        Generate a blog article from source content using OpenAI.

        Args:
            source_content: dict with keys like 'title', 'content', 'source_url', 'manufacturer'
            category: optional category override

        Returns:
            dict with generated article fields or {'error': '...'}
        """
        if not self.client or not self.api_key:
            return {'error': 'OpenAI API key ist nicht konfiguriert.'}

        user_prompt = self._build_user_prompt(source_content, category)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)

            # Generate slug from title
            result['slug'] = self._generate_unique_slug(result.get('title', ''))

            # Track token usage
            tokens_used = response.usage.total_tokens if response.usage else 0
            result['tokens_used'] = tokens_used
            # gpt-4o-mini pricing: ~$0.15/1M input + $0.60/1M output
            result['cost_estimate'] = tokens_used * 0.0000004

            return result

        except json.JSONDecodeError as e:
            return {'error': f'JSON-Parsing-Fehler: {str(e)}'}
        except Exception as e:
            return {'error': f'OpenAI API Fehler: {str(e)}'}

    def generate_from_topic(self, topic, category=None, manufacturer_name=None):
        """
        Generate an article from a free-form topic description.

        Args:
            topic: str, the topic to write about
            category: optional category
            manufacturer_name: optional manufacturer name for context

        Returns:
            dict with generated article fields or {'error': '...'}
        """
        source_content = {
            'title': topic,
            'content': topic,
        }
        if manufacturer_name:
            source_content['manufacturer'] = manufacturer_name

        return self.generate_article(source_content, category)

    def generate_from_news(self, news_item):
        """
        Generate an article from a scraped news item.

        Args:
            news_item: dict with 'title', 'content', 'source_url', optionally 'manufacturer', 'image_url'

        Returns:
            dict with generated article fields or {'error': '...'}
        """
        return self.generate_article(news_item)

    def auto_generate(self, count=1):
        """
        Automatically generate blog articles from available news sources.
        Used by the CLI command and cron job.

        Args:
            count: number of articles to generate

        Returns:
            list of results (dicts with article data or error info)
        """
        from ..models import NewsSource, BlogPost, BlogGenerationLog, Manufacturer, ManufacturerContent
        from .. import db

        results = []

        # Strategy 1: Generate from recent manufacturer content (blog/news type)
        recent_content = ManufacturerContent.query.filter(
            ManufacturerContent.content_type.in_(['blog', 'news']),
            ManufacturerContent.published == True
        ).order_by(ManufacturerContent.created_at.desc()).limit(20).all()

        for item in recent_content:
            if len(results) >= count:
                break

            # Skip if already used as source
            if self._is_duplicate(item.source_url, item.title):
                continue

            source = {
                'title': item.title,
                'content': item.full_content or item.description or '',
                'source_url': item.source_url or '',
                'manufacturer': item.manufacturer.name if item.manufacturer else '',
                'image_url': item.image_url or '',
            }

            result = self.generate_article(source)

            if 'error' not in result:
                post = self._save_article(result, source, item.manufacturer_id)
                results.append({'success': True, 'title': post.title, 'id': post.id})

                # Log generation
                log = BlogGenerationLog(
                    blog_post_id=post.id,
                    source_type='manufacturer_content',
                    source_url=item.source_url,
                    status='success',
                    tokens_used=result.get('tokens_used', 0),
                    cost_estimate=result.get('cost_estimate', 0),
                )
                db.session.add(log)
                db.session.commit()
            else:
                results.append({'success': False, 'error': result['error']})
                log = BlogGenerationLog(
                    source_type='manufacturer_content',
                    source_url=item.source_url,
                    status='error',
                    error_message=result['error'],
                )
                db.session.add(log)
                db.session.commit()

        # Strategy 2: Generate from RSS news sources
        if len(results) < count:
            from .news_scraper_service import get_news_scraper
            scraper = get_news_scraper()
            news_items = scraper.fetch_all_news()

            for news in news_items:
                if len(results) >= count:
                    break

                if self._is_duplicate(news.get('source_url', ''), news.get('title', '')):
                    continue

                result = self.generate_from_news(news)

                if 'error' not in result:
                    # Try to match manufacturer
                    manufacturer_id = news.get('manufacturer_id')
                    post = self._save_article(result, news, manufacturer_id)
                    results.append({'success': True, 'title': post.title, 'id': post.id})

                    log = BlogGenerationLog(
                        blog_post_id=post.id,
                        source_type='rss',
                        source_url=news.get('source_url', ''),
                        status='success',
                        tokens_used=result.get('tokens_used', 0),
                        cost_estimate=result.get('cost_estimate', 0),
                    )
                    db.session.add(log)
                    db.session.commit()
                else:
                    results.append({'success': False, 'error': result['error']})

        # Strategy 3: Generate from topic if still not enough
        if len(results) < count:
            topics = self._get_fallback_topics()
            for topic in topics:
                if len(results) >= count:
                    break

                result = self.generate_from_topic(topic)
                if 'error' not in result:
                    post = self._save_article(result, {'title': topic, 'content': topic})
                    results.append({'success': True, 'title': post.title, 'id': post.id})

                    log = BlogGenerationLog(
                        blog_post_id=post.id,
                        source_type='topic',
                        status='success',
                        tokens_used=result.get('tokens_used', 0),
                        cost_estimate=result.get('cost_estimate', 0),
                    )
                    db.session.add(log)
                    db.session.commit()

        return results

    def _save_article(self, result, source, manufacturer_id=None):
        """Save a generated article as a draft BlogPost."""
        from ..models import BlogPost
        from .. import db

        post = BlogPost(
            title=result.get('title', ''),
            slug=result.get('slug', ''),
            content=result.get('content', ''),
            excerpt=result.get('excerpt', ''),
            meta_title=result.get('meta_title', ''),
            meta_description=result.get('meta_description', ''),
            category=result.get('category', ''),
            tags=result.get('tags', ''),
            image_url=source.get('image_url', ''),
            source_url=source.get('source_url', ''),
            source_content=json.dumps(source, ensure_ascii=False),
            manufacturer_id=manufacturer_id,
            ai_generated=True,
            status='draft',
            published=False,
            reading_time=max(1, len(result.get('content', '').split()) // 200),
        )
        db.session.add(post)
        db.session.commit()
        return post

    def _build_user_prompt(self, source_content, category=None):
        """Build the user prompt from source content."""
        parts = []

        if source_content.get('manufacturer'):
            parts.append(f"Hersteller: {source_content['manufacturer']}")

        if source_content.get('title'):
            parts.append(f"Thema/Titel: {source_content['title']}")

        if source_content.get('content'):
            content = source_content['content']
            # Limit source content to avoid token waste
            if len(content) > 2000:
                content = content[:2000] + '...'
            parts.append(f"Quellinformationen:\n{content}")

        if source_content.get('source_url'):
            parts.append(f"Originalquelle: {source_content['source_url']}")

        if category:
            parts.append(f"Kategorie: {category}")

        return "\n\n".join(parts)

    def _generate_unique_slug(self, title):
        """Generate a unique slug, appending a number if needed."""
        from ..models import BlogPost

        base_slug = slugify(title, max_length=290)
        if not base_slug:
            base_slug = f"blog-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        slug = base_slug
        counter = 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def _is_duplicate(self, source_url, title):
        """Check if an article from this source or with similar title exists."""
        from ..models import BlogPost

        if source_url:
            existing = BlogPost.query.filter_by(source_url=source_url).first()
            if existing:
                return True

        if title:
            slug = slugify(title, max_length=290)
            existing = BlogPost.query.filter_by(slug=slug).first()
            if existing:
                return True

        return False

    def _auto_categorize(self, title, content):
        """Automatically assign a category based on content keywords."""
        text = f"{title} {content}".lower()
        scores = {}
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[cat] = score

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else 'Design-Trends'

    def _get_fallback_topics(self):
        """Return a list of evergreen topics for when no news is available."""
        return [
            "Aktuelle Fliesentrends fuer Badezimmer 2026",
            "Grossformat-Fliesen: Tipps fuer moderne Raeume",
            "Naturstein vs. Feinsteinzeug: Ein Vergleich",
            "Fliesen richtig pflegen: Die besten Tipps",
            "Kueche mit Fliesen gestalten: Ideen und Inspiration",
            "Outdoor-Fliesen: Terrasse und Balkon stilvoll gestalten",
            "Mosaikfliesen: Kreative Akzente im Bad",
            "Fliesen fuer den Flur: Robust und elegant",
            "Holzoptik-Fliesen: Natuerlichkeit trifft Langlebigkeit",
            "Betonoptik-Fliesen: Industrial Style fuer Zuhause",
        ]


# Singleton
_blog_generator = None


def get_blog_generator():
    """Get or create blog generator service instance."""
    global _blog_generator
    if _blog_generator is None:
        _blog_generator = BlogGeneratorService()
    return _blog_generator
