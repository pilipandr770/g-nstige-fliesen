"""
AI Content Processor - обработка контента производителей через OpenAI
"""

from openai import OpenAI
import os
from typing import Optional, Dict
import re


class ContentProcessor:
    """Обработчик контента через OpenAI для немецкого рынка"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
    
    def process_collection_description(self, 
                                      raw_text: str, 
                                      collection_name: str,
                                      manufacturer_name: str) -> Dict[str, str]:
        """
        Обрабатывает описание коллекции плитки через OpenAI
        
        Args:
            raw_text: Сырой текст с сайта производителя
            collection_name: Название коллекции
            manufacturer_name: Название производителя
            
        Returns:
            Dict с обработанным текстом:
            - description: Краткое описание (150-200 символов)
            - full_content: Полное описание с призывом к действию
        """
        
        if not raw_text or len(raw_text.strip()) < 20:
            # Если текста нет или он слишком короткий, генерируем базовое описание
            return self._generate_fallback_description(collection_name, manufacturer_name)
        
        system_prompt = """Du bist ein Experte für Fliesenmarketing in Deutschland mit Fokus auf Frankfurt.

Deine Aufgabe: Verarbeite Produktbeschreibungen von Fliesenherstellern und erstelle optimierte Texte für unseren Showroom.

WICHTIG:
- Schreibe auf Deutsch (für deutsches Publikum)
- Ton: Professionell, aber zugänglich und einladend
- Entferne Marketing-Floskeln wie "Entdecken Sie", "Kontaktieren Sie uns heute"
- Fokus auf praktische Vorteile für Kunden
- Erwähne nie: Großhandel, B2B, Händler, Vertriebspartner
- Zielgruppe: Endkunden (Privat + Architekten)

FORMAT:
1. KURZBESCHREIBUNG (150-200 Zeichen): Präzise Zusammenfassung mit Stil und Hauptmerkmalen
2. VOLLTEXT (200-300 Wörter): Detaillierte Beschreibung + Benefits + lokaler Bezug"""

        user_prompt = f"""HERSTELLER: {manufacturer_name}
KOLLEKTION: {collection_name}

ORIGINAL-TEXT vom Hersteller:
{raw_text[:1500]}

---

Erstelle:
1. KURZBESCHREIBUNG: (max 200 Zeichen)
2. VOLLTEXT: Detaillierte Beschreibung mit:
   - Stil und Design
   - Materialien und Eigenschaften
   - Einsatzbereiche (Bad, Küche, Wohnbereich etc.)
   - Formate und Verlegeoptionen (falls im Original erwähnt)
   
   Schließe mit lokalem CTA ab:
   "Diese Kollektion ist in unserem Showroom in Frankfurt (Hanauer Landstraße 421) ausgestellt. Besuchen Sie uns für eine persönliche Beratung – kostenlose Parkplätze direkt vor Ort."

WICHTIG: 
- Keine generischen Phrasen wie "diese Serie bietet..."
- Konkret und bildhaft schreiben
- Auf Deutsch für Frankfurt-Publikum"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            # Парсим ответ - ищем KURZBESCHREIBUNG и VOLLTEXT
            description = ""
            full_content = ""
            
            # Ищем секции
            kurz_match = re.search(r'(?:KURZBESCHREIBUNG:|1\.\s*KURZBESCHREIBUNG:?)\s*(.+?)(?=\n\n|2\.|VOLLTEXT:|$)', 
                                  content, re.DOTALL | re.IGNORECASE)
            if kurz_match:
                description = kurz_match.group(1).strip()
                # Убираем кавычки если есть
                description = description.strip('"').strip()
            
            voll_match = re.search(r'(?:VOLLTEXT:|2\.\s*VOLLTEXT:?)\s*(.+)', 
                                  content, re.DOTALL | re.IGNORECASE)
            if voll_match:
                full_content = voll_match.group(1).strip()
            
            # Если не нашли разделение, пробуем взять весь текст
            if not description and not full_content:
                lines = content.split('\n\n')
                if len(lines) >= 2:
                    description = lines[0].strip()
                    full_content = '\n\n'.join(lines[1:]).strip()
                else:
                    description = content[:200].strip()
                    full_content = content.strip()
            
            # Форматируем full_content в HTML
            full_content_html = self._format_as_html(full_content)
            
            # Валидация длины
            if len(description) > 250:
                description = description[:247] + "..."
            
            return {
                'description': description or f"{collection_name} von {manufacturer_name}",
                'full_content': full_content_html or f"<p>{description}</p>"
            }
            
        except Exception as e:
            print(f"  ⚠️  Ошибка OpenAI обработки: {str(e)}")
            return self._generate_fallback_description(collection_name, manufacturer_name)
    
    def process_project_description(self,
                                   raw_text: str,
                                   project_name: str,
                                   manufacturer_name: str) -> Dict[str, str]:
        """
        Обрабатывает описание проекта через OpenAI
        
        Args:
            raw_text: Сырой текст с сайта
            project_name: Название проекта
            manufacturer_name: Производитель
            
        Returns:
            Dict с description и full_content
        """
        
        if not raw_text or len(raw_text.strip()) < 20:
            return {
                'description': f"Referenzprojekt mit {manufacturer_name} Fliesen: {project_name}",
                'full_content': f"<p>Referenzprojekt mit hochwertigen Fliesen von {manufacturer_name}.</p>"
            }
        
        system_prompt = """Du bist ein Experte für Architektur und Fliesendesign in Deutschland.

Aufgabe: Verarbeite Projektbeschreibungen von Fliesenherstellern (Referenzprojekte) für unseren Showroom.

WICHTIG:
- Deutsch für deutsches Publikum
- Fokus auf Design-Inspiration für Kunden
- Entferne generische Marketing-Texte
- Zeige konkrete Anwendungsbeispiele
- Ton: Inspirierend aber professionell"""

        user_prompt = f"""PROJEKT: {project_name}
HERSTELLER: {manufacturer_name}

ORIGINAL:
{raw_text[:1000]}

---

Erstelle:
1. KURZ (max 150 Zeichen): Was wurde gemacht, wo (falls genannt)
2. VOLLTEXT (100-150 Wörter): 
   - Art des Projekts (Hotel, Restaurant, Wohnhaus etc.)
   - Verwendete Fliesen/Kollektionen
   - Design-Highlights
   - Inspiration für eigene Projekte
   
Schließe mit: "Lassen Sie sich inspirieren! Besuchen Sie unseren Showroom in Frankfurt für eigene Projektideen."

Auf Deutsch, keine generischen Phrasen."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Парсим
            description = ""
            full_content = ""
            
            kurz_match = re.search(r'(?:KURZ:|1\.\s*KURZ:?)\s*(.+?)(?=\n\n|2\.|VOLLTEXT:|$)', 
                                  content, re.DOTALL | re.IGNORECASE)
            if kurz_match:
                description = kurz_match.group(1).strip().strip('"')
            
            voll_match = re.search(r'(?:VOLLTEXT:|2\.\s*VOLLTEXT:?)\s*(.+)', 
                                  content, re.DOTALL | re.IGNORECASE)
            if voll_match:
                full_content = voll_match.group(1).strip()
            
            if not description and not full_content:
                lines = content.split('\n\n')
                description = lines[0][:150] if lines else content[:150]
                full_content = content
            
            full_content_html = self._format_as_html(full_content)
            
            if len(description) > 180:
                description = description[:177] + "..."
            
            return {
                'description': description or f"{project_name} – {manufacturer_name}",
                'full_content': full_content_html or f"<p>{description}</p>"
            }
            
        except Exception as e:
            print(f"  ⚠️  Ошибка OpenAI: {str(e)}")
            return {
                'description': f"Referenzprojekt: {project_name} mit {manufacturer_name}",
                'full_content': f"<p>Hochwertiges Referenzprojekt mit Fliesen von {manufacturer_name}.</p>"
            }
    
    def _format_as_html(self, text: str) -> str:
        """Преобразует текст в простой HTML"""
        if not text:
            return ""
        
        # Разбиваем на параграфы
        paragraphs = text.split('\n\n')
        html_parts = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Проверяем на заголовки (начинаются с "##" или просто жирный текст)
            if para.startswith('**') and para.endswith('**'):
                # Подзаголовок
                clean = para.strip('*').strip()
                html_parts.append(f'<h4 class="fw-bold mt-3 mb-2">{clean}</h4>')
            elif para.startswith('- ') or para.startswith('• '):
                # Список
                items = [item.strip('- •').strip() for item in para.split('\n') if item.strip()]
                if items:
                    html_parts.append('<ul>')
                    for item in items:
                        html_parts.append(f'<li>{item}</li>')
                    html_parts.append('</ul>')
            else:
                # Обычный параграф
                # Заменяем жирный текст
                para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
                html_parts.append(f'<p>{para}</p>')
        
        return '\n'.join(html_parts)
    
    def _generate_fallback_description(self, collection_name: str, manufacturer_name: str) -> Dict[str, str]:
        """Генерирует базовое описание если основное не получилось"""
        description = f"{collection_name} – Hochwertige Fliesenkollektion von {manufacturer_name}"
        
        full_content = f"""<p><strong>{collection_name}</strong> von {manufacturer_name} – eine exklusive Fliesenkollektion mit zeitlosem Design.</p>

<p>Weitere Informationen und Muster erhalten Sie in unserem Showroom in Frankfurt (Hanauer Landstraße 421). 
Wir beraten Sie gerne persönlich – kostenlose Parkplätze direkt vor Ort.</p>"""
        
        return {
            'description': description,
            'full_content': full_content
        }


# Singleton instance
_processor_instance = None

def get_content_processor() -> ContentProcessor:
    """Возвращает singleton instance процессора"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = ContentProcessor()
    return _processor_instance
