"""
AI Analyzer Service
Uses Gemini or Qwen for multimodal analysis of PowerPoint content
"""

import os
import json
import base64
import httpx
import asyncio
from typing import Optional, Dict, List, Any

class AIAnalyzer:
    """AI-powered presentation analyzer using Gemini or Qwen"""

    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key or os.environ.get(
            "GEMINI_API_KEY" if provider == "gemini" else "REPLICATE_API_TOKEN"
        )

        if provider == "gemini":
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
            self.model = "gemini-1.5-flash"
        else:
            self.base_url = "https://api.replicate.com/v1"
            self.model = "qwen/qwen-vl-chat"

    async def analyze_slide(self, slide_image_b64: str, slide_content: Dict) -> Dict:
        """Analyze a single slide for content understanding and redesign recommendations"""

        prompt = f"""Analyze this PowerPoint slide and provide detailed information for redesign.

Current slide content:
{json.dumps(slide_content, indent=2)}

Please analyze and return a JSON object with:
1. "content_type": The type of content (title, data, comparison, process, timeline, etc.)
2. "key_message": The main message or takeaway
3. "visual_elements": List of visual elements present
4. "suggested_layout": Best layout approach for this content
5. "emphasis_elements": What should be visually emphasized
6. "content_hierarchy": Order of importance for elements
7. "color_suggestions": Colors that would work well with content meaning
8. "improvement_notes": Specific improvements for clarity and impact

Respond ONLY with valid JSON, no markdown formatting."""

        if self.provider == "gemini":
            return await self._analyze_with_gemini(prompt, slide_image_b64)
        else:
            return await self._analyze_with_replicate(prompt, slide_image_b64)

    async def analyze_presentation_structure(self, slides_data: List[Dict]) -> Dict:
        """Analyze the overall presentation structure"""

        slides_summary = []
        for i, slide in enumerate(slides_data):
            slides_summary.append({
                "slide_number": i + 1,
                "layout_type": slide.get("layout_type"),
                "has_chart": slide.get("has_chart"),
                "has_table": slide.get("has_table"),
                "text_preview": slide.get("text_content", [])[:2]
            })

        prompt = f"""Analyze this presentation structure and provide redesign recommendations.

Presentation slides:
{json.dumps(slides_summary, indent=2)}

Return a JSON object with:
1. "presentation_type": Type of presentation (pitch, report, educational, etc.)
2. "narrative_flow": How the content flows (linear, problem-solution, etc.)
3. "section_breaks": Recommended section break points
4. "pacing_notes": Notes on information density and pacing
5. "consistency_issues": Any inconsistencies to address
6. "design_direction": Overall design direction recommendation
7. "special_slides": Slides that need special treatment (title, conclusion, etc.)

Respond ONLY with valid JSON."""

        if self.provider == "gemini":
            return await self._analyze_with_gemini(prompt)
        else:
            return await self._analyze_with_replicate(prompt)

    async def suggest_style_match(self, presentation_analysis: Dict, available_styles: List[Dict]) -> Dict:
        """Suggest the best matching styles for the presentation"""

        prompt = f"""Based on this presentation analysis, recommend the best design styles.

Presentation Analysis:
{json.dumps(presentation_analysis, indent=2)}

Available Styles:
{json.dumps([{{"id": s["id"], "name": s["name"], "category": s["category"], "description": s["description"]}} for s in available_styles], indent=2)}

Return a JSON object with:
1. "top_recommendations": Top 3 style IDs with reasons
2. "avoid_styles": Styles that wouldn't work well
3. "customization_notes": Any style customizations needed
4. "audience_considerations": How audience affects style choice

Respond ONLY with valid JSON."""

        if self.provider == "gemini":
            return await self._analyze_with_gemini(prompt)
        else:
            return await self._analyze_with_replicate(prompt)

    async def generate_slide_layout(self, slide_content: Dict, style: Dict, slide_analysis: Dict) -> Dict:
        """Generate optimal layout for a slide based on content and style"""

        prompt = f"""Create an optimal slide layout for this content.

Content:
{json.dumps(slide_content, indent=2)}

Style Theme:
{json.dumps(style.get('theme', {}), indent=2)}

Analysis:
{json.dumps(slide_analysis, indent=2)}

Return a JSON object with:
1. "layout_type": The layout pattern to use
2. "elements": Array of elements with:
   - type (title, body, bullet, image, chart, shape)
   - content
   - position (x, y, width, height as percentages)
   - styling (font_size, color, alignment, etc.)
3. "background": Background specification
4. "accent_elements": Decorative elements to add
5. "spacing": Spacing values for the layout

Respond ONLY with valid JSON."""

        if self.provider == "gemini":
            return await self._analyze_with_gemini(prompt)
        else:
            return await self._analyze_with_replicate(prompt)

    async def _analyze_with_gemini(self, prompt: str, image_b64: Optional[str] = None) -> Dict:
        """Call Gemini API for analysis"""
        if not self.api_key:
            return self._get_fallback_response("No API key provided")

        url = f"{self.base_url}/models/{self.model}:generateContent"

        parts = [{"text": prompt}]

        if image_b64:
            parts.insert(0, {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_b64
                }
            })

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{url}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json()
                    text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                    # Clean the response
                    text = text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.startswith("```"):
                        text = text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    return json.loads(text.strip())
                else:
                    return self._get_fallback_response(f"API error: {response.status_code}")

        except Exception as e:
            return self._get_fallback_response(str(e))

    async def _analyze_with_replicate(self, prompt: str, image_b64: Optional[str] = None) -> Dict:
        """Call Replicate API for Qwen analysis"""
        if not self.api_key:
            return self._get_fallback_response("No API key provided")

        url = f"{self.base_url}/predictions"

        input_data = {"prompt": prompt}

        if image_b64:
            input_data["image"] = f"data:image/jpeg;base64,{image_b64}"

        payload = {
            "version": "qwen/qwen-vl-chat",
            "input": input_data
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    # Handle Replicate's async response
                    if data.get("status") == "starting" or data.get("status") == "processing":
                        prediction_url = data.get("urls", {}).get("get")
                        if prediction_url:
                            # Poll for result
                            for _ in range(30):
                                await asyncio.sleep(2)
                                result = await client.get(
                                    prediction_url,
                                    headers={"Authorization": f"Token {self.api_key}"}
                                )
                                result_data = result.json()
                                if result_data.get("status") == "succeeded":
                                    output = result_data.get("output", "")
                                    return json.loads(output)
                                elif result_data.get("status") == "failed":
                                    return self._get_fallback_response("Prediction failed")

                    output = data.get("output", "{}")
                    return json.loads(output) if isinstance(output, str) else output
                else:
                    return self._get_fallback_response(f"API error: {response.status_code}")

        except Exception as e:
            return self._get_fallback_response(str(e))

    def _get_fallback_response(self, error_msg: str) -> Dict:
        """Return a fallback response when AI analysis fails"""
        return {
            "error": error_msg,
            "content_type": "general",
            "key_message": "Content preserved from original",
            "visual_elements": [],
            "suggested_layout": "standard",
            "emphasis_elements": [],
            "content_hierarchy": [],
            "color_suggestions": [],
            "improvement_notes": "Using default redesign approach"
        }


class DesignIntelligence:
    """
    Rule-based design intelligence as fallback/supplement to AI
    Provides deterministic design decisions
    """

    @staticmethod
    def analyze_content_type(slide_data: Dict) -> str:
        """Determine content type from slide data"""
        text_content = slide_data.get("text_content", [])

        if not text_content:
            if slide_data.get("images"):
                return "image_focused"
            return "empty"

        # Check for title slide indicators
        if len(text_content) <= 2:
            types = [t.get("type", "") for t in text_content]
            if "ctrTitle" in types or "subTitle" in types:
                return "title_slide"

        # Check for data presentation
        if slide_data.get("has_chart") or slide_data.get("has_table"):
            return "data_presentation"

        # Check text patterns
        all_text = " ".join([t.get("text", "") for t in text_content]).lower()

        if any(word in all_text for word in ["step", "process", "phase", "stage"]):
            return "process"
        if any(word in all_text for word in ["compare", "versus", "vs", "difference"]):
            return "comparison"
        if any(word in all_text for word in ["timeline", "history", "roadmap"]):
            return "timeline"
        if any(word in all_text for word in ["question", "?", "faq"]):
            return "qa"
        if any(word in all_text for word in ["thank", "contact", "questions?"]):
            return "closing"

        # Count bullet points
        bullet_count = sum(1 for t in text_content if t.get("type") == "body")
        if bullet_count > 4:
            return "detailed_content"

        return "standard_content"

    @staticmethod
    def get_layout_recommendation(content_type: str, element_count: int) -> Dict:
        """Get layout recommendation based on content type"""
        layouts = {
            "title_slide": {
                "type": "centered",
                "title_position": "center",
                "columns": 1,
                "vertical_balance": "center"
            },
            "data_presentation": {
                "type": "split",
                "title_position": "top",
                "columns": 2,
                "chart_position": "right"
            },
            "process": {
                "type": "horizontal_flow",
                "title_position": "top",
                "columns": "auto",
                "element_style": "connected"
            },
            "comparison": {
                "type": "side_by_side",
                "title_position": "top",
                "columns": 2,
                "visual_separator": True
            },
            "timeline": {
                "type": "horizontal_timeline",
                "title_position": "top",
                "flow_direction": "left_to_right"
            },
            "closing": {
                "type": "centered",
                "title_position": "center",
                "columns": 1,
                "emphasis": "high"
            },
            "standard_content": {
                "type": "title_body",
                "title_position": "top",
                "columns": 1,
                "body_layout": "bullets" if element_count > 2 else "paragraphs"
            },
            "detailed_content": {
                "type": "two_column_content",
                "title_position": "top",
                "columns": 2,
                "body_layout": "split_bullets"
            }
        }

        return layouts.get(content_type, layouts["standard_content"])

    @staticmethod
    def calculate_font_sizes(text_content: List[Dict], slide_width: float, slide_height: float) -> Dict:
        """Calculate optimal font sizes based on content"""
        total_text_length = sum(len(t.get("text", "")) for t in text_content)

        # Base sizes for 960x540
        if total_text_length < 100:
            return {"title": 44, "subtitle": 24, "body": 20, "caption": 14}
        elif total_text_length < 300:
            return {"title": 40, "subtitle": 22, "body": 18, "caption": 12}
        elif total_text_length < 500:
            return {"title": 36, "subtitle": 20, "body": 16, "caption": 11}
        else:
            return {"title": 32, "subtitle": 18, "body": 14, "caption": 10}

    @staticmethod
    def get_color_application(style_theme: Dict, content_type: str) -> Dict:
        """Determine how to apply style colors based on content"""
        primary = style_theme.get("primary", "#000000")
        secondary = style_theme.get("secondary", "#ffffff")
        accent = style_theme.get("accent", primary)
        background = style_theme.get("background", "#ffffff")
        text_color = style_theme.get("text", "#000000")

        applications = {
            "title_slide": {
                "background": primary,
                "title_color": style_theme.get("primary_foreground", "#ffffff"),
                "subtitle_color": style_theme.get("text_muted", "#cccccc"),
                "accent_uses": ["decorative_shape"]
            },
            "data_presentation": {
                "background": background,
                "title_color": text_color,
                "chart_colors": [primary, accent, secondary],
                "accent_uses": ["data_highlight"]
            },
            "standard_content": {
                "background": background,
                "title_color": primary,
                "body_color": text_color,
                "accent_uses": ["bullets", "emphasis"]
            },
            "closing": {
                "background": primary,
                "title_color": style_theme.get("primary_foreground", "#ffffff"),
                "accent_uses": ["cta_button"]
            }
        }

        return applications.get(content_type, applications["standard_content"])
