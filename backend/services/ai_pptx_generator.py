"""
AI-Powered PPTX Generator
Uses Qwen AI to analyze content and generate custom designs for each slide
No templates - pure AI-driven design decisions
"""

import os
import json
import httpx
import asyncio
from typing import Dict, List, Optional, Tuple
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


def hex_to_rgb(hex_color: str) -> RGBColor:
    """Convert hex color to RGBColor"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
    return RGBColor(0, 0, 0)


DESIGN_PROMPT = """You are a world-class PowerPoint designer. Analyze this slide content and generate specific design instructions.

SLIDE CONTENT:
{content}

SLIDE POSITION: {position} of {total} slides
PRESENTATION CONTEXT: {context}

Generate a JSON response with these exact fields:
{{
    "layout": "hero|content_cards|two_column|grid|stats|quote|closing",
    "background": {{
        "type": "solid|gradient",
        "primary_color": "#hex",
        "secondary_color": "#hex or null",
        "gradient_direction": "diagonal|vertical|horizontal or null"
    }},
    "title": {{
        "text": "cleaned/shortened title",
        "color": "#hex",
        "size": 28-54,
        "bold": true/false,
        "position": "top-left|center|bottom"
    }},
    "content_style": {{
        "type": "bullets|cards|numbered|paragraphs",
        "accent_color": "#hex",
        "text_color": "#hex",
        "card_bg_color": "#hex or null"
    }},
    "decorations": [
        {{"type": "circle|rectangle|line|triangle", "position": "top-right|bottom-left|etc", "color": "#hex", "size": "small|medium|large"}}
    ],
    "mood": "professional|energetic|calm|bold|minimal",
    "key_message": "the main takeaway in 10 words or less"
}}

Consider:
- First slide should be impactful hero/title
- Last slide should be memorable closing
- Use colors that complement each other
- Keep text readable (dark on light or light on dark)
- Limit to 6 content items max per slide
- Make design serve the message

Respond ONLY with valid JSON, no explanation."""


class AIPPTXGenerator:
    """AI-powered PPTX generator using Qwen for design decisions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("REPLICATE_API_TOKEN")
        self.replicate_url = "https://api.replicate.com/v1/models/meta/meta-llama-3-70b-instruct/predictions"
        self.presentation_context = ""
        
    async def generate_presentation(
        self, 
        slides_data: List[Dict],
        output_path: str
    ) -> str:
        """Generate a complete presentation with AI-designed slides"""
        
        # Create presentation
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        
        # First, analyze overall presentation for context
        all_content = []
        for slide in slides_data:
            texts = self._extract_texts(slide.get('original_content', []))
            all_content.extend(texts[:3])  # First 3 items from each slide
        
        self.presentation_context = " | ".join(all_content[:10])[:500]
        
        # Generate each slide with AI design
        total = len(slides_data)
        for i, slide_data in enumerate(slides_data):
            print(f"[AI Generator] Designing slide {i+1}/{total}...")
            
            # Get AI design instructions
            design = await self._get_ai_design(slide_data, i, total)
            
            # Create slide with AI design
            self._create_ai_slide(prs, slide_data, design, i, total)
        
        prs.save(output_path)
        return output_path
    
    def _extract_texts(self, original_content: List) -> List[str]:
        """Extract text items from content"""
        texts = []
        skip_types = ['sldNum', 'ftr', 'dt', 'hdr']
        
        for item in original_content:
            if isinstance(item, str):
                text = item.strip()
            else:
                if item.get('type') in skip_types:
                    continue
                text = item.get('text', '').strip()
            
            if text and not (text.isdigit() and len(text) <= 3):
                texts.append(text)
        
        return texts
    
    async def _get_ai_design(self, slide_data: Dict, index: int, total: int) -> Dict:
        """Get AI-generated design instructions for a slide"""
        texts = self._extract_texts(slide_data.get('original_content', []))
        content_summary = "\n".join([f"- {t[:100]}" for t in texts[:8]])
        
        position = "first (title slide)" if index == 0 else \
                   "last (closing slide)" if index == total - 1 else \
                   f"middle ({index + 1})"
        
        prompt = DESIGN_PROMPT.format(
            content=content_summary,
            position=position,
            total=total,
            context=self.presentation_context[:300]
        )
        
        try:
            design = await self._call_qwen(prompt)
            return design
        except Exception as e:
            print(f"[AI Generator] AI call failed: {e}, using fallback")
            return self._get_fallback_design(index, total, texts)
    
    async def _call_qwen(self, prompt: str) -> Dict:
        """Call Qwen/Llama via Replicate API"""
        if not self.api_key:
            raise ValueError("No API key available")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.replicate_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "input": {
                        "prompt": prompt,
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                }
            )
            
            if response.status_code != 201:
                raise Exception(f"API error: {response.status_code}")
            
            result = response.json()
            prediction_url = result.get('urls', {}).get('get')
            
            # Poll for result
            for _ in range(30):
                await asyncio.sleep(1)
                poll_response = await client.get(
                    prediction_url,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                poll_result = poll_response.json()
                
                if poll_result.get('status') == 'succeeded':
                    output = poll_result.get('output', '')
                    if isinstance(output, list):
                        output = ''.join(output)
                    
                    # Parse JSON from output
                    return self._parse_json_response(output)
                elif poll_result.get('status') == 'failed':
                    raise Exception("Prediction failed")
            
            raise Exception("Timeout waiting for AI response")
    
    def _parse_json_response(self, text: str) -> Dict:
        """Parse JSON from AI response"""
        # Try to find JSON in the response
        text = text.strip()
        
        # Look for JSON block
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            text = text[start:end].strip()
        elif '```' in text:
            start = text.find('```') + 3
            end = text.find('```', start)
            text = text[start:end].strip()
        
        # Find JSON object
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            return json.loads(json_str)
        
        raise ValueError("No valid JSON found in response")
    
    def _get_fallback_design(self, index: int, total: int, texts: List[str]) -> Dict:
        """Generate fallback design without AI"""
        is_first = index == 0
        is_last = index == total - 1
        
        # Color palettes
        palettes = [
            {"bg": "#1e3a5f", "accent": "#00d4aa", "text": "#ffffff"},
            {"bg": "#2d1b4e", "accent": "#ff6b6b", "text": "#ffffff"},
            {"bg": "#0f4c5c", "accent": "#ffd166", "text": "#ffffff"},
            {"bg": "#1a1a2e", "accent": "#00b4d8", "text": "#ffffff"},
            {"bg": "#f8f9fa", "accent": "#0077b6", "text": "#1a1a2e"},
        ]
        palette = palettes[index % len(palettes)]
        
        if is_first:
            return {
                "layout": "hero",
                "background": {"type": "solid", "primary_color": palette["bg"]},
                "title": {
                    "text": texts[0][:60] if texts else "Presentation",
                    "color": palette["text"],
                    "size": 48,
                    "bold": True,
                    "position": "center"
                },
                "content_style": {
                    "type": "paragraphs",
                    "accent_color": palette["accent"],
                    "text_color": palette["text"]
                },
                "decorations": [
                    {"type": "circle", "position": "top-right", "color": palette["accent"], "size": "large"},
                    {"type": "circle", "position": "bottom-left", "color": palette["accent"], "size": "medium"}
                ],
                "mood": "bold",
                "key_message": texts[0][:50] if texts else ""
            }
        elif is_last:
            return {
                "layout": "closing",
                "background": {"type": "solid", "primary_color": palette["bg"]},
                "title": {
                    "text": "Thank You",
                    "color": palette["text"],
                    "size": 54,
                    "bold": True,
                    "position": "center"
                },
                "content_style": {
                    "type": "paragraphs",
                    "accent_color": palette["accent"],
                    "text_color": palette["text"]
                },
                "decorations": [
                    {"type": "circle", "position": "bottom-right", "color": palette["accent"], "size": "large"}
                ],
                "mood": "professional",
                "key_message": "Questions?"
            }
        else:
            layout = "grid" if len(texts) > 5 else "content_cards"
            return {
                "layout": layout,
                "background": {"type": "solid", "primary_color": palette["bg"]},
                "title": {
                    "text": texts[0][:50] if texts else f"Slide {index + 1}",
                    "color": palette["text"],
                    "size": 32,
                    "bold": True,
                    "position": "top-left"
                },
                "content_style": {
                    "type": "cards",
                    "accent_color": palette["accent"],
                    "text_color": palette["text"],
                    "card_bg_color": "#ffffff20"
                },
                "decorations": [
                    {"type": "line", "position": "top", "color": palette["accent"], "size": "small"}
                ],
                "mood": "professional",
                "key_message": texts[0][:40] if texts else ""
            }
    
    def _create_ai_slide(self, prs: Presentation, slide_data: Dict, design: Dict, index: int, total: int):
        """Create a slide using AI-generated design instructions"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
        
        texts = self._extract_texts(slide_data.get('original_content', []))
        
        # Apply background
        bg = design.get('background', {})
        bg_color = bg.get('primary_color', '#1a1a2e')
        self._set_background(slide, bg_color)
        
        # Add decorations first (behind content)
        for deco in design.get('decorations', []):
            self._add_decoration(slide, deco)
        
        # Get design params
        title_config = design.get('title', {})
        content_style = design.get('content_style', {})
        layout = design.get('layout', 'content_cards')
        
        # Title
        title_text = title_config.get('text', texts[0] if texts else '')
        if title_text:
            self._add_title(slide, title_text, title_config)
        
        # Content based on layout
        content_texts = texts[1:] if len(texts) > 1 else texts
        
        if layout == 'hero':
            self._create_hero_content(slide, content_texts, content_style, title_config)
        elif layout == 'closing':
            self._create_closing_content(slide, content_texts, content_style)
        elif layout == 'grid':
            self._create_grid_content(slide, content_texts, content_style)
        elif layout == 'two_column':
            self._create_two_column_content(slide, content_texts, content_style)
        elif layout == 'stats':
            self._create_stats_content(slide, content_texts, content_style)
        else:  # content_cards
            self._create_cards_content(slide, content_texts, content_style)
    
    def _set_background(self, slide, color: str):
        """Set slide background"""
        if color.startswith('#'):
            fill = slide.background.fill
            fill.solid()
            fill.fore_color.rgb = hex_to_rgb(color)
    
    def _add_decoration(self, slide, deco: Dict):
        """Add decorative shape"""
        deco_type = deco.get('type', 'circle')
        position = deco.get('position', 'top-right')
        color = deco.get('color', '#00b4d8')
        size = deco.get('size', 'medium')
        
        # Size mapping
        sizes = {'small': 1.5, 'medium': 3, 'large': 5}
        s = sizes.get(size, 3)
        
        # Position mapping
        positions = {
            'top-right': (11, -1),
            'top-left': (-1, -1),
            'bottom-right': (10, 5),
            'bottom-left': (-1, 5),
            'center-right': (11, 2.5),
            'top': (0, 0),
        }
        x, y = positions.get(position, (11, -1))
        
        # Shape mapping
        shapes = {
            'circle': MSO_SHAPE.OVAL,
            'rectangle': MSO_SHAPE.RECTANGLE,
            'triangle': MSO_SHAPE.ISOSCELES_TRIANGLE,
        }
        
        if deco_type == 'line':
            if position == 'top':
                shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1))
            else:
                shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(s), Inches(0.08))
        else:
            shape_type = shapes.get(deco_type, MSO_SHAPE.OVAL)
            shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(s), Inches(s))
        
        shape.fill.solid()
        shape.fill.fore_color.rgb = hex_to_rgb(color)
        shape.line.fill.background()
    
    def _add_title(self, slide, text: str, config: Dict):
        """Add title to slide"""
        position = config.get('position', 'top-left')
        color = config.get('color', '#ffffff')
        size = config.get('size', 32)
        bold = config.get('bold', True)
        
        # Position mapping
        if position == 'center':
            x, y, w = 0.5, 2.5, 12.333
            align = PP_ALIGN.CENTER
        elif position == 'bottom':
            x, y, w = 0.5, 5.5, 12.333
            align = PP_ALIGN.CENTER
        else:  # top-left
            x, y, w = 0.8, 0.6, 11
            align = PP_ALIGN.LEFT
        
        title_box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(1.5))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text[:80]
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = hex_to_rgb(color)
        p.alignment = align
    
    def _create_hero_content(self, slide, texts: List[str], style: Dict, title_config: Dict):
        """Create hero slide content"""
        if texts:
            # Subtitle
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(10), Inches(1))
            tf = sub_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = texts[0][:100]
            p.font.size = Pt(22)
            p.font.color.rgb = hex_to_rgb(style.get('text_color', '#ffffff'))
            
            # Accent line
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.0), Inches(2), Inches(0.06))
            line.fill.solid()
            line.fill.fore_color.rgb = hex_to_rgb(style.get('accent_color', '#00b4d8'))
            line.line.fill.background()
    
    def _create_closing_content(self, slide, texts: List[str], style: Dict):
        """Create closing slide content"""
        # Tagline
        tagline = texts[0] if texts else "Questions?"
        tag_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(12.333), Inches(1))
        tf = tag_box.text_frame
        p = tf.paragraphs[0]
        p.text = tagline[:60]
        p.font.size = Pt(20)
        p.font.color.rgb = hex_to_rgb(style.get('text_color', '#ffffff'))
        p.alignment = PP_ALIGN.CENTER
        
        # Decorative line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.5), Inches(5.5), Inches(2.333), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = hex_to_rgb(style.get('accent_color', '#00b4d8'))
        line.line.fill.background()
    
    def _create_cards_content(self, slide, texts: List[str], style: Dict):
        """Create card-based content"""
        accent = style.get('accent_color', '#00b4d8')
        text_color = style.get('text_color', '#ffffff')
        card_bg = style.get('card_bg_color', '#ffffff20')
        
        items = texts[:6]
        card_height = 0.9
        start_y = 1.8
        
        for i, text in enumerate(items):
            y = start_y + i * (card_height + 0.15)
            if y > 6.3:
                break
            
            # Card
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(0.8), Inches(y),
                Inches(11.5), Inches(card_height)
            )
            # Semi-transparent card
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.fill.fore_color.brightness = 0.85
            card.line.fill.background()
            
            # Accent bar
            accent_bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0.8), Inches(y),
                Inches(0.1), Inches(card_height)
            )
            accent_bar.fill.solid()
            accent_bar.fill.fore_color.rgb = hex_to_rgb(accent)
            accent_bar.line.fill.background()
            
            # Number
            num_circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(1.1), Inches(y + 0.2),
                Inches(0.5), Inches(0.5)
            )
            num_circle.fill.solid()
            num_circle.fill.fore_color.rgb = hex_to_rgb(accent)
            num_circle.line.fill.background()
            
            num_box = slide.shapes.add_textbox(Inches(1.1), Inches(y + 0.25), Inches(0.5), Inches(0.45))
            tf = num_box.text_frame
            p = tf.paragraphs[0]
            p.text = str(i + 1)
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            
            # Text
            text_box = slide.shapes.add_textbox(Inches(1.8), Inches(y + 0.2), Inches(10), Inches(card_height - 0.4))
            tf = text_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = text[:120]
            p.font.size = Pt(14)
            p.font.color.rgb = RGBColor(30, 30, 50)
    
    def _create_grid_content(self, slide, texts: List[str], style: Dict):
        """Create grid layout for many items"""
        accent = style.get('accent_color', '#00b4d8')
        
        items = texts[:6]
        cols = 3
        rows = 2
        card_w = 3.8
        card_h = 2.3
        start_x = 0.6
        start_y = 1.8
        gap = 0.35
        
        for i, text in enumerate(items):
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + gap)
            y = start_y + row * (card_h + gap)
            
            # Card
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(x), Inches(y),
                Inches(card_w), Inches(card_h)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.fill.fore_color.brightness = 0.9
            card.line.fill.background()
            
            # Top accent
            colors = [accent, '#ff6b6b', '#ffd166', '#06d6a0', '#118ab2', '#073b4c']
            top = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x), Inches(y),
                Inches(card_w), Inches(0.1)
            )
            top.fill.solid()
            top.fill.fore_color.rgb = hex_to_rgb(colors[i % len(colors)])
            top.line.fill.background()
            
            # Number
            num = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(x + 0.2), Inches(y + 0.3),
                Inches(0.5), Inches(0.5)
            )
            num.fill.solid()
            num.fill.fore_color.rgb = hex_to_rgb(colors[i % len(colors)])
            num.line.fill.background()
            
            num_box = slide.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.35), Inches(0.5), Inches(0.45))
            tf = num_box.text_frame
            p = tf.paragraphs[0]
            p.text = str(i + 1)
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            
            # Text
            text_box = slide.shapes.add_textbox(
                Inches(x + 0.15), Inches(y + 1),
                Inches(card_w - 0.3), Inches(card_h - 1.2)
            )
            tf = text_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = text[:100]
            p.font.size = Pt(12)
            p.font.color.rgb = RGBColor(30, 30, 50)
    
    def _create_two_column_content(self, slide, texts: List[str], style: Dict):
        """Create two-column layout"""
        accent = style.get('accent_color', '#00b4d8')
        text_color = style.get('text_color', '#ffffff')
        
        mid = len(texts) // 2
        left_items = texts[:mid]
        right_items = texts[mid:]
        
        # Left column header
        left_header = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.6), Inches(1.6),
            Inches(5.8), Inches(0.5)
        )
        left_header.fill.solid()
        left_header.fill.fore_color.rgb = hex_to_rgb(accent)
        left_header.line.fill.background()
        
        # Left items
        for i, text in enumerate(left_items[:4]):
            y = 2.3 + i * 1.1
            self._add_list_item(slide, text, 0.6, y, accent)
        
        # Right column header
        right_header = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(6.9), Inches(1.6),
            Inches(5.8), Inches(0.5)
        )
        right_header.fill.solid()
        right_header.fill.fore_color.rgb = hex_to_rgb('#ff6b6b')
        right_header.line.fill.background()
        
        # Right items
        for i, text in enumerate(right_items[:4]):
            y = 2.3 + i * 1.1
            self._add_list_item(slide, text, 6.9, y, '#ff6b6b')
    
    def _create_stats_content(self, slide, texts: List[str], style: Dict):
        """Create statistics display"""
        accent = style.get('accent_color', '#00b4d8')
        
        stats = texts[:4]
        card_w = 2.8
        total_w = len(stats) * card_w + (len(stats) - 1) * 0.4
        start_x = (13.333 - total_w) / 2
        
        for i, text in enumerate(stats):
            x = start_x + i * (card_w + 0.4)
            
            # Card
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(x), Inches(2.2),
                Inches(card_w), Inches(3.5)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.line.fill.background()
            
            # Parse stat
            parts = text.split(':', 1) if ':' in text else [text[:20], text[20:50]]
            
            # Value
            val_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(2.6), Inches(card_w - 0.2), Inches(1))
            tf = val_box.text_frame
            p = tf.paragraphs[0]
            p.text = parts[0][:15]
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = hex_to_rgb(accent)
            p.alignment = PP_ALIGN.CENTER
            
            # Label
            if len(parts) > 1:
                lbl_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(3.8), Inches(card_w - 0.2), Inches(1.5))
                tf = lbl_box.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = parts[1][:50]
                p.font.size = Pt(11)
                p.font.color.rgb = RGBColor(100, 100, 100)
                p.alignment = PP_ALIGN.CENTER
    
    def _add_list_item(self, slide, text: str, x: float, y: float, accent: str):
        """Add a list item with icon"""
        # Icon
        icon = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.35), Inches(0.35))
        icon.fill.solid()
        icon.fill.fore_color.rgb = hex_to_rgb(accent)
        icon.line.fill.background()
        
        # Text
        text_box = slide.shapes.add_textbox(Inches(x + 0.5), Inches(y), Inches(5), Inches(0.9))
        tf = text_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text[:90]
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(255, 255, 255)


async def generate_ai_presentation(slides_data: List[Dict], output_path: str, api_key: str = None) -> str:
    """Convenience function to generate AI-designed presentation"""
    generator = AIPPTXGenerator(api_key)
    return await generator.generate_presentation(slides_data, output_path)
