"""
Redesign Engine - World-Class PowerPoint Designer
Generates stunning, professional slides from content and style specifications
with AI-powered per-slide design instructions.
"""

import os
import json
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path


class SlideDesigner:
    """Generates professional HTML slides optimized for PPTX conversion"""

    def __init__(self, style: Dict, ai_instructions: Optional[Dict] = None):
        self.style = style
        self.theme = style.get("theme", {})
        self.typography = style.get("typography", {})
        self.layout_config = style.get("layout", {})
        self.effects = style.get("effects", {})
        self.ai_instructions = ai_instructions  # Per-slide AI guidance
        self.visual_concept = ai_instructions.get("visual_concept", {}) if ai_instructions else {}

    def _get_base_css(self) -> str:
        """Generate comprehensive base CSS for all slides"""
        theme = self.theme
        typo = self.typography
        
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: {typo.get('body_font', 'Inter, Arial')}, -apple-system, BlinkMacSystemFont, sans-serif;
            color: {theme.get('text', '#1a1a2e')};
            line-height: 1.5;
            overflow: hidden;
        }}
        h1, h2, h3 {{
            font-family: {typo.get('heading_font', 'Inter, Arial')}, -apple-system, sans-serif;
            font-weight: {typo.get('heading_weight', '600')};
            letter-spacing: {typo.get('letter_spacing', '0.5px')};
            line-height: 1.2;
        }}
        .slide {{
            width: 960px;
            height: 540px;
            position: relative;
            overflow: hidden;
        }}
        .col {{ display: flex; flex-direction: column; }}
        .row {{ display: flex; flex-direction: row; }}
        .center {{ align-items: center; justify-content: center; }}
        .fill {{ flex: 1; }}
        .gap-sm {{ gap: 8px; }}
        .gap-md {{ gap: 16px; }}
        .gap-lg {{ gap: 24px; }}
        
        /* AI-Optimized Typography */
        .title-xl {{ font-size: 52px; font-weight: 700; }}
        .title-lg {{ font-size: 44px; font-weight: 700; }}
        .title-md {{ font-size: 36px; font-weight: 600; }}
        .title-sm {{ font-size: 28px; font-weight: 600; }}
        
        .body-lg {{ font-size: 20px; line-height: 1.6; }}
        .body-md {{ font-size: 17px; line-height: 1.6; }}
        .body-sm {{ font-size: 15px; line-height: 1.5; }}
        
        /* Bullet styling */
        ul {{
            list-style: none;
            padding: 0;
        }}
        ul li {{
            position: relative;
            padding-left: 28px;
            margin-bottom: 14px;
        }}
        ul li::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 10px;
            width: 8px;
            height: 8px;
            background: {theme.get('accent', theme.get('primary', '#0077b6'))};
            border-radius: 50%;
        }}
        
        /* Accent elements */
        .accent-bar {{
            position: absolute;
            background: {theme.get('accent', theme.get('primary', '#0077b6'))};
        }}
        .accent-bar-left {{ left: 0; top: 0; width: 6px; height: 100%; }}
        .accent-bar-top {{ left: 0; top: 0; width: 100%; height: 5px; }}
        .accent-bar-bottom {{ left: 48px; right: 48px; bottom: 28px; height: 3px; border-radius: 2px; }}
        
        /* Cards & containers */
        .card {{
            background: {theme.get('surface', '#ffffff')};
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        }}
        
        /* Stats styling */
        .stat-value {{
            font-size: 56px;
            font-weight: 800;
            color: {theme.get('primary', '#0077b6')};
            line-height: 1;
        }}
        .stat-label {{
            font-size: 13px;
            color: {theme.get('text_muted', '#666666')};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 8px;
        }}
        
        /* Emphasis styles */
        .emphasis {{
            color: {theme.get('primary', '#0077b6')};
            font-weight: 600;
        }}
        .highlight {{
            background: linear-gradient(120deg, {theme.get('accent', '#0077b6')}20, {theme.get('accent', '#0077b6')}20);
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        /* Quote styling */
        .quote-block {{
            border-left: 4px solid {theme.get('accent', '#0077b6')};
            padding: 16px 24px;
            background: rgba(0,0,0,0.02);
            border-radius: 0 12px 12px 0;
            font-style: italic;
        }}
        """

    def _get_background_style(self, ai_slide_instructions: Optional[Dict] = None) -> str:
        """Generate background style, considering AI instructions"""
        bg = self.theme.get('background', '#ffffff')
        
        if ai_slide_instructions:
            color_app = ai_slide_instructions.get('color_application', {})
            bg_type = color_app.get('background', 'solid')
            
            if bg_type == 'gradient':
                primary = self.theme.get('primary', '#0077b6')
                return f"background: linear-gradient(135deg, {bg} 0%, {primary}15 100%);"
            elif bg_type == 'accent_block':
                return f"background-color: {self.theme.get('primary', '#0077b6')};"
        
        if 'gradient' in str(bg).lower() or 'linear' in str(bg).lower():
            return f"background: {bg};"
        return f"background-color: {bg};"

    def _get_accent_element(self, ai_slide_instructions: Optional[Dict] = None) -> str:
        """Generate accent elements based on AI instructions or style config"""
        
        # Check AI instructions first
        if ai_slide_instructions:
            visual_elements = ai_slide_instructions.get('visual_elements', {})
            accent_bar = visual_elements.get('accent_bar', 'none')
            
            if accent_bar == 'left':
                return '<div class="accent-bar accent-bar-left"></div>'
            elif accent_bar == 'top':
                return '<div class="accent-bar accent-bar-top"></div>'
            elif accent_bar == 'bottom':
                return '<div class="accent-bar accent-bar-bottom"></div>'
        
        # Fallback to style config
        accent_position = self.layout_config.get("accent_position", "left-bar")
        accent = self.theme.get("accent", self.theme.get("primary", "#0077b6"))
        primary = self.theme.get("primary", "#0077b6")

        elements = {
            "left-bar": '<div class="accent-bar accent-bar-left"></div>',
            "top-bar": '<div class="accent-bar accent-bar-top"></div>',
            "bottom-bar": '<div class="accent-bar accent-bar-bottom"></div>',
            "bottom-line": '<div class="accent-bar accent-bar-bottom"></div>',
            "corner-shapes": f'''
                <div style="position:absolute;right:-60px;top:-60px;width:200px;height:200px;background:{accent};opacity:0.12;border-radius:50%;"></div>
                <div style="position:absolute;left:-40px;bottom:-40px;width:120px;height:120px;background:{primary};opacity:0.08;border-radius:50%;"></div>
            ''',
            "diagonal": f'<div style="position:absolute;right:-150px;top:-100px;width:400px;height:300px;background:{accent};opacity:0.06;transform:rotate(45deg);"></div>',
            "none": ""
        }
        
        return elements.get(accent_position, elements["left-bar"])

    def _get_title_style(self, ai_slide_instructions: Optional[Dict] = None) -> Dict[str, str]:
        """Get title styling based on AI instructions"""
        typo_inst = ai_slide_instructions.get('typography', {}) if ai_slide_instructions else {}
        
        size_map = {
            'large': self.typography.get('title_size', '48px'),
            'medium': '36px',
            'small': '28px'
        }
        
        weight_map = {
            'bold': '700',
            'semibold': '600',
            'normal': '500'
        }
        
        color_map = {
            'primary': self.theme.get('primary', '#0077b6'),
            'text': self.theme.get('text', '#1a1a2e'),
            'accent': self.theme.get('accent', '#00b4d8')
        }
        
        return {
            'size': size_map.get(typo_inst.get('title_size', 'medium'), '36px'),
            'weight': weight_map.get(typo_inst.get('title_weight', 'bold'), '700'),
            'color': color_map.get(typo_inst.get('title_color', 'primary'), self.theme.get('primary', '#0077b6'))
        }

    def _get_spacing_style(self, ai_slide_instructions: Optional[Dict] = None) -> Dict[str, str]:
        """Get spacing values based on AI instructions"""
        spacing_inst = ai_slide_instructions.get('spacing', {}) if ai_slide_instructions else {}
        
        density = spacing_inst.get('content_density', 'balanced')
        padding = spacing_inst.get('padding_style', 'generous')
        
        padding_map = {
            'generous': {'h': '56px', 'v': '44px'},
            'standard': {'h': '48px', 'v': '36px'},
            'tight': {'h': '36px', 'v': '28px'}
        }
        
        gap_map = {
            'sparse': '24px',
            'balanced': '16px',
            'dense': '10px'
        }
        
        return {
            'padding': padding_map.get(padding, padding_map['generous']),
            'gap': gap_map.get(density, '16px')
        }

    def generate_slide_html(
        self, 
        slide_data: Dict,
        slide_index: int,
        ai_slide_instructions: Optional[Dict] = None
    ) -> str:
        """Generate HTML for any slide type using AI instructions"""
        
        # Determine layout from AI or content analysis
        layout_type = "content"
        if ai_slide_instructions:
            layout = ai_slide_instructions.get('layout', {})
            layout_type = layout.get('type', 'content')
        else:
            layout_type = slide_data.get('layout_type', 'content')
        
        # Extract content
        text_content = slide_data.get("text_content", [])
        title = ""
        subtitle = ""
        body_items = []
        
        for item in text_content:
            item_type = item.get("type", "body")
            text = item.get("text", "").strip()
            if not text:
                continue
            if item_type in ["title", "ctrTitle", "TITLE", "CENTER_TITLE"]:
                title = text
            elif item_type in ["subTitle", "SUBTITLE"]:
                subtitle = text
            else:
                body_items.append({"type": "bullet", "text": text})
        
        # Route to appropriate generator
        generators = {
            'title': self._generate_title_slide,
            'content': self._generate_content_slide,
            'two_column': self._generate_two_column_slide,
            'stats': self._generate_stats_slide,
            'image_content': self._generate_image_slide,
            'chart': self._generate_chart_slide,
            'closing': self._generate_closing_slide,
            'section_break': self._generate_section_slide
        }
        
        generator = generators.get(layout_type, self._generate_content_slide)
        
        return generator(
            title=title,
            subtitle=subtitle,
            body_items=body_items,
            slide_data=slide_data,
            ai_instructions=ai_slide_instructions
        )

    def _generate_title_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a stunning title slide"""
        css = self._get_base_css()
        bg_style = self._get_background_style(ai_instructions)
        accent = self._get_accent_element(ai_instructions)
        title_style = self._get_title_style(ai_instructions)
        
        # Determine text colors based on background
        bg = self.theme.get('background', '#ffffff')
        is_dark = self._is_dark_background(bg)
        title_color = '#ffffff' if is_dark else title_style['color']
        subtitle_color = 'rgba(255,255,255,0.85)' if is_dark else self.theme.get('text_muted', '#666666')

        # Get key message from AI for subtitle emphasis
        key_message = ""
        if ai_instructions:
            key_message = ai_instructions.get('key_message', '')

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col center" style="{bg_style}">
        {accent}
        <div class="col center gap-lg" style="z-index:1;max-width:820px;text-align:center;padding:40px;">
            <h1 style="font-size:{title_style['size']};font-weight:{title_style['weight']};color:{title_color};margin:0;line-height:1.15;">
                {self._escape_html(title)}
            </h1>
            {f'<p style="font-size:24px;color:{subtitle_color};margin:0;margin-top:8px;">{self._escape_html(subtitle)}</p>' if subtitle else ''}
            {f'<div style="width:80px;height:4px;background:{self.theme.get("accent", "#0077b6")};border-radius:2px;margin-top:32px;"></div>' if not subtitle else ''}
        </div>
    </div>
</body>
</html>"""

    def _generate_content_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a professional content slide"""
        css = self._get_base_css()
        bg_style = self._get_background_style(ai_instructions)
        accent = self._get_accent_element(ai_instructions)
        title_style = self._get_title_style(ai_instructions)
        spacing = self._get_spacing_style(ai_instructions)
        
        text_color = self.theme.get('text', '#1a1a2e')
        
        # Apply AI emphasis if available
        emphasis_words = []
        if ai_instructions:
            emphasis_words = ai_instructions.get('typography', {}).get('body_emphasis', [])
        
        content_html = self._generate_bullet_list(body_items, text_color, emphasis_words)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col" style="{bg_style}">
        {accent}
        <!-- Title Section -->
        <div style="padding:{spacing['padding']['v']} {spacing['padding']['h']} 0;z-index:1;">
            <h1 style="font-size:{title_style['size']};font-weight:{title_style['weight']};color:{title_style['color']};margin:0;">
                {self._escape_html(title or 'Overview')}
            </h1>
        </div>
        
        <!-- Content Section -->
        <div class="col fill" style="padding:24px {spacing['padding']['h']} {spacing['padding']['v']};gap:{spacing['gap']};z-index:1;">
            {content_html}
        </div>
    </div>
</body>
</html>"""

    def _generate_two_column_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a two-column content slide"""
        css = self._get_base_css()
        bg_style = self._get_background_style(ai_instructions)
        accent = self._get_accent_element(ai_instructions)
        title_style = self._get_title_style(ai_instructions)
        spacing = self._get_spacing_style(ai_instructions)
        
        text_color = self.theme.get('text', '#1a1a2e')
        border_color = self.theme.get('border', '#e5e7eb')
        
        mid = len(body_items) // 2
        left_html = self._generate_bullet_list(body_items[:mid], text_color)
        right_html = self._generate_bullet_list(body_items[mid:], text_color)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col" style="{bg_style}">
        {accent}
        <!-- Title Section -->
        <div style="padding:{spacing['padding']['v']} {spacing['padding']['h']} 0;z-index:1;">
            <h1 style="font-size:{title_style['size']};font-weight:{title_style['weight']};color:{title_style['color']};margin:0;">
                {self._escape_html(title or 'Key Points')}
            </h1>
        </div>
        
        <!-- Two Column Content -->
        <div class="row fill" style="padding:24px {spacing['padding']['h']} {spacing['padding']['v']};gap:48px;z-index:1;">
            <div class="col" style="flex:1;gap:8px;">
                {left_html}
            </div>
            <div style="width:1px;background:{border_color};"></div>
            <div class="col" style="flex:1;gap:8px;">
                {right_html}
            </div>
        </div>
    </div>
</body>
</html>"""

    def _generate_stats_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a statistics showcase slide"""
        css = self._get_base_css()
        bg_style = self._get_background_style(ai_instructions)
        accent = self._get_accent_element(ai_instructions)
        title_style = self._get_title_style(ai_instructions)
        
        surface = self.theme.get('surface', '#f8f9fa')
        
        # Parse stats from body items
        stats_html = ""
        for item in body_items[:4]:
            text = item.get('text', '')
            # Try to parse as value:label
            if ':' in text:
                parts = text.split(':', 1)
            elif '-' in text:
                parts = text.split('-', 1)
            else:
                parts = [text, '']
            
            value = parts[0].strip()
            label = parts[1].strip() if len(parts) > 1 else ''
            
            stats_html += f'''
            <div class="col center card" style="flex:1;min-width:180px;background:{surface};">
                <div class="stat-value">{self._escape_html(value)}</div>
                <div class="stat-label">{self._escape_html(label)}</div>
            </div>
            '''

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col" style="{bg_style}">
        {accent}
        <!-- Title Section -->
        <div style="padding:44px 56px 0;z-index:1;">
            <h1 style="font-size:{title_style['size']};font-weight:{title_style['weight']};color:{title_style['color']};margin:0;">
                {self._escape_html(title or 'Key Metrics')}
            </h1>
        </div>
        
        <!-- Stats Grid -->
        <div class="row center fill" style="padding:32px 56px;gap:24px;flex-wrap:wrap;z-index:1;">
            {stats_html}
        </div>
    </div>
</body>
</html>"""

    def _generate_image_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a slide with image placeholder and content"""
        css = self._get_base_css()
        bg_style = self._get_background_style(ai_instructions)
        accent = self._get_accent_element(ai_instructions)
        title_style = self._get_title_style(ai_instructions)
        
        text_color = self.theme.get('text', '#1a1a2e')
        surface = self.theme.get('surface', '#f5f5f5')
        
        content_html = self._generate_bullet_list(body_items[:5], text_color)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col" style="{bg_style}">
        {accent}
        <!-- Title Section -->
        <div style="padding:44px 56px 0;z-index:1;">
            <h1 style="font-size:{title_style['size']};font-weight:{title_style['weight']};color:{title_style['color']};margin:0;">
                {self._escape_html(title or 'Overview')}
            </h1>
        </div>
        
        <!-- Image + Content Layout -->
        <div class="row fill" style="padding:24px 56px 44px;gap:40px;z-index:1;">
            <div style="flex:1.2;background:{surface};border-radius:16px;display:flex;align-items:center;justify-content:center;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="{self.theme.get('text_muted', '#888')}" stroke-width="1.5" opacity="0.5">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                </svg>
            </div>
            <div class="col" style="flex:1;justify-content:center;">
                {content_html}
            </div>
        </div>
    </div>
</body>
</html>"""

    def _generate_chart_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a chart placeholder slide"""
        css = self._get_base_css()
        bg_style = self._get_background_style(ai_instructions)
        accent = self._get_accent_element(ai_instructions)
        title_style = self._get_title_style(ai_instructions)
        
        text_color = self.theme.get('text', '#1a1a2e')
        surface = self.theme.get('surface', '#f5f5f5')
        
        content_html = self._generate_bullet_list(body_items[:4], text_color) if body_items else ''

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col" style="{bg_style}">
        {accent}
        <!-- Title Section -->
        <div style="padding:44px 56px 0;z-index:1;">
            <h1 style="font-size:{title_style['size']};font-weight:{title_style['weight']};color:{title_style['color']};margin:0;">
                {self._escape_html(title or 'Data Analysis')}
            </h1>
        </div>
        
        <!-- Chart + Content Layout -->
        <div class="row fill" style="padding:24px 56px 44px;gap:40px;z-index:1;">
            <div class="col" style="flex:0.4;justify-content:center;">
                {content_html if content_html else f'<p style="color:{self.theme.get("text_muted", "#666")};font-size:15px;">Data visualization placeholder</p>'}
            </div>
            <div style="flex:0.6;background:{surface};border-radius:16px;display:flex;align-items:center;justify-content:center;">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="{self.theme.get('text_muted', '#888')}" stroke-width="1.5" opacity="0.5">
                    <path d="M3 3v18h18"/>
                    <path d="M18 17V9"/>
                    <path d="M13 17V5"/>
                    <path d="M8 17v-3"/>
                </svg>
            </div>
        </div>
    </div>
</body>
</html>"""

    def _generate_closing_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a professional closing slide"""
        css = self._get_base_css()
        primary = self.theme.get('primary', '#0077b6')
        
        contact = body_items[0].get('text', '') if body_items else ''
        
        # Check AI instructions for CTA
        cta_text = ""
        if ai_instructions:
            special = ai_instructions.get('special_instructions', '')
            if 'cta' in special.lower() or 'call to action' in special.lower():
                cta_text = "Get Started"

        cta_html = ""
        if cta_text:
            cta_html = f'''
            <div style="margin-top:36px;">
                <div style="display:inline-block;background:#ffffff;padding:16px 36px;border-radius:10px;">
                    <span style="font-size:17px;font-weight:600;color:{primary};">{self._escape_html(cta_text)}</span>
                </div>
            </div>
            '''

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col center" style="background-color:{primary};">
        <div class="col center gap-lg" style="text-align:center;max-width:720px;">
            <h1 style="font-size:56px;font-weight:700;color:#ffffff;margin:0;">
                {self._escape_html(title or 'Thank You')}
            </h1>
            {f'<p style="font-size:21px;color:rgba(255,255,255,0.9);margin:0;">{self._escape_html(contact)}</p>' if contact else ''}
            {cta_html}
        </div>
    </div>
</body>
</html>"""

    def _generate_section_slide(self, title: str, subtitle: str, body_items: List, slide_data: Dict, ai_instructions: Optional[Dict]) -> str:
        """Generate a section break slide"""
        css = self._get_base_css()
        bg_style = self._get_background_style(ai_instructions)
        
        primary = self.theme.get('primary', '#0077b6')
        accent = self.theme.get('accent', primary)
        
        # Check if there's a section number
        section_num = ""
        if ai_instructions:
            purpose = ai_instructions.get('purpose', '')
            if 'section' in purpose.lower():
                # Extract number if present
                import re
                nums = re.findall(r'\d+', purpose)
                if nums:
                    section_num = nums[0]

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=960, height=540">
    <style>{css}</style>
</head>
<body>
    <div class="slide col center" style="{bg_style}">
        <div class="col center gap-md" style="text-align:center;">
            {f'<div style="font-size:80px;font-weight:200;color:{accent};opacity:0.2;line-height:1;">{section_num}</div>' if section_num else ''}
            <h1 style="font-size:48px;font-weight:600;color:{primary};margin:0;">
                {self._escape_html(title or 'Section')}
            </h1>
            <div style="width:80px;height:4px;background:{accent};border-radius:2px;margin-top:20px;"></div>
        </div>
    </div>
</body>
</html>"""

    def _generate_bullet_list(self, items: List[Dict], text_color: str, emphasis_words: List[str] = None) -> str:
        """Generate a bullet list with optional emphasis"""
        if not items:
            return ""
        
        html = '<ul style="margin:0;">'
        for item in items[:8]:
            text = item.get('text', '')
            
            # Apply emphasis if specified
            if emphasis_words:
                for word in emphasis_words:
                    if word.lower() in text.lower():
                        text = text.replace(word, f'<span class="emphasis">{word}</span>')
            
            html += f'<li style="color:{text_color};font-size:17px;line-height:1.6;">{self._escape_html(text)}</li>'
        html += '</ul>'
        
        return html

    def _is_dark_background(self, bg: str) -> bool:
        """Check if background is dark"""
        if 'gradient' in str(bg).lower():
            return any(x in bg.lower() for x in ['#0', '#1', '#2', 'dark'])
        if bg.startswith('#'):
            hex_color = bg.lstrip('#')
            if len(hex_color) >= 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                return luminance < 0.5
        return False

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not isinstance(text, str):
            text = str(text)
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))


class RedesignEngine:
    """Main engine that orchestrates the redesign process with AI-powered instructions"""

    def __init__(
        self, 
        style: Dict, 
        parsed_content: Dict, 
        ai_design_result: Optional[Dict] = None
    ):
        self.style = style
        self.parsed_content = parsed_content
        self.ai_design_result = ai_design_result or {}
        self.designer = SlideDesigner(style, ai_design_result)
        self.slides_html = []

    def redesign(self) -> List[Dict]:
        """Redesign all slides with AI-powered instructions"""
        slides = self.parsed_content.get("slides", [])
        slide_instructions = self.ai_design_result.get("slide_instructions", [])

        for i, slide in enumerate(slides):
            # Get AI instructions for this specific slide
            ai_slide_inst = None
            if slide_instructions and i < len(slide_instructions):
                ai_slide_inst = slide_instructions[i]
            
            # Determine layout type
            layout_type = self._determine_layout(slide, ai_slide_inst)
            
            # Generate HTML with AI guidance
            html = self.designer.generate_slide_html(
                slide_data=slide,
                slide_index=i,
                ai_slide_instructions=ai_slide_inst
            )
            
            self.slides_html.append({
                "slide_number": i + 1,
                "layout_type": layout_type,
                "html": html,
                "original_content": slide.get("text_content", []),
                "ai_instructions": ai_slide_inst,
                "has_chart": slide.get("has_chart", False),
                "has_table": slide.get("has_table", False),
                "has_images": len(slide.get("images", [])) > 0
            })

        return self.slides_html

    def _determine_layout(self, slide: Dict, ai_instructions: Optional[Dict]) -> str:
        """Determine the best layout for a slide"""
        
        # AI instructions take priority
        if ai_instructions:
            layout = ai_instructions.get('layout', {})
            return layout.get('type', 'content')
        
        # Fallback to content analysis
        text_content = slide.get("text_content", [])
        
        # Check for title slide
        types = [t.get("type", "") for t in text_content]
        if "ctrTitle" in types or "subTitle" in types:
            if len(text_content) <= 2:
                return "title"
        
        # Check for closing slide
        all_text = " ".join([t.get("text", "") for t in text_content]).lower()
        if any(word in all_text for word in ["thank", "questions", "contact"]):
            return "closing"
        
        # Check for data slides
        if slide.get("has_chart"):
            return "chart"
        if slide.get("images"):
            return "image_content"
        
        # Check content density
        body_count = sum(1 for t in text_content if t.get("type") not in ["title", "ctrTitle"])
        if body_count > 5:
            return "two_column"
        
        return "content"

    def get_html_files(self, output_dir: str) -> List[str]:
        """Write HTML files and return paths"""
        paths = []
        for i, slide in enumerate(self.slides_html):
            path = os.path.join(output_dir, f"slide{i + 1}.html")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(slide["html"])
            paths.append(path)
        return paths
