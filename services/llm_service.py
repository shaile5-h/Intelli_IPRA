import os
import json
import google.generativeai as genai
from typing import Optional, Dict, Any
from models.schemas import ExtractedInvoiceData
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class LLMService:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    async def extract_invoice_data(self, content: Any, is_file: bool = False) -> Optional[ExtractedInvoiceData]:
        """
        Extracts structured invoice data from text or file bytes using Gemini.
        """
        prompt = """
        Extract the following fields from the provided invoice content and return them in a strict JSON format:
        - vendor_name
        - invoice_number
        - invoice_date (ISO format YYYY-MM-DD)
        - line_items (list of objects with description, qty, unit_price)
        - total_amount (numeric)
        - currency (3-letter ISO code)
        - po_reference

        Return ONLY the JSON object. Do not include markdown formatting or extra text.
        """

        try:
            if is_file:
                # content is bytes
                # For simplicity, we assume image or PDF that Gemini can handle
                # We need to wrap it in the expected format
                response = self.model.generate_content([
                    prompt,
                    {"mime_type": "application/pdf", "data": content} # Adjust mime_type if needed
                ])
            else:
                # content is text or dict converted to string
                response = self.model.generate_content(f"{prompt}\n\nInvoice Content:\n{content}")

            # Extract JSON from response
            text_response = response.text.strip()
            # Remove potential markdown code blocks
            if text_response.startswith("```json"):
                text_response = text_response[7:-3].strip()
            elif text_response.startswith("```"):
                text_response = text_response[3:-3].strip()

            data = json.loads(text_response)
            return ExtractedInvoiceData(**data)
        except Exception as e:
            print(f"Error in LLM extraction: {e}")
            return None

# Singleton instance
llm_service = LLMService()
