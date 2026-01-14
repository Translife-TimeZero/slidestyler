"""
Professional PPTX Exporter
Generates high-quality PowerPoint files with proper styling
"""

import os
from typing import Dict, List, Optional
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
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


class PPTXExporter:
    """Exports redesigned slides to a professional PPTX file"""
    
    def __init__(self, style: Dict, slides_data: List[Dict]):
        self.style = style
        self.theme = style.get('theme', {})
        self.typography = style.get('typography', {})
        self.slides_data = slides_data
        
        # Create presentation with 16:9 aspect ratio
        self.prs = Presentation()
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(5.625)  # 16:9
        
    def export(self, output_path: str) -> str:
        """Export all slides to PPTX"""
        for slide_data in self.slides_data:
            self._create_slide(slide_data)
        
        self.prs.save(output_path)
        return output_path
    
    def _create_slide(self, slide_data: Dict):
        """Create a single slide based on layout type"""
        layout_type = slide_data.get('layout_type', 'content')
        original_content = slide_data.get('original_content', [])
        
        # Extract title and body
        title = ""
        subtitle = ""
        body_texts = []
        
        for item in original_content:
            item_type = item.get('type', 'body')
            text = item.get('text', '').strip()
            if not text:
                continue
                
            if item_type in ['title', 'ctrTitle', 'TITLE', 'CENTER_TITLE']:
                title = text
            elif item_type in ['subTitle', 'SUBTITLE']:
                subtitle = text
            else:
                body_texts.append(text)
        
        # Create appropriate slide type
        if layout_type == 'title':
            self._create_title_slide(title, subtitle)
        elif layout_type == 'closing':
            self._create_closing_slide(title, body_texts)
        elif layout_type == 'section_break':
            self._create_section_slide(title)
        elif layout_type == 'two_column':
            mid = len(body_texts) // 2
            self._create_two_column_slide(title, body_texts[:mid], body_texts[mid:])
        elif layout_type == 'stats':
            self._create_stats_slide(title, body_texts)
        elif layout_type in ['chart', 'image']:
            self._create_media_slide(title, body_texts, layout_type)
        else:
            self._create_content_slide(title, body_texts)
    
    def _create_title_slide(self, title: str, subtitle: str = ""):
        """Create a professional title slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank
        
        bg = self.theme.get('background', '#ffffff')
        primary = self.theme.get('primary', '#0077b6')
        
        # Set background
        if not bg.startswith('linear'):
            self._set_slide_background(slide, bg)
        
        # Determine text colors based on background
        is_dark = self._is_dark_color(bg)
        title_color = '#ffffff' if is_dark else self.theme.get('text', '#1a1a2e')
        subtitle_color = 'rgba(255,255,255,0.8)' if is_dark else self.theme.get('text_muted', '#666666')
        
        # Add accent bar
        accent_color = self.theme.get('accent', primary)
        self._add_accent_element(slide, self.style.get('layout', {}).get('accent_position', 'left-bar'))
        
        # Title
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(1.2))
            self._format_title_text(title_box, title, title_color, center=True, size=42)
        
        # Subtitle
        if subtitle:
            sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.3), Inches(9), Inches(0.6))
            self._format_body_text(sub_box, subtitle, subtitle_color if isinstance(subtitle_color, str) and '#' in subtitle_color else '#888888', center=True, size=22)
    
    def _create_content_slide(self, title: str, body_texts: List[str]):
        """Create a standard content slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # Blank
        
        bg = self.theme.get('background', '#ffffff')
        if not bg.startswith('linear'):
            self._set_slide_background(slide, bg)
        
        primary = self.theme.get('primary', '#0077b6')
        text_color = self.theme.get('text', '#1a1a2e')
        
        # Add accent element
        self._add_accent_element(slide, self.style.get('layout', {}).get('accent_position', 'left-bar'))
        
        # Title
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.8))
            self._format_title_text(title_box, title, primary, size=28)
        
        # Content area
        if body_texts:
            content_box = slide.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(8.8), Inches(3.8))
            tf = content_box.text_frame
            tf.word_wrap = True
            
            for i, text in enumerate(body_texts[:8]):
                if i == 0:
                    p = tf.paragraphs[0]
                else:
                    p = tf.add_paragraph()
                
                # Add bullet character
                p.text = f"• {text}"
                p.font.size = Pt(16)
                p.font.color.rgb = hex_to_rgb(text_color)
                p.space_after = Pt(10)
                p.line_spacing = 1.3
    
    def _create_two_column_slide(self, title: str, left_texts: List[str], right_texts: List[str]):
        """Create a two-column content slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        bg = self.theme.get('background', '#ffffff')
        if not bg.startswith('linear'):
            self._set_slide_background(slide, bg)
        
        primary = self.theme.get('primary', '#0077b6')
        text_color = self.theme.get('text', '#1a1a2e')
        border_color = self.theme.get('border', '#e5e7eb')
        
        self._add_accent_element(slide, self.style.get('layout', {}).get('accent_position', 'left-bar'))
        
        # Title
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.8))
            self._format_title_text(title_box, title, primary, size=28)
        
        # Left column
        left_box = slide.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(4.2), Inches(3.8))
        self._add_bullet_list(left_box, left_texts, text_color)
        
        # Divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.95), Inches(1.4), Inches(0.02), Inches(3.5))
        line.fill.solid()
        line.fill.fore_color.rgb = hex_to_rgb(border_color)
        line.line.fill.background()
        
        # Right column
        right_box = slide.shapes.add_textbox(Inches(5.2), Inches(1.4), Inches(4.2), Inches(3.8))
        self._add_bullet_list(right_box, right_texts, text_color)
    
    def _create_closing_slide(self, title: str, body_texts: List[str]):
        """Create a closing/thank you slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        primary = self.theme.get('primary', '#0077b6')
        self._set_slide_background(slide, primary)
        
        # Title in white
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(9), Inches(1.2))
            self._format_title_text(title_box, title, '#ffffff', center=True, size=48)
        
        # Contact info
        if body_texts:
            info_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.4), Inches(9), Inches(0.6))
            self._format_body_text(info_box, body_texts[0], '#ffffff', center=True, size=18, opacity=0.9)
    
    def _create_section_slide(self, title: str):
        """Create a section break slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        bg = self.theme.get('background', '#ffffff')
        if not bg.startswith('linear'):
            self._set_slide_background(slide, bg)
        
        primary = self.theme.get('primary', '#0077b6')
        accent = self.theme.get('accent', primary)
        
        # Title centered
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.2), Inches(9), Inches(1))
            self._format_title_text(title_box, title, primary, center=True, size=42)
        
        # Decorative line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.4), Inches(3.5), Inches(1.2), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = hex_to_rgb(accent)
        line.line.fill.background()
    
    def _create_stats_slide(self, title: str, body_texts: List[str]):
        """Create a statistics showcase slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        bg = self.theme.get('background', '#ffffff')
        if not bg.startswith('linear'):
            self._set_slide_background(slide, bg)
        
        primary = self.theme.get('primary', '#0077b6')
        text_color = self.theme.get('text', '#1a1a2e')
        surface = self.theme.get('surface', '#f5f5f5')
        
        self._add_accent_element(slide, self.style.get('layout', {}).get('accent_position', 'left-bar'))
        
        # Title
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.8))
            self._format_title_text(title_box, title, primary, size=28)
        
        # Stats as cards
        stats = body_texts[:4]
        if stats:
            card_width = 2.0
            total_width = len(stats) * card_width + (len(stats) - 1) * 0.3
            start_x = (10 - total_width) / 2
            
            for i, stat_text in enumerate(stats):
                x = start_x + i * (card_width + 0.3)
                
                # Card background
                card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2), Inches(card_width), Inches(2.2))
                card.fill.solid()
                card.fill.fore_color.rgb = hex_to_rgb(surface)
                card.line.fill.background()
                
                # Stat text
                stat_box = slide.shapes.add_textbox(Inches(x + 0.1), Inches(2.3), Inches(card_width - 0.2), Inches(1.6))
                tf = stat_box.text_frame
                tf.word_wrap = True
                
                # Try to parse as value:label
                parts = stat_text.split(':', 1) if ':' in stat_text else stat_text.split('-', 1) if '-' in stat_text else [stat_text, '']
                value = parts[0].strip()
                label = parts[1].strip() if len(parts) > 1 else ''
                
                p = tf.paragraphs[0]
                p.text = value
                p.font.size = Pt(32)
                p.font.bold = True
                p.font.color.rgb = hex_to_rgb(primary)
                p.alignment = PP_ALIGN.CENTER
                
                if label:
                    p2 = tf.add_paragraph()
                    p2.text = label
                    p2.font.size = Pt(11)
                    p2.font.color.rgb = hex_to_rgb(self.theme.get('text_muted', '#666666'))
                    p2.alignment = PP_ALIGN.CENTER
    
    def _create_media_slide(self, title: str, body_texts: List[str], media_type: str):
        """Create a slide with media placeholder (chart or image)"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        
        bg = self.theme.get('background', '#ffffff')
        if not bg.startswith('linear'):
            self._set_slide_background(slide, bg)
        
        primary = self.theme.get('primary', '#0077b6')
        text_color = self.theme.get('text', '#1a1a2e')
        surface = self.theme.get('surface', '#f5f5f5')
        
        self._add_accent_element(slide, self.style.get('layout', {}).get('accent_position', 'left-bar'))
        
        # Title
        if title:
            title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(8.8), Inches(0.8))
            self._format_title_text(title_box, title, primary, size=28)
        
        # Content on left
        if body_texts:
            content_box = slide.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(3.5), Inches(3.8))
            self._add_bullet_list(content_box, body_texts[:5], text_color, size=14)
        
        # Media placeholder on right
        placeholder = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.5), Inches(1.4), Inches(5), Inches(3.6))
        placeholder.fill.solid()
        placeholder.fill.fore_color.rgb = hex_to_rgb(surface)
        placeholder.line.fill.background()
        
        # Placeholder icon text
        icon_box = slide.shapes.add_textbox(Inches(4.5), Inches(2.8), Inches(5), Inches(0.6))
        tf = icon_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"[{media_type.upper()} PLACEHOLDER]"
        p.font.size = Pt(12)
        p.font.color.rgb = hex_to_rgb(self.theme.get('text_muted', '#888888'))
        p.alignment = PP_ALIGN.CENTER
    
    def _set_slide_background(self, slide, color: str):
        """Set slide background color"""
        if color.startswith('#'):
            background = slide.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = hex_to_rgb(color)
    
    def _add_accent_element(self, slide, accent_type: str):
        """Add decorative accent element to slide"""
        accent_color = self.theme.get('accent', self.theme.get('primary', '#0077b6'))
        
        if accent_type == 'left-bar':
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.08), Inches(5.625))
            shape.fill.solid()
            shape.fill.fore_color.rgb = hex_to_rgb(accent_color)
            shape.line.fill.background()
        
        elif accent_type == 'top-bar':
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(0.06))
            shape.fill.solid()
            shape.fill.fore_color.rgb = hex_to_rgb(accent_color)
            shape.line.fill.background()
        
        elif accent_type == 'bottom-bar' or accent_type == 'bottom-line':
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(5.3), Inches(9), Inches(0.04))
            shape.fill.solid()
            shape.fill.fore_color.rgb = hex_to_rgb(accent_color)
            shape.line.fill.background()
    
    def _format_title_text(self, textbox, text: str, color: str, center: bool = False, size: int = 32):
        """Format title text"""
        tf = textbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(size)
        p.font.bold = True
        p.font.color.rgb = hex_to_rgb(color)
        if center:
            p.alignment = PP_ALIGN.CENTER
    
    def _format_body_text(self, textbox, text: str, color: str, center: bool = False, size: int = 16, opacity: float = 1.0):
        """Format body text"""
        tf = textbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(size)
        p.font.color.rgb = hex_to_rgb(color)
        if center:
            p.alignment = PP_ALIGN.CENTER
    
    def _add_bullet_list(self, textbox, items: List[str], color: str, size: int = 16):
        """Add bullet list to textbox"""
        tf = textbox.text_frame
        tf.word_wrap = True
        
        for i, text in enumerate(items[:8]):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            
            p.text = f"• {text}"
            p.font.size = Pt(size)
            p.font.color.rgb = hex_to_rgb(color)
            p.space_after = Pt(8)
            p.line_spacing = 1.3
    
    def _is_dark_color(self, color: str) -> bool:
        """Check if a color is dark"""
        if color.startswith('linear'):
            return 'dark' in color.lower() or '#0' in color or '#1' in color or '#2' in color
        if color.startswith('#'):
            hex_color = color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                return luminance < 0.5
        return False


def export_presentation(style: Dict, slides_data: List[Dict], output_path: str) -> str:
    """Convenience function to export a presentation"""
    exporter = PPTXExporter(style, slides_data)
    return exporter.export(output_path)
