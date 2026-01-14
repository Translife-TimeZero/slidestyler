"""
AI-Powered PPTX Generator with Proper Layer Separation
Background, Images, and Text are completely separate and editable
"""

import os
import io
import json
import httpx
import asyncio
import tempfile
from typing import Dict, List, Optional, Tuple
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn


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


class AIPPTXGenerator:
    """
    AI-powered PPTX generator with proper layer separation:
    - Layer 1: Slide Background (solid color or gradient)
    - Layer 2: Images (AI-generated or decorative shapes)
    - Layer 3: Text elements (titles, content, labels)
    
    Each layer is completely independent and editable in PowerPoint.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("REPLICATE_API_TOKEN")
        self.llm_url = "https://api.replicate.com/v1/models/meta/meta-llama-3-70b-instruct/predictions"
        self.image_url = "https://api.replicate.com/v1/models/bytedance/seedream-3.0/predictions"
        self.presentation_context = ""
        
    async def generate_presentation(
        self, 
        slides_data: List[Dict],
        output_path: str,
        generate_images: bool = True
    ) -> str:
        """Generate presentation with properly separated layers"""
        
        # Create widescreen presentation
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        
        # Build context
        all_content = []
        for slide in slides_data:
            texts = self._extract_texts(slide.get('original_content', []))
            all_content.extend(texts[:3])
        self.presentation_context = " | ".join(all_content[:10])[:500]
        
        # Generate each slide with separated layers
        total = len(slides_data)
        for i, slide_data in enumerate(slides_data):
            print(f"[AI Generator] Creating slide {i+1}/{total} with layer separation...")
            
            # Get design config
            design = await self._get_design_config(slide_data, i, total)
            
            # Generate image if requested
            image_path = None
            if generate_images and design.get('image_prompt'):
                image_path = await self._generate_image(design.get('image_prompt'), i)
            
            # Create slide with SEPARATED LAYERS
            self._create_layered_slide(prs, slide_data, design, image_path, i, total)
        
        prs.save(output_path)
        return output_path
    
    def _extract_texts(self, original_content: List) -> List[str]:
        """Extract clean text items"""
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
    
    async def _get_design_config(self, slide_data: Dict, index: int, total: int) -> Dict:
        """Get design configuration for the slide"""
        texts = self._extract_texts(slide_data.get('original_content', []))
        
        # Smart defaults based on position and content
        is_first = index == 0
        is_last = index == total - 1
        content_count = len(texts)
        
        # Color schemes (dark backgrounds for professional look)
        schemes = [
            {"bg": "#0f172a", "accent": "#3b82f6", "accent2": "#22d3ee", "text": "#ffffff"},
            {"bg": "#1e1b4b", "accent": "#8b5cf6", "accent2": "#f472b6", "text": "#ffffff"},
            {"bg": "#14532d", "accent": "#22c55e", "accent2": "#a3e635", "text": "#ffffff"},
            {"bg": "#7c2d12", "accent": "#f97316", "accent2": "#fbbf24", "text": "#ffffff"},
            {"bg": "#1e3a5f", "accent": "#0ea5e9", "accent2": "#2dd4bf", "text": "#ffffff"},
        ]
        scheme = schemes[index % len(schemes)]
        
        # Determine layout and image needs
        if is_first:
            return {
                "layout": "hero",
                "background": {"color": scheme["bg"], "type": "solid"},
                "image": {
                    "enabled": True,
                    "position": "right",  # Image on right, text on left
                    "width": 6,
                    "height": 7.5,
                    "x": 7.333,
                    "y": 0
                },
                "image_prompt": self._generate_image_prompt(texts, "hero"),
                "text": {
                    "title": texts[0][:50] if texts else "Presentation",
                    "subtitle": texts[1][:80] if len(texts) > 1 else "",
                    "position": "left",
                    "title_size": 48,
                    "title_x": 0.8,
                    "title_y": 2.5,
                    "title_width": 6
                },
                "colors": scheme,
                "decorations": [
                    {"type": "accent_line", "x": 0.8, "y": 4.0, "w": 2, "h": 0.06}
                ]
            }
        elif is_last:
            return {
                "layout": "closing",
                "background": {"color": scheme["bg"], "type": "solid"},
                "image": {
                    "enabled": True,
                    "position": "background_accent",
                    "width": 5,
                    "height": 5,
                    "x": 9,
                    "y": 3
                },
                "image_prompt": self._generate_image_prompt(texts, "closing"),
                "text": {
                    "title": "Thank You",
                    "subtitle": texts[0][:60] if texts else "Questions?",
                    "position": "center",
                    "title_size": 54,
                    "title_x": 0.5,
                    "title_y": 2.8,
                    "title_width": 12.333
                },
                "colors": scheme,
                "decorations": [
                    {"type": "circle", "x": -1, "y": -1, "size": 4},
                    {"type": "accent_line", "x": 5.5, "y": 5.2, "w": 2.333, "h": 0.06}
                ]
            }
        elif content_count > 6:
            return {
                "layout": "grid",
                "background": {"color": scheme["bg"], "type": "solid"},
                "image": {
                    "enabled": True,
                    "position": "corner",
                    "width": 3.5,
                    "height": 3,
                    "x": 9.5,
                    "y": 0
                },
                "image_prompt": self._generate_image_prompt(texts, "accent"),
                "text": {
                    "title": texts[0][:45] if texts else "",
                    "content": texts[1:7],
                    "position": "full",
                    "title_size": 32,
                    "title_x": 0.6,
                    "title_y": 0.5,
                    "title_width": 8
                },
                "colors": scheme,
                "decorations": [
                    {"type": "top_bar", "h": 0.08}
                ]
            }
        else:
            return {
                "layout": "split",
                "background": {"color": scheme["bg"], "type": "solid"},
                "image": {
                    "enabled": True,
                    "position": "right_panel",
                    "width": 5.5,
                    "height": 7.5,
                    "x": 7.833,
                    "y": 0
                },
                "image_prompt": self._generate_image_prompt(texts, "content"),
                "text": {
                    "title": texts[0][:45] if texts else "",
                    "content": texts[1:6],
                    "position": "left",
                    "title_size": 32,
                    "title_x": 0.6,
                    "title_y": 0.6,
                    "title_width": 6.5
                },
                "colors": scheme,
                "decorations": [
                    {"type": "left_bar", "w": 0.12},
                    {"type": "top_bar", "h": 0.08}
                ]
            }
    
    def _generate_image_prompt(self, texts: List[str], style: str) -> str:
        """Generate contextual image prompt"""
        content = " ".join(texts[:3]).lower()
        
        base_prompts = {
            "hero": "dramatic abstract composition, professional, cinematic lighting, ",
            "closing": "uplifting abstract shapes, celebration of achievement, ",
            "accent": "subtle geometric pattern, corner accent, ",
            "content": "abstract professional background, vertical composition, "
        }
        
        # Content-aware additions
        keywords = {
            "learn": "flowing knowledge streams, education concept",
            "error": "problem-solving visualization, correction arrows",
            "process": "interconnected nodes, workflow diagram style",
            "leader": "ascending peaks, growth trajectory",
            "team": "collaborative circles, unity shapes",
            "change": "transformation morphing shapes",
            "analy": "data visualization abstract, chart elements"
        }
        
        base = base_prompts.get(style, base_prompts["content"])
        addition = "modern corporate aesthetic"
        
        for key, prompt in keywords.items():
            if key in content:
                addition = prompt
                break
        
        return f"{base}{addition}, no text, high quality, 4k"
    
    async def _generate_image(self, prompt: str, slide_index: int) -> Optional[str]:
        """Generate image using Seedream-3"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.image_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "input": {
                            "prompt": prompt,
                            "num_outputs": 1,
                            "aspect_ratio": "16:9",
                            "output_format": "png"
                        }
                    }
                )
                
                if response.status_code != 201:
                    print(f"[Image Gen] API error: {response.status_code}")
                    return None
                
                result = response.json()
                prediction_url = result.get('urls', {}).get('get')
                
                for _ in range(60):
                    await asyncio.sleep(2)
                    poll = await client.get(
                        prediction_url,
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    poll_result = poll.json()
                    
                    if poll_result.get('status') == 'succeeded':
                        output = poll_result.get('output')
                        if output:
                            image_url = output[0] if isinstance(output, list) else output
                            img_response = await client.get(image_url)
                            if img_response.status_code == 200:
                                temp_path = tempfile.mktemp(suffix='.png')
                                with open(temp_path, 'wb') as f:
                                    f.write(img_response.content)
                                print(f"[Image Gen] Created image for slide {slide_index + 1}")
                                return temp_path
                    elif poll_result.get('status') == 'failed':
                        return None
                
                return None
                
        except Exception as e:
            print(f"[Image Gen] Error: {e}")
            return None
    
    def _create_layered_slide(
        self, 
        prs: Presentation, 
        slide_data: Dict, 
        design: Dict, 
        image_path: Optional[str],
        index: int,
        total: int
    ):
        """
        Create slide with properly separated layers:
        1. BACKGROUND LAYER - Slide background fill
        2. IMAGE LAYER - Pictures and decorative shapes
        3. TEXT LAYER - All text elements on top
        """
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        texts = self._extract_texts(slide_data.get('original_content', []))
        colors = design.get('colors', {})
        
        # ============================================
        # LAYER 1: BACKGROUND (Slide background fill)
        # ============================================
        bg_config = design.get('background', {})
        bg_color = bg_config.get('color', '#1e3a5f')
        
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = hex_to_rgb(bg_color)
        
        print(f"  [Layer 1] Background: {bg_color}")
        
        # ============================================
        # LAYER 2: IMAGES AND DECORATIVE SHAPES
        # ============================================
        image_config = design.get('image', {})
        
        # Add AI-generated image if available
        if image_path and os.path.exists(image_path) and image_config.get('enabled'):
            img_x = image_config.get('x', 7)
            img_y = image_config.get('y', 0)
            img_w = image_config.get('width', 6)
            img_h = image_config.get('height', 7.5)
            
            slide.shapes.add_picture(
                image_path,
                Inches(img_x), Inches(img_y),
                width=Inches(img_w), height=Inches(img_h)
            )
            print(f"  [Layer 2] Image: {img_w}x{img_h} at ({img_x}, {img_y})")
        else:
            # Add decorative shapes as image replacement
            self._add_decorative_shapes(slide, design, colors)
            print(f"  [Layer 2] Decorative shapes (no image)")
        
        # Add decoration elements (accent bars, circles)
        for deco in design.get('decorations', []):
            self._add_decoration(slide, deco, colors)
        
        # ============================================
        # LAYER 3: TEXT ELEMENTS (Always on top)
        # ============================================
        text_config = design.get('text', {})
        layout = design.get('layout', 'split')
        
        # Title (separate text box)
        title = text_config.get('title', '')
        if title:
            self._add_title_text(slide, title, text_config, colors)
            print(f"  [Layer 3] Title: '{title[:30]}...'")
        
        # Subtitle or content
        if layout in ['hero', 'closing']:
            subtitle = text_config.get('subtitle', '')
            if subtitle:
                self._add_subtitle_text(slide, subtitle, text_config, colors)
                print(f"  [Layer 3] Subtitle: '{subtitle[:30]}...'")
        else:
            content = text_config.get('content', texts[1:6])
            if content:
                self._add_content_cards(slide, content, text_config, colors, layout)
                print(f"  [Layer 3] Content: {len(content)} items")
    
    def _add_decorative_shapes(self, slide, design: Dict, colors: Dict):
        """Add decorative shapes as image layer replacement"""
        layout = design.get('layout', 'split')
        accent = colors.get('accent', '#3b82f6')
        accent2 = colors.get('accent2', '#22d3ee')
        
        if layout == 'hero':
            # Large accent circle (right side)
            circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(8), Inches(-1),
                Inches(7), Inches(7)
            )
            circle.fill.solid()
            circle.fill.fore_color.rgb = hex_to_rgb(accent)
            circle.fill.fore_color.brightness = 0.3
            circle.line.fill.background()
            
            # Smaller accent
            circle2 = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(10), Inches(5),
                Inches(4), Inches(4)
            )
            circle2.fill.solid()
            circle2.fill.fore_color.rgb = hex_to_rgb(accent2)
            circle2.fill.fore_color.brightness = 0.2
            circle2.line.fill.background()
            
        elif layout == 'closing':
            # Large background accent
            circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(9), Inches(3),
                Inches(6), Inches(6)
            )
            circle.fill.solid()
            circle.fill.fore_color.rgb = hex_to_rgb(accent)
            circle.fill.fore_color.brightness = 0.25
            circle.line.fill.background()
            
        elif layout == 'split':
            # Right panel decoration
            panel = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(7.833), Inches(0),
                Inches(5.5), Inches(7.5)
            )
            panel.fill.solid()
            panel.fill.fore_color.rgb = hex_to_rgb(accent)
            panel.fill.fore_color.brightness = 0.4
            panel.line.fill.background()
            
            # Decorative circles on panel
            for x, y, s in [(9, 1.5, 2), (11, 4, 1.5), (8.5, 5.5, 1)]:
                c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(s), Inches(s))
                c.fill.solid()
                c.fill.fore_color.rgb = RGBColor(255, 255, 255)
                c.fill.fore_color.brightness = 0.75
                c.line.fill.background()
                
        elif layout == 'grid':
            # Corner accent
            corner = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(10), Inches(-1),
                Inches(4.5), Inches(4)
            )
            corner.fill.solid()
            corner.fill.fore_color.rgb = hex_to_rgb(accent)
            corner.fill.fore_color.brightness = 0.35
            corner.line.fill.background()
    
    def _add_decoration(self, slide, deco: Dict, colors: Dict):
        """Add accent decorations"""
        deco_type = deco.get('type', '')
        accent = colors.get('accent', '#3b82f6')
        
        if deco_type == 'top_bar':
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0), Inches(0),
                Inches(13.333), Inches(deco.get('h', 0.08))
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = hex_to_rgb(accent)
            bar.line.fill.background()
            
        elif deco_type == 'left_bar':
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0), Inches(0),
                Inches(deco.get('w', 0.12)), Inches(7.5)
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = hex_to_rgb(accent)
            bar.line.fill.background()
            
        elif deco_type == 'accent_line':
            line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(deco.get('x', 0)), Inches(deco.get('y', 0)),
                Inches(deco.get('w', 2)), Inches(deco.get('h', 0.06))
            )
            line.fill.solid()
            line.fill.fore_color.rgb = hex_to_rgb(accent)
            line.line.fill.background()
            
        elif deco_type == 'circle':
            circle = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(deco.get('x', 0)), Inches(deco.get('y', 0)),
                Inches(deco.get('size', 3)), Inches(deco.get('size', 3))
            )
            circle.fill.solid()
            circle.fill.fore_color.rgb = hex_to_rgb(colors.get('accent2', accent))
            circle.fill.fore_color.brightness = 0.2
            circle.line.fill.background()
    
    def _add_title_text(self, slide, title: str, config: Dict, colors: Dict):
        """Add title as separate text layer"""
        x = config.get('title_x', 0.8)
        y = config.get('title_y', 2.5)
        w = config.get('title_width', 10)
        size = config.get('title_size', 42)
        position = config.get('position', 'left')
        
        title_box = slide.shapes.add_textbox(
            Inches(x), Inches(y),
            Inches(w), Inches(1.5)
        )
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(size)
        p.font.bold = True
        p.font.color.rgb = hex_to_rgb(colors.get('text', '#ffffff'))
        
        if position == 'center':
            p.alignment = PP_ALIGN.CENTER
    
    def _add_subtitle_text(self, slide, subtitle: str, config: Dict, colors: Dict):
        """Add subtitle as separate text layer"""
        x = config.get('title_x', 0.8)
        y = config.get('title_y', 2.5) + 1.5
        w = config.get('title_width', 10)
        position = config.get('position', 'left')
        
        sub_box = slide.shapes.add_textbox(
            Inches(x), Inches(y),
            Inches(w), Inches(1)
        )
        tf = sub_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(20)
        p.font.color.rgb = hex_to_rgb(colors.get('text', '#ffffff'))
        
        if position == 'center':
            p.alignment = PP_ALIGN.CENTER
    
    def _add_content_cards(self, slide, items: List[str], config: Dict, colors: Dict, layout: str):
        """Add content items as separate text elements with card styling"""
        accent = colors.get('accent', '#3b82f6')
        text_color = colors.get('text', '#ffffff')
        
        if layout == 'grid':
            self._add_grid_cards(slide, items, colors)
        else:
            self._add_list_cards(slide, items, config, colors)
    
    def _add_list_cards(self, slide, items: List[str], config: Dict, colors: Dict):
        """Add items as vertical card list"""
        accent = colors.get('accent', '#3b82f6')
        x = config.get('title_x', 0.6)
        start_y = config.get('title_y', 0.6) + 1.2
        w = config.get('title_width', 6.5)
        
        card_h = 0.85
        gap = 0.12
        
        for i, text in enumerate(items[:6]):
            y = start_y + i * (card_h + gap)
            if y > 6.2:
                break
            
            # Card background (IMAGE LAYER)
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(x), Inches(y),
                Inches(w), Inches(card_h)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.fill.fore_color.brightness = 0.85
            card.line.fill.background()
            
            # Accent bar (IMAGE LAYER)
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x), Inches(y),
                Inches(0.08), Inches(card_h)
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = hex_to_rgb(accent)
            bar.line.fill.background()
            
            # Number badge (IMAGE LAYER)
            badge = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(x + 0.2), Inches(y + 0.17),
                Inches(0.5), Inches(0.5)
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = hex_to_rgb(accent)
            badge.line.fill.background()
            
            # Number text (TEXT LAYER)
            num_box = slide.shapes.add_textbox(
                Inches(x + 0.2), Inches(y + 0.21),
                Inches(0.5), Inches(0.45)
            )
            tf = num_box.text_frame
            p = tf.paragraphs[0]
            p.text = str(i + 1)
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            
            # Content text (TEXT LAYER - separate from card)
            text_box = slide.shapes.add_textbox(
                Inches(x + 0.85), Inches(y + 0.17),
                Inches(w - 1.1), Inches(card_h - 0.34)
            )
            tf = text_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = text[:110]
            p.font.size = Pt(13)
            p.font.color.rgb = RGBColor(30, 30, 50)
    
    def _add_grid_cards(self, slide, items: List[str], colors: Dict):
        """Add items as grid of cards"""
        accent = colors.get('accent', '#3b82f6')
        accent_colors = [accent, '#f472b6', '#fbbf24', '#22c55e', '#0ea5e9', '#a855f7']
        
        cols = 3
        card_w = 3.8
        card_h = 2.2
        start_x = 0.5
        start_y = 1.5
        gap = 0.3
        
        for i, text in enumerate(items[:6]):
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + gap)
            y = start_y + row * (card_h + gap)
            
            color = accent_colors[i % len(accent_colors)]
            
            # Card background (IMAGE LAYER)
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(x), Inches(y),
                Inches(card_w), Inches(card_h)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.fill.fore_color.brightness = 0.9
            card.line.fill.background()
            
            # Top accent bar (IMAGE LAYER)
            top = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x), Inches(y),
                Inches(card_w), Inches(0.1)
            )
            top.fill.solid()
            top.fill.fore_color.rgb = hex_to_rgb(color)
            top.line.fill.background()
            
            # Number badge (IMAGE LAYER)
            badge = slide.shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(x + 0.2), Inches(y + 0.3),
                Inches(0.5), Inches(0.5)
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = hex_to_rgb(color)
            badge.line.fill.background()
            
            # Number text (TEXT LAYER)
            num_box = slide.shapes.add_textbox(
                Inches(x + 0.2), Inches(y + 0.34),
                Inches(0.5), Inches(0.45)
            )
            tf = num_box.text_frame
            p = tf.paragraphs[0]
            p.text = str(i + 1)
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = PP_ALIGN.CENTER
            
            # Content text (TEXT LAYER - separate)
            text_box = slide.shapes.add_textbox(
                Inches(x + 0.15), Inches(y + 0.95),
                Inches(card_w - 0.3), Inches(card_h - 1.1)
            )
            tf = text_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = text[:90]
            p.font.size = Pt(12)
            p.font.color.rgb = RGBColor(30, 30, 50)


async def generate_ai_presentation(
    slides_data: List[Dict], 
    output_path: str, 
    api_key: str = None,
    generate_images: bool = True
) -> str:
    """Generate AI-designed presentation with separated layers"""
    generator = AIPPTXGenerator(api_key)
    return await generator.generate_presentation(slides_data, output_path, generate_images)
