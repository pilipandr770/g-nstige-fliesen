# Gazzini Kollektionen - Manuelle Bildverwaltung

## Problem
Die Gazzini-Website (ceramicagazzini.it) verwendet **SG Captcha-Schutz**, der automatisches Scraping unmöglich macht. Alle Versuche, die Seiten automatisch abzurufen, führen zu 403-Fehlern.

## Lösung
Die 10 Gazzini-Kollektionen wurden **manuell zur Datenbank hinzugefügt**, sind aber:
- ❌ **Unveröffentlicht** (published=False)
- ❌ **Ohne Bilder** (image_url=None)

Sie müssen die Bilder **manuell hochladen**, um die Kollektionen sichtbar zu machen.

---

## Anleitung: Bilder manuell hinzufügen

### Option 1: Über das Admin-Panel (EMPFOHLEN)

1. **Gehen Sie zum Admin-Panel:**
   ```
   http://localhost:5000/admin/manufacturers
   ```
   oder auf Render:
   ```
   https://gunstige-fliesen.onrender.com/admin/manufacturers
   ```

2. **Klicken Sie auf "Gazzini" → "Inhalt verwalten"**

3. **Für jede Kollektion:**
   - Klicken Sie auf "Bearbeiten"
   - Besuchen Sie die Kollektionsseite im Browser:
     ```
     https://www.ceramicagazzini.it/de/kollektionen/[kollektion-name]/
     ```
   - Rechtsklick auf ein Bild → "Bild speichern unter..."
   - Im Admin-Panel: Klicken Sie auf "Neues Bild hochladen"
   - Wählen Sie das gespeicherte Bild
   - **Aktivieren Sie "Veröffentlicht" Checkbox**
   - Klicken Sie auf "Speichern"

4. **Wiederholen Sie Schritt 3 für alle 10 Kollektionen**

---

### Option 2: Datei-Upload (Für Entwickler)

Wenn Sie die Bilder bereits heruntergeladen haben:

1. **Platzieren Sie die Bilder in:**
   ```
   app/static/uploads/manufacturers/
   ```
   
2. **Dateiname-Format:**
   ```
   gazzini_[eindeutige_id].jpg
   ```
   Beispiel: `gazzini_amalfi_lux.jpg`

3. **Führen Sie das Update-Skript aus:**
   ```bash
   python update_gazzini_images.py
   ```
   (Dieses Skript muss noch erstellt werden, falls benötigt)

---

## Liste der Gazzini-Kollektionen

| Nr | Kollektion          | URL                                                                  | Status       |
|----|---------------------|----------------------------------------------------------------------|--------------|
| 1  | Amalfi Lux          | https://www.ceramicagazzini.it/de/kollektionen/amalfi-lux/          | Unveröff.    |
| 2  | Antique Portofino   | https://www.ceramicagazzini.it/de/kollektionen/antique-portofino/   | Unveröff.    |
| 3  | Artwork             | https://www.ceramicagazzini.it/de/kollektionen/artwork/             | Unveröff.    |
| 4  | Atelier             | https://www.ceramicagazzini.it/de/kollektionen/atelier/             | Unveröff.    |
| 5  | Atlantic Blue       | https://www.ceramicagazzini.it/de/kollektionen/atlantic-blue/       | Unveröff.    |
| 6  | Avenue White        | https://www.ceramicagazzini.it/de/kollektionen/avenue-white/        | Unveröff.    |
| 7  | Blauwsteen          | https://www.ceramicagazzini.it/de/kollektionen/blauwsteen/          | Unveröff.    |
| 8  | Briques             | https://www.ceramicagazzini.it/de/kollektionen/briques/             | Unveröff.    |
| 9  | Calacatta Emerald   | https://www.ceramicagazzini.it/de/kollektionen/calacatta-emerald/   | Unveröff.    |
| 10 | Calacatta Oro       | https://www.ceramicagazzini.it/de/kollektionen/calacatta-oro/       | Unveröff.    |

---

## Technische Details

### Was wurde geändert:

1. **GazziniParser verbessert:**
   - Session-basierte Anfragen hinzugefügt
   - Bessere Browser-Header
   - Delay zwischen Anfragen
   - Verwendet deutsche URLs `/de/kollektionen/`

2. **Admin-Panel erweitert:**
   - Bild-Upload-Feld hinzugefügt
   - Unterstützt JPG, PNG, GIF, WebP
   - Automatische Dateinamen-Generierung

3. **Kollektionen-Datenbank:**
   - 10 Gazzini-Kollektionen hinzugefügt
   - Alle mit `published=False` (unsichtbar)
   - Alle mit `image_url=None` (kein Bild)

### Code-Änderungen:
- ✅ `app/routes.py` - Bild-Upload in `edit_manufacturer_content()`
- ✅ `app/templates/admin/edit_manufacturer_content.html` - File-Input hinzugefügt
- ✅ `app/services/manufacturer_parsers.py` - GazziniParser verbessert
- ✅ `add_gazzini_collections.py` - Skript zum Hinzufügen der Kollektionen

---

## Häufige Fragen

**Q: Warum funktioniert der automatische Sync nicht?**  
A: Die Gazzini-Website blockiert alle automatisierten Anfragen mit einem Captcha-System. Dies ist eine bewusste Sicherheitsmaßnahme der Website.

**Q: Kann man das Captcha umgehen?**  
A: Technisch möglich mit Browser-Automation (Selenium/Playwright) + Captcha-Solving-Dienst, aber sehr aufwändig und rechtlich fragwürdig.

**Q: Gibt es eine einfachere Lösung?**  
A: Leider nein. Manuelle Bild-Uploads sind die praktischste Lösung.

**Q: Wie lange dauert es, alle 10 Bilder hinzuzufügen?**  
A: Ca. 5-10 Minuten für alle Kollektionen.

---

## Nächste Schritte

1. ✅ Kollektionen sind in Datenbank
2. ⏳ **Fügen Sie Bilder über Admin-Panel hinzu**
3. ⏳ **Aktivieren Sie "Veröffentlicht" für jede Kollektion**
4. ✅ Kollektionen werden auf der Website angezeigt

Sobald Bilder hochgeladen und Kollektionen veröffentlicht wurden, erscheinen sie auf:
```
https://gunstige-fliesen.onrender.com/hersteller/gazzini
```
