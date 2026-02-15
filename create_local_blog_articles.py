"""
Script to create local SEO blog articles about Frankfurt and Rhein-Main region
"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import BlogPost
from datetime import datetime
import re

def generate_slug(title):
    """Generate URL-safe slug from title."""
    slug = title.lower()
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue',
    }
    for char, repl in replacements.items():
        slug = slug.replace(char, repl)
    
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    slug = slug.strip('-')
    return slug

def create_local_articles():
    """Create local SEO articles about Frankfurt and Rhein-Main"""
    
    articles = [
        {
            "title": "Fliesen kaufen in Frankfurt am Main – Ihr lokaler Experte",
            "content": """<h2>Fliesen kaufen in Frankfurt: Qualität und Beratung vor Ort</h2>

<p>Sie suchen hochwertige Fliesen in Frankfurt am Main? In unserem Showroom auf der Hanauer Landstraße 421 finden Sie eine umfangreiche Auswahl an Premium-Fliesen von über 50 führenden europäischen Herstellern. Als lokaler Experte im Rhein-Main-Gebiet bieten wir Ihnen nicht nur erstklassige Produkte, sondern auch persönliche Beratung und umfassenden Service.</p>

<h3>Warum Fliesen lokal in Frankfurt kaufen?</h3>

<p>Der Kauf von Fliesen vor Ort hat viele Vorteile gegenüber Online-Bestellungen:</p>

<ul>
    <li><strong>Haptische Erfahrung:</strong> Fühlen Sie die Oberfläche, prüfen Sie die Beschaffenheit und erleben Sie die Fliesen mit allen Sinnen.</li>
    <li><strong>Farbbeurteilung:</strong> Online-Bilder können täuschen. Nur vor Ort sehen Sie die echten Farben und deren Wirkung.</li>
    <li><strong>Persönliche Beratung:</strong> Unsere Experten nehmen sich Zeit für Sie und finden die perfekte Lösung für Ihr Projekt.</li>
    <li><strong>Musterservice:</strong> Nehmen Sie Muster mit nach Hause und testen Sie diese in Ihrer Umgebung.</li>
    <li><strong>Keine Versandkosten:</strong> Schwere Fliesen verursachen hohe Versandkosten – bei uns liefern wir regional zu fairen Preisen.</li>
</ul>

<h3>Unser Showroom in Frankfurt-Fechenheim</h3>

<p>Unser moderner Showroom befindet sich verkehrsgünstig auf der Hanauer Landstraße 421 in Frankfurt-Fechenheim. Mit kostenlosen Parkplätzen direkt vor der Tür ist Ihr Besuch bequem und stressfrei. Hier präsentieren wir auf großer Fläche die schönsten Fliesenkollektionen und neuesten Trends.</p>

<h3>Große Auswahl für jeden Geschmack</h3>

<p>In unserem Sortiment finden Sie:</p>

<ul>
    <li>Keramikfliesen für Bad, Küche und Wohnbereich</li>
    <li>Feinsteinzeug in verschiedenen Formaten</li>
    <li>Natursteinfliesen aus Marmor, Granit und Travertin</li>
    <li>Großformatfliesen für moderne Raumgestaltung</li>
    <li>Mosaikfliesen für kreative Akzente</li>
    <li>Outdoor-Fliesen für Terrasse und Balkon</li>
</ul>

<h3>Service rund um Ihre Fliesen</h3>

<p>Wir bieten Ihnen den kompletten Service aus einer Hand:</p>

<ul>
    <li><strong>Kostenlose Beratung:</strong> Unsere Fachberater unterstützen Sie bei der Auswahl und Planung.</li>
    <li><strong>Materialberechnung:</strong> Wir ermitteln die benötigte Menge inklusive Verschnitt.</li>
    <li><strong>Lieferung:</strong> Schnelle und zuverlässige Lieferung im gesamten Rhein-Main-Gebiet.</li>
    <li><strong>Verlegervermittlung:</strong> Wir vermitteln Ihnen erfahrene Fliesenleger aus unserem Partnernetzwerk.</li>
</ul>

<h3>Perfekte Verkehrsanbindung</h3>

<p>Unser Showroom ist optimal erreichbar:</p>

<ul>
    <li>Mit dem Auto: Direkt an der Hanauer Landstraße (B40) mit kostenlosen Parkplätzen</li>
    <li>Mit der Straßenbahn: Haltestelle Ostbahnhof (Linien 11, 12) – nur 5 Minuten Fußweg</li>
    <li>Vom Frankfurter Hauptbahnhof: 15 Minuten mit der S-Bahn</li>
</ul>

<h3>Öffnungszeiten</h3>

<p>Besuchen Sie uns zu folgenden Zeiten:</p>

<ul>
    <li>Montag bis Freitag: 09:00 – 18:00 Uhr</li>
    <li>Samstag: 10:00 – 14:00 Uhr</li>
    <li>Sonntag: Geschlossen</li>
</ul>

<p>Termine außerhalb der Öffnungszeiten sind nach Absprache möglich.</p>

<h3>Besuchen Sie uns!</h3>

<p>Überzeugen Sie sich selbst von unserer Auswahl und unserem Service. Unser Team freut sich auf Ihren Besuch im Fliesen Showroom Frankfurt!</p>

<p><strong>Hermitage Home & Design GmbH & Co KG</strong><br>
Hanauer Landstraße 421<br>
60314 Frankfurt am Main<br>
Telefon: 069 90475570<br>
E-Mail: info@hermitage-frankfurt.de</p>""",
            "excerpt": "Fliesen kaufen in Frankfurt – Besuchen Sie unseren Showroom auf der Hanauer Landstraße! Über 50 Premium-Marken, kostenlose Beratung und Parkplätze direkt vor Ort.",
            "category": "Ratgeber",
            "meta_title": "Fliesen kaufen Frankfurt – Showroom mit 50+ Premium-Marken",
            "meta_description": "Fliesen in Frankfurt kaufen ✓ Showroom Hanauer Landstraße ✓ 50+ Premium-Marken ✓ Kostenlose Beratung & Parkplätze ✓ Jetzt besuchen!",
            "tags": "Frankfurt, Fliesen kaufen, Showroom Frankfurt, Rhein-Main, lokaler Händler"
        },
        {
            "title": "Die besten Fliesenleger in Frankfurt und Umgebung finden",
            "content": """<h2>Qualifizierte Fliesenleger in Frankfurt finden</h2>

<p>Die schönsten Fliesen nützen wenig, wenn die Verlegung nicht fachgerecht erfolgt. Eine professionelle Verlegung ist entscheidend für das Endergebnis und die Langlebigkeit Ihrer Fliesen. Wir zeigen Ihnen, worauf Sie bei der Suche nach einem guten Fliesenleger in Frankfurt achten sollten und wie wir Sie dabei unterstützen können.</p>

<h3>Warum ist professionelle Verlegung so wichtig?</h3>

<p>Fliesen verlegen ist ein Handwerk, das Erfahrung und Präzision erfordert:</p>

<ul>
    <li><strong>Untergrundvorbereitung:</strong> Der Untergrund muss perfekt eben und tragfähig sein.</li>
    <li><strong>Verlegetechnik:</strong> Je nach Fliesenart und -format sind unterschiedliche Techniken erforderlich.</li>
    <li><strong>Fugenarbeit:</strong> Gleichmäßige Fugen sind optisch und funktional wichtig.</li>
    <li><strong>Abdichtung:</strong> Besonders in Nassbereichen muss fachgerecht abgedichtet werden.</li>
    <li><strong>Großformat:</strong> Moderne Großformatfliesen erfordern spezielle Kenntnisse.</li>
</ul>

<h3>Worauf bei der Auswahl achten?</h3>

<p>Ein guter Fliesenleger zeichnet sich aus durch:</p>

<ul>
    <li><strong>Qualifikation:</strong> Abgeschlossene Ausbildung als Fliesenleger, idealerweise mit Meistertitel</li>
    <li><strong>Erfahrung:</strong> Mehrjährige Berufserfahrung, Referenzen und Beispielarbeiten</li>
    <li><strong>Versicherung:</strong> Betriebshaftpflichtversicherung für eventuelle Schäden</li>
    <li><strong>Kommunikation:</strong> Klare Absprachen zu Terminen, Kosten und Ausführung</li>
    <li><strong>Gewährleistung:</strong> Gesetzliche Gewährleistung von 5 Jahren auf Werkleistung</li>
</ul>

<h3>Unser Partnernetzwerk in Frankfurt</h3>

<p>Als Fliesen Showroom Frankfurt haben wir über die Jahre ein Netzwerk erfahrener und zuverlässiger Fliesenleger aufgebaut. Wir arbeiten ausschließlich mit qualifizierten Fachbetrieben zusammen, die unseren hohen Qualitätsansprüchen genügen.</p>

<h4>Vorteile unserer Partnervermittlung:</h4>

<ul>
    <li>Geprüfte und erfahrene Meisterbetriebe</li>
    <li>Spezialisiert auf verschiedene Fliesenarten und -formate</li>
    <li>Zuverlässige Termineinhaltung</li>
    <li>Faire und transparente Preise</li>
    <li>Gewährleistung und Versicherungsschutz</li>
    <li>Kurze Anfahrtswege im Rhein-Main-Gebiet</li>
</ul>

<h3>Regionale Abdeckung</h3>

<p>Unsere Partner-Fliesenleger arbeiten in ganz Frankfurt und Umgebung:</p>

<ul>
    <li>Frankfurt am Main (alle Stadtteile)</li>
    <li>Offenbach am Main</li>
    <li>Bad Vilbel</li>
    <li>Neu-Isenburg</li>
    <li>Dreieich</li>
    <li>Mainz und Wiesbaden</li>
    <li>Weitere Orte im Rhein-Main-Gebiet auf Anfrage</li>
</ul>

<h3>So funktioniert die Vermittlung</h3>

<p><strong>Schritt 1:</strong> Besuchen Sie unseren Showroom und wählen Sie Ihre Fliesen aus.</p>

<p><strong>Schritt 2:</strong> Teilen Sie uns Ihr Projekt mit – wir besprechen die Anforderungen.</p>

<p><strong>Schritt 3:</strong> Wir stellen den Kontakt zu passenden Fachbetrieben her.</p>

<p><strong>Schritt 4:</strong> Der Fliesenleger erstellt Ihnen ein Angebot für die Verlegung.</p>

<p><strong>Schritt 5:</strong> Nach Ihrer Beauftragung koordinieren wir Lieferung und Verlegung.</p>

<h3>Kosten für Fliesenverlegung in Frankfurt</h3>

<p>Die Kosten für die Verlegung hängen von verschiedenen Faktoren ab:</p>

<ul>
    <li>Flächengröße (größere Flächen = günstigerer Quadratmeterpreis)</li>
    <li>Fliesenformat (Großformat erfordert mehr Erfahrung)</li>
    <li>Verlegemuster (diagonal oder mit besonderen Mustern aufwendiger)</li>
    <li>Untergrundvorbereitung (Altfliesen entfernen, Boden ausgleichen)</li>
    <li>Zusatzarbeiten (Abdichtung, Fußbodenheizung)</li>
</ul>

<p>Durchschnittlich können Sie in Frankfurt mit 30-60 € pro Quadratmeter für die Verlegung rechnen, je nach Komplexität des Projekts.</p>

<h3>Tipps für Ihr Fliesenprojekt</h3>

<p><strong>Planung:</strong> Planen Sie ausreichend Zeit ein – Qualität braucht Zeit.</p>

<p><strong>Material:</strong> Bestellen Sie 10% mehr Fliesen als benötigt (Verschnitt und Reserve).</p>

<p><strong>Abstimmung:</strong> Besprechen Sie alle Details vorab mit dem Fliesenleger.</p>

<p><strong>Untergrund:</strong> Klären Sie, wer für die Untergrundvorbereitung zuständig ist.</p>

<p><strong>Abnahme:</strong> Nehmen Sie die Arbeit sorgfältig ab und dokumentieren Sie eventuelle Mängel.</p>

<h3>Kontaktieren Sie uns</h3>

<p>Gerne vermitteln wir Ihnen einen passenden Fliesenleger für Ihr Projekt in Frankfurt und Umgebung. Besuchen Sie uns im Showroom oder rufen Sie uns an!</p>

<p><strong>Fliesen Showroom Frankfurt</strong><br>
Hanauer Landstraße 421, 60314 Frankfurt am Main<br>
Telefon: 069 90475570</p>""",
            "excerpt": "Professionelle Fliesenleger in Frankfurt finden – Wir vermitteln geprüfte Meisterbetriebe für fachgerechte Verlegung. Qualität, Zuverlässigkeit und faire Preise garantiert!",
            "category": "Ratgeber",
            "meta_title": "Fliesenleger Frankfurt finden – Geprüfte Meisterbetriebe",
            "meta_description": "Fliesenleger in Frankfurt gesucht? ✓ Wir vermitteln geprüfte Fachbetriebe ✓ Meisterqualität ✓ Rhein-Main-Gebiet ✓ Jetzt anfragen!",
            "tags": "Fliesenleger Frankfurt, Fliesenleger finden, Handwerker, Rhein-Main, Verlegung"
        },
        {
            "title": "Badrenovierung in Frankfurt – Trends und Tipps für 2026",
            "content": """<h2>Badrenovierung in Frankfurt: Modern und stilvoll</h2>

<p>Sie planen eine Badrenovierung in Frankfurt? Ein neues Bad steigert nicht nur Ihren Wohnkomfort, sondern auch den Wert Ihrer Immobilie. In diesem Artikel zeigen wir Ihnen die aktuellen Trends für 2026 und geben praktische Tipps für Ihre Badplanung.</p>

<h3>Aktuelle Badtrends 2026</h3>

<h4>1. Natursteinoptik und große Formate</h4>

<p>Großformatige Fliesen in Natursteinoptik liegen weiter im Trend. Sie schaffen eine elegante, fugenarme Optik und lassen das Bad größer wirken. Besonders beliebt sind:</p>

<ul>
    <li>Marmoroptik in hellen Grau- und Beigetönen</li>
    <li>Travertinoptik für warme, mediterrane Atmosphäre</li>
    <li>Schiefer- und Granitoptik für moderne, dunkle Bäder</li>
</ul>

<h4>2. Holzoptik im Bad</h4>

<p>Holzoptikfliesen bringen Wärme und Natürlichkeit ins Badezimmer. Moderne Keramikfliesen in Holzoptik sind pflegeleicht, wasserfest und optisch kaum von echtem Holz zu unterscheiden.</p>

<h4>3. Erdtöne und natürliche Farben</h4>

<p>Nach Jahren der minimalistischen Ästhetik kehren wärmere Töne zurück:</p>

<ul>
    <li>Sandfarbene und beige Nuancen</li>
    <li>Terrakotta und Rostfarben als Akzente</li>
    <li>Grüntöne für ein naturnahes Ambiente</li>
</ul>

<h4>4. Barrierefreiheit</h4>

<p>Bodengleiche Duschen und rutschfeste Fliesen sind nicht nur praktisch, sondern auch optisch modern und zeitlos.</p>

<h4>5. Smartes Badezimmer</h4>

<p>Integrierte Beleuchtung, Spiegelheizung und digitale Armaturen machen das Bad komfortabler und energieeffizienter.</p>

<h3>Planung Ihrer Badrenovierung</h3>

<h4>Budget festlegen</h4>

<p>Eine Badrenovierung in Frankfurt kostet je nach Umfang:</p>

<ul>
    <li><strong>Einfache Renovierung:</strong> 5.000 – 10.000 € (nur Fliesen und Sanitär)</li>
    <li><strong>Mittlere Renovierung:</strong> 10.000 – 20.000 € (inkl. neue Armaturen und Möbel)</li>
    <li><strong>Luxus-Renovierung:</strong> 20.000 – 40.000+ € (hochwertige Materialien, Designer-Elemente)</li>
</ul>

<h4>Zeitplanung</h4>

<p>Planen Sie realistisch:</p>

<ul>
    <li>Planung und Materialauswahl: 2-4 Wochen</li>
    <li>Materialbestellung und Lieferzeit: 2-4 Wochen</li>
    <li>Bauzeit: 2-4 Wochen je nach Umfang</li>
</ul>

<p>Insgesamt sollten Sie 6-12 Wochen vom Start der Planung bis zum fertigen Bad einplanen.</p>

<h3>Fliesenauswahl für Ihr Bad</h3>

<h4>Wandfliesen</h4>

<ul>
    <li><strong>Format:</strong> Großformat (30×60 cm oder 60×120 cm) für moderne Optik</li>
    <li><strong>Oberfläche:</strong> Glänzend für kleine Bäder (reflektiert Licht), matt für große Bäder</li>
    <li><strong>Farbe:</strong> Helle Töne lassen das Bad größer wirken</li>
</ul>

<h4>Bodenfliesen</h4>

<ul>
    <li><strong>Rutschfestigkeit:</strong> Mindestens R10, besser R11 für Duschbereiche</li>
    <li><strong>Format:</strong> 60×60 cm oder 80×80 cm für moderne Optik</li>
    <li><strong>Material:</strong> Feinsteinzeug – robust, pflegeleicht und wasserdicht</li>
</ul>

<h3>Frankfurt-spezifische Tipps</h3>

<h4>Denkmalschutz beachten</h4>

<p>In Frankfurter Altbauten gelten oft Denkmalschutzauflagen. Informieren Sie sich vorab beim Denkmalamt, welche Arbeiten genehmigungspflichtig sind.</p>

<h4>Lokale Handwerker</h4>

<p>Arbeiten Sie mit lokalen Handwerkern – kurze Wege bedeuten bessere Erreichbarkeit und schnellere Problemlösung.</p>

<h4>Lieferung in Frankfurt</h4>

<p>In Frankfurts dicht bebautem Stadtgebiet ist die Anlieferung oft eine Herausforderung. Klären Sie vorab:</p>

<ul>
    <li>Parkmöglichkeiten für Lieferfahrzeuge</li>
    <li>Aufzug vorhanden oder Treppenhaus?</li>
    <li>Lagerung der Materialien</li>
</ul>

<h3>Nachhaltigkeit im Bad</h3>

<p>Moderne Badrenovierungen setzen auf Nachhaltigkeit:</p>

<ul>
    <li><strong>Wassersparende Armaturen:</strong> Reduzieren Wasserverbrauch um bis zu 50%</li>
    <li><strong>LED-Beleuchtung:</strong> Energieeffizient und langlebig</li>
    <li><strong>Recycelte Materialien:</strong> Viele Hersteller bieten Fliesen aus recyceltem Material</li>
    <li><strong>Lokale Produkte:</strong> Kurze Transportwege schonen die Umwelt</li>
</ul>

<h3>Unser Service für Ihre Badrenovierung</h3>

<p>Im Fliesen Showroom Frankfurt unterstützen wir Sie bei Ihrer Badrenovierung:</p>

<ul>
    <li>Kostenlose Erstberatung und Stilberatung</li>
    <li>Materialberechnung inklusive Verschnitt</li>
    <li>Musterservice – testen Sie Fliesen zu Hause</li>
    <li>Lieferung im Rhein-Main-Gebiet</li>
    <li>Vermittlung erfahrener Fliesenleger und Sanitärbetriebe</li>
</ul>

<h3>Besuchen Sie unseren Showroom</h3>

<p>Lassen Sie sich inspirieren! In unserem Showroom sehen Sie verschiedene Badgestaltungen und können Fliesen direkt vergleichen.</p>

<p><strong>Fliesen Showroom Frankfurt</strong><br>
Hanauer Landstraße 421, 60314 Frankfurt am Main<br>
Telefon: 069 90475570<br>
Öffnungszeiten: Mo-Fr 09:00-18:00, Sa 10:00-14:00</p>

<p>Wir freuen uns auf Ihren Besuch!</p>""",
            "excerpt": "Badrenovierung in Frankfurt 2026 – Aktuelle Trends von Natursteinoptik bis Smart Home. Plus: Praktische Tipps für Budget, Planung und Umsetzung in Frankfurt.",
            "category": "Inspiration",
            "meta_title": "Badrenovierung Frankfurt 2026 – Trends, Tipps & Kosten",
            "meta_description": "Bad renovieren in Frankfurt ✓ Trends 2026 ✓ Naturstein & Holzoptik ✓ Kostenübersicht ✓ Beratung im Showroom ✓ Jetzt informieren!",
            "tags": "Badrenovierung, Frankfurt, Badtrends 2026, Badezimmer, Renovierung"
        }
    ]
    
    app = create_app()
    
    with app.app_context():
        created_count = 0
        skipped_count = 0
        
        for article_data in articles:
            slug = generate_slug(article_data['title'])
            
            # Check if article already exists
            existing = BlogPost.query.filter_by(slug=slug).first()
            if existing:
                print(f"⏭️  Skipped (already exists): {article_data['title']}")
                skipped_count += 1
                continue
            
            # Create new article
            article = BlogPost(
                title=article_data['title'],
                slug=slug,
                content=article_data['content'],
                excerpt=article_data['excerpt'],
                category=article_data['category'],
                meta_title=article_data.get('meta_title'),
                meta_description=article_data.get('meta_description'),
                tags=article_data.get('tags'),
                published=True,
                status='published',
                published_at=datetime.utcnow(),
                ai_generated=False,
                reading_time=len(article_data['content'].split()) // 200  # Estimate reading time
            )
            
            db.session.add(article)
            created_count += 1
            print(f"✅ Created: {article_data['title']}")
        
        try:
            db.session.commit()
            print(f"\n🎉 Successfully created {created_count} article(s), skipped {skipped_count}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {e}")
            raise

if __name__ == '__main__':
    create_local_articles()
