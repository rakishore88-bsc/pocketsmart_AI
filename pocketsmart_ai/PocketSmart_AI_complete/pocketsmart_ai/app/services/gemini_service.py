from __future__ import annotations

import json
from typing import Any

from app.config import get_settings
from app.models.schemas import HomeRequest, JewelryRequest, PartyRequest, RecommendationResponse
from app.services.recommendation_service import home_fallback, jewelry_fallback, party_fallback

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None
    types = None


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = None
        if genai and self.settings.gemini_api_key:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def _generate(self, prompt: str, image_bytes: bytes | None = None, mime_type: str | None = None) -> RecommendationResponse:
        if not self.client:
            raise RuntimeError("Gemini API is not configured")

        contents: list[Any] = [prompt]
        if image_bytes and mime_type:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

        response = self.client.models.generate_content(
            model=self.settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=3000,
                response_mime_type="application/json",
                response_schema=RecommendationResponse,
                system_instruction=(
                    "You are PocketSmart AI, a budget-aware recommendation assistant. "
                    "Return only valid structured data matching the requested schema. "
                    "Do not claim real-time prices or inventory unless provided. Use estimated prices. "
                    "Platform URLs must be normal public search URLs, not invented product-detail URLs."
                ),
            ),
        )
        if getattr(response, "parsed", None) is not None:
            return response.parsed
        return RecommendationResponse.model_validate(json.loads(response.text))

    def home(self, data: HomeRequest) -> RecommendationResponse:
        prompt = f"""Create a home interior recommendation plan. Budget: {data.currency} {data.budget}. Rooms: {data.rooms}. Style: {data.style}. Quantities: {data.quantities}. Notes: {data.notes}. Recommend products across Amazon, IKEA and Flipkart. Keep the total estimated recommendation spend aligned with the budget and clearly mark estimates."""
        try:
            result = self._generate(prompt)
            result.planner = "home"
            return result
        except Exception:
            return home_fallback(data)

    def party(self, data: PartyRequest) -> RecommendationResponse:
        prompt = f"""Create a party budget plan. Budget: {data.currency} {data.budget}. Guests: {data.guests}. Event: {data.event_type}. Area: {data.venue_area}. Food preference: {data.food_preference}. Notes: {data.notes}. Allocate money across food, venue, decoration and entertainment. Use Swiggy, Zomato, OYO and Amazon as research destinations where appropriate. Use estimated prices only."""
        try:
            result = self._generate(prompt)
            result.planner = "party"
            return result
        except Exception:
            return party_fallback(data)

    def jewelry(self, data: JewelryRequest, image_bytes: bytes | None = None, mime_type: str | None = None) -> RecommendationResponse:
        prompt = f"""Create a jewelry recommendation plan. Budget: {data.currency} {data.budget}. Occasion: {data.occasion}. Style: {data.style}. Metal: {data.metal}. Outfit description: {data.outfit_description}. Notes: {data.notes}. If an outfit image is supplied, use it only to describe broad colors, patterns and styling cues. Recommend jewelry research options from Amazon and Flipkart. Do not make claims about precious-metal authenticity. Use estimated prices."""
        try:
            result = self._generate(prompt, image_bytes, mime_type)
            result.planner = "jewelry"
            return result
        except Exception:
            return jewelry_fallback(data)
