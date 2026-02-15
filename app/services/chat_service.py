"""
ChatBot Service — интеграция с OpenAI и управление сообщениями
"""
import os
from openai import OpenAI


class ChatBotService:
    """Service for managing chatbot responses using OpenAI API."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def get_system_prompt(self, custom_instructions=""):
        """Construct full system prompt with company info and custom instructions."""
        
        # Base system instructions
        base_prompt = """Du bist ein hilfreicher Kundenservice-Assistent für einen Fliesen Showroom in Frankfurt.

UNTERNEHMENSINFO:
Name: günstige-fliesen.de (Hermitage Home & Design GmbH & Co KG)
Adresse: Hanauer Landstrasse 421, 60314 Frankfurt am Main
Telefon: 069 90475570
E-Mail: info@hermitage-frankfurt.de
Öffnungszeiten: Mo–Fr 09:00 – 18:00, Sa 10:00 – 14:00

HAUPT-AUFGABE:
- Beantwortung von Fragen zu Fliesen, Kollektionen und Dienstleistungen
- Terminvereinbarungen erleichtern
- Kundenanfragen freundlich und professionell bearbeiten
- Bei Bedarf zur Website oder zum persönlichen Besuch einladen

VERHALTEN:
- Antworten Sie immer in der Sprache, in der die Frage gestellt wurde (Deutsch, Englisch, etc.)
- Seien Sie freundlich, hilfreich und professionell
- Halten Sie Antworten prägnant und relevant
- Bei Fragen außerhalb des Bereichs: höflich ablehnen und auf Fachgebiet hinweisen
- Empfehlen Sie bei komplexen Anfragen einen Termin im Showroom"""

        # Add custom instructions from admin (if any) with explicit precedence
        if custom_instructions:
            base_prompt += (
                "\n\nWICHTIG: Admin-Anweisungen haben Vorrang vor Basis-Angaben. "
                "Wenn dort abweichende Kontakt- oder Unternehmensdaten stehen, nutze diese."
                f"\n\nADMIN-ANWEISUNGEN:\n{custom_instructions}"
            )

        return base_prompt

    def chat(self, user_message, custom_instructions=""):
        """
        Send user message to OpenAI and get response.
        Falls back to default response if API is not configured.
        
        Args:
            user_message (str): User's message
            custom_instructions (str): Custom instructions from admin
            
        Returns:
            str: Bot response
        """
        
        if not self.client or not self.api_key:
            return self._get_fallback_response()

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self.get_system_prompt(custom_instructions)
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return self._get_fallback_response()

    def _get_fallback_response(self):
        """Fallback response when OpenAI API is not available."""
        return (
            "Vielen Dank für Ihre Anfrage! Leider kann unser Chat gerade keine KI-gestützte Antwort "
            "generieren. Bitte kontaktieren Sie uns direkt: 069 90475570 oder "
            "info@hermitage-frankfurt.de. Wir helfen Ihnen gerne weiter!"
        )

    def detect_language(self, text):
        """
        Simple language detection (DE, EN, FR, etc.)
        Returns 2-letter language code
        """
        # Simple heuristic-based detection
        de_words = ["guten", "tag", "hallo", "fragen", "danke", "bitte", "wie", "was", "warum"]
        en_words = ["hello", "hi", "thanks", "please", "what", "why", "how", "question"]
        
        text_lower = text.lower()
        
        de_count = sum(1 for word in de_words if word in text_lower)
        en_count = sum(1 for word in en_words if word in text_lower)
        
        if de_count > en_count:
            return "de"
        elif en_count > 0:
            return "en"
        
        # Default to German for this showroom
        return "de"


# Singleton instance
_chat_service = None

def get_chat_service():
    """Get or create chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatBotService()
    return _chat_service
