import os
import json
import google.generativeai as genai
import logging  
from typing import Optional, Dict, Any
from models.schemas import ExtractedInvoiceData
from dotenv import load_dotenv

load_dotenv()

# Configure logging to match main.py
logger = logging.getLogger("uvicorn")

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    logger.error("GEMINI_API_KEY not found in environment variables!")

class LLMService:
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        self.model = genai.GenerativeModel(model_name)

    async def extract_invoice_data(self, content: Any, is_file: bool = False, filename: Optional[str] = None) -> Optional[ExtractedInvoiceData]:
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
        Ensure all numeric values are numbers, not strings with symbols.
        """

        try:
            if is_file:
                import mimetypes
                mime_type = mimetypes.guess_type(filename)[0] if filename else "application/pdf"
                
                # If it's a text-based file, read it as a string instead of a multi-modal blob
                if mime_type and (mime_type.startswith("text/") or mime_type == "application/json"):
                    text_content = content.decode("utf-8", errors="ignore")
                    response = self.model.generate_content(f"{prompt}\n\nInvoice Content (from {filename}):\n{text_content}")
                else:
                    if not mime_type:
                        mime_type = "application/pdf"
                    
                    # Use a list for multi-modal input
                    response = self.model.generate_content([
                        prompt,
                        {"mime_type": mime_type, "data": content}
                    ])
            else:
                if isinstance(content, dict):
                    content = json.dumps(content, indent=2)
                response = self.model.generate_content(f"{prompt}\n\nInvoice Content:\n{content}")

            # Safety check
            if not response or not response.candidates:
                logger.error("No candidates in LLM response.")
                return None
            
            finish_reason = response.candidates[0].finish_reason
            if finish_reason != 1: # 1 is STOP
                logger.warning(f"Response finished with reason: {finish_reason}")

            text_response = response.text.strip()
            
            # Robust JSON extraction
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif "```" in text_response:
                text_response = text_response.split("```")[1].split("```")[0].strip()
            
            start_index = text_response.find('{')
            end_index = text_response.rfind('}')
            if start_index != -1 and end_index != -1:
                text_response = text_response[start_index:end_index+1]

            data = json.loads(text_response)
            
            # Field normalization
            required_fields = ["vendor_name", "invoice_number", "invoice_date", "line_items", "total_amount", "currency"]
            for field in required_fields:
                if field not in data or data[field] is None:
                    if field == "line_items":
                        data[field] = []
                    elif field == "total_amount":
                        data[field] = 0.0
                    else:
                        data[field] = "N/A"

            try:
                return ExtractedInvoiceData(**data)
            except Exception as ve:
                logger.error(f"Pydantic Validation Error: {ve}")
                logger.error(f"Data that failed validation: {json.dumps(data, indent=2)}")
                return None

        except json.JSONDecodeError as je:
            logger.error(f"JSON Decode Error: {je}")
            logger.error(f"Attempted to parse: {text_response if 'text_response' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            if 'response' in locals() and response:
                try:
                    logger.info(f"Response candidate 0: {response.candidates[0] if response.candidates else 'No candidates'}")
                except Exception as re:
                    logger.error(f"Could not retrieve response details: {re}")
            return None

# Singleton instance
llm_service = LLMService()
