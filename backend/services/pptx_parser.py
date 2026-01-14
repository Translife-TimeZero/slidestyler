"""
PowerPoint Parser Service
Extracts content, structure, and metadata from uploaded PPTX files
"""

import os
import json
import zipfile
import tempfile
import shutil
import base64
import re
from pathlib import Path
from xml.etree import ElementTree as ET

# XML namespaces for PPTX
NAMESPACES = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'cp': 'http://schemas.openxmlformats.org/package/2006/content-types',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships'
}

class PPTXParser:
    def __init__(self, pptx_path):
        self.pptx_path = pptx_path
        self.temp_dir = None
        self.slides = []
        self.metadata = {}
        self.media = {}
        self.theme_colors = {}

    def parse(self):
        """Main entry point - parse the entire presentation"""
        self.temp_dir = tempfile.mkdtemp()
        try:
            # Extract PPTX (it's a ZIP file)
            with zipfile.ZipFile(self.pptx_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)

            # Parse components
            self._parse_presentation_metadata()
            self._parse_theme()
            self._parse_slides()
            self._extract_media()

            print(f"[Parser] Parsed {len(self.slides)} slides")
            for i, slide in enumerate(self.slides):
                print(f"  Slide {i+1}: {len(slide.get('text_content', []))} text items, layout={slide.get('layout_type')}")
            
            return {
                'metadata': self.metadata,
                'slides': self.slides,
                'media': self.media,
                'theme_colors': self.theme_colors,
                'slide_count': len(self.slides)
            }
        finally:
            # Cleanup temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def _parse_presentation_metadata(self):
        """Parse presentation.xml for metadata"""
        pres_path = os.path.join(self.temp_dir, 'ppt', 'presentation.xml')
        if not os.path.exists(pres_path):
            return

        tree = ET.parse(pres_path)
        root = tree.getroot()

        # Get slide size
        sld_sz = root.find('.//p:sldSz', NAMESPACES)
        if sld_sz is not None:
            # EMUs to pixels (914400 EMUs = 1 inch, assume 96 DPI)
            cx = int(sld_sz.get('cx', '9144000'))
            cy = int(sld_sz.get('cy', '6858000'))
            self.metadata['width'] = cx / 914400 * 96
            self.metadata['height'] = cy / 914400 * 96
            self.metadata['aspect_ratio'] = '16:9' if abs(cx/cy - 16/9) < 0.1 else '4:3'

        # Count slides
        sld_id_lst = root.find('.//p:sldIdLst', NAMESPACES)
        if sld_id_lst is not None:
            self.metadata['slide_count'] = len(sld_id_lst.findall('p:sldId', NAMESPACES))

    def _parse_theme(self):
        """Parse theme for colors"""
        theme_dir = os.path.join(self.temp_dir, 'ppt', 'theme')
        if not os.path.exists(theme_dir):
            return

        # Find theme1.xml
        theme_path = os.path.join(theme_dir, 'theme1.xml')
        if not os.path.exists(theme_path):
            return

        tree = ET.parse(theme_path)
        root = tree.getroot()

        # Parse color scheme
        clr_scheme = root.find('.//a:clrScheme', NAMESPACES)
        if clr_scheme is not None:
            color_mappings = {
                'dk1': 'dark1',
                'lt1': 'light1',
                'dk2': 'dark2',
                'lt2': 'light2',
                'accent1': 'accent1',
                'accent2': 'accent2',
                'accent3': 'accent3',
                'accent4': 'accent4',
                'accent5': 'accent5',
                'accent6': 'accent6',
                'hlink': 'hyperlink',
                'folHlink': 'followed_hyperlink'
            }

            for xml_name, py_name in color_mappings.items():
                color_elem = clr_scheme.find(f'a:{xml_name}', NAMESPACES)
                if color_elem is not None:
                    # Check for srgbClr or sysClr
                    srgb = color_elem.find('a:srgbClr', NAMESPACES)
                    if srgb is not None:
                        self.theme_colors[py_name] = '#' + srgb.get('val', '000000')
                    else:
                        sys_clr = color_elem.find('a:sysClr', NAMESPACES)
                        if sys_clr is not None:
                            self.theme_colors[py_name] = '#' + sys_clr.get('lastClr', '000000')

    def _parse_slides(self):
        """Parse all slides"""
        slides_dir = os.path.join(self.temp_dir, 'ppt', 'slides')
        if not os.path.exists(slides_dir):
            return

        # Get slide files sorted by number
        slide_files = []
        for f in os.listdir(slides_dir):
            if f.startswith('slide') and f.endswith('.xml'):
                match = re.search(r'slide(\d+)\.xml', f)
                if match:
                    slide_files.append((int(match.group(1)), f))

        slide_files.sort(key=lambda x: x[0])

        for idx, (num, filename) in enumerate(slide_files):
            slide_path = os.path.join(slides_dir, filename)
            slide_data = self._parse_single_slide(slide_path, idx)
            slide_data['slide_number'] = idx + 1
            slide_data['filename'] = filename
            self.slides.append(slide_data)

    def _parse_single_slide(self, slide_path, slide_index):
        """Parse a single slide XML file"""
        tree = ET.parse(slide_path)
        root = tree.getroot()

        slide_data = {
            'shapes': [],
            'text_content': [],
            'images': [],
            'has_chart': False,
            'has_table': False,
            'layout_type': 'unknown'
        }

        # Find shape tree
        sp_tree = root.find('.//p:spTree', NAMESPACES)
        if sp_tree is None:
            return slide_data

        # Parse shapes
        for shape in sp_tree.findall('.//p:sp', NAMESPACES):
            shape_data = self._parse_shape(shape)
            if shape_data:
                slide_data['shapes'].append(shape_data)
                if shape_data.get('text'):
                    placeholder_type = shape_data.get('placeholder_type') or 'body'
                    
                    # For title-like content, use the full text
                    # For body content with multiple paragraphs, split into separate items
                    if placeholder_type in ['title', 'ctrTitle', 'subTitle']:
                        text_item = {
                            'type': placeholder_type,
                            'text': shape_data['text'],
                            'formatting': shape_data.get('formatting', {})
                        }
                        slide_data['text_content'].append(text_item)
                        print(f"  [Parser] Found text: type={text_item['type']}, text={text_item['text'][:50]}...")
                    else:
                        # Split body text into individual paragraphs
                        paragraphs = shape_data.get('text_paragraphs', [shape_data['text']])
                        for para in paragraphs:
                            para = para.strip()
                            if para:
                                text_item = {
                                    'type': placeholder_type,
                                    'text': para,
                                    'formatting': shape_data.get('formatting', {})
                                }
                                slide_data['text_content'].append(text_item)
                                print(f"  [Parser] Found text: type={text_item['type']}, text={text_item['text'][:50]}...")

        # Check for charts
        if sp_tree.find('.//p:graphicFrame', NAMESPACES) is not None:
            slide_data['has_chart'] = True

        # Check for tables
        if root.find('.//a:tbl', NAMESPACES) is not None:
            slide_data['has_table'] = True

        # Parse images
        for pic in sp_tree.findall('.//p:pic', NAMESPACES):
            img_data = self._parse_image(pic, slide_index)
            if img_data:
                slide_data['images'].append(img_data)

        # Determine layout type based on content
        slide_data['layout_type'] = self._determine_layout_type(slide_data)

        return slide_data

    def _parse_shape(self, shape):
        """Parse a shape element"""
        shape_data = {
            'type': 'shape',
            'text': '',
            'formatting': {},
            'position': {},
            'placeholder_type': None
        }

        # Get placeholder type
        nv_sp_pr = shape.find('.//p:nvSpPr', NAMESPACES)
        if nv_sp_pr is not None:
            nv_pr = nv_sp_pr.find('p:nvPr', NAMESPACES)
            if nv_pr is not None:
                ph = nv_pr.find('p:ph', NAMESPACES)
                if ph is not None:
                    shape_data['placeholder_type'] = ph.get('type', 'body')

        # Get position
        xfrm = shape.find('.//p:spPr/a:xfrm', NAMESPACES)
        if xfrm is not None:
            off = xfrm.find('a:off', NAMESPACES)
            ext = xfrm.find('a:ext', NAMESPACES)
            if off is not None:
                shape_data['position']['x'] = int(off.get('x', '0')) / 914400
                shape_data['position']['y'] = int(off.get('y', '0')) / 914400
            if ext is not None:
                shape_data['position']['width'] = int(ext.get('cx', '0')) / 914400
                shape_data['position']['height'] = int(ext.get('cy', '0')) / 914400

        # Get text content
        tx_body = shape.find('p:txBody', NAMESPACES)
        if tx_body is not None:
            paragraphs = []
            for p in tx_body.findall('a:p', NAMESPACES):
                para_text = self._extract_paragraph_text(p)
                if para_text:
                    paragraphs.append(para_text)
            # Store as list for multi-paragraph content, joined for display
            shape_data['text'] = '\n'.join(paragraphs)
            shape_data['text_paragraphs'] = paragraphs  # Keep individual paragraphs
            shape_data['formatting'] = self._extract_text_formatting(tx_body)

        return shape_data if shape_data['text'] or shape_data['placeholder_type'] else None

    def _extract_paragraph_text(self, paragraph):
        """Extract text from a paragraph element"""
        texts = []
        # Try finding text runs
        for r in paragraph.findall('.//a:r', NAMESPACES):
            t = r.find('a:t', NAMESPACES)
            if t is not None and t.text:
                texts.append(t.text)
        
        # Also check for direct text (a:t without a:r wrapper)
        for t in paragraph.findall('a:t', NAMESPACES):
            if t.text:
                texts.append(t.text)
        
        # Check for field text (like slide numbers)
        for fld in paragraph.findall('.//a:fld', NAMESPACES):
            t = fld.find('a:t', NAMESPACES)
            if t is not None and t.text:
                texts.append(t.text)
        
        return ' '.join(texts)

    def _extract_text_formatting(self, tx_body):
        """Extract formatting information from text body"""
        formatting = {
            'is_bold': False,
            'is_italic': False,
            'font_size': None,
            'font_name': None,
            'color': None,
            'alignment': 'left'
        }

        # Check first run for formatting
        first_r = tx_body.find('.//a:r', NAMESPACES)
        if first_r is not None:
            rPr = first_r.find('a:rPr', NAMESPACES)
            if rPr is not None:
                formatting['is_bold'] = rPr.get('b') == '1'
                formatting['is_italic'] = rPr.get('i') == '1'
                sz = rPr.get('sz')
                if sz:
                    formatting['font_size'] = int(sz) / 100  # hundredths of a point

                # Check for color
                solid_fill = rPr.find('a:solidFill', NAMESPACES)
                if solid_fill is not None:
                    srgb = solid_fill.find('a:srgbClr', NAMESPACES)
                    if srgb is not None:
                        formatting['color'] = '#' + srgb.get('val', '000000')

        # Check paragraph alignment
        first_p = tx_body.find('a:p', NAMESPACES)
        if first_p is not None:
            pPr = first_p.find('a:pPr', NAMESPACES)
            if pPr is not None:
                algn = pPr.get('algn')
                if algn:
                    formatting['alignment'] = {'l': 'left', 'ctr': 'center', 'r': 'right'}.get(algn, 'left')

        return formatting

    def _parse_image(self, pic, slide_index):
        """Parse an image element"""
        img_data = {
            'type': 'image',
            'position': {},
            'rel_id': None
        }

        # Get position
        sp_pr = pic.find('p:spPr', NAMESPACES)
        if sp_pr is not None:
            xfrm = sp_pr.find('a:xfrm', NAMESPACES)
            if xfrm is not None:
                off = xfrm.find('a:off', NAMESPACES)
                ext = xfrm.find('a:ext', NAMESPACES)
                if off is not None:
                    img_data['position']['x'] = int(off.get('x', '0')) / 914400
                    img_data['position']['y'] = int(off.get('y', '0')) / 914400
                if ext is not None:
                    img_data['position']['width'] = int(ext.get('cx', '0')) / 914400
                    img_data['position']['height'] = int(ext.get('cy', '0')) / 914400

        # Get relationship ID for the image
        blip_fill = pic.find('p:blipFill', NAMESPACES)
        if blip_fill is not None:
            blip = blip_fill.find('a:blip', NAMESPACES)
            if blip is not None:
                embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                if embed:
                    img_data['rel_id'] = embed

        return img_data if img_data['rel_id'] else None

    def _extract_media(self):
        """Extract media files from the presentation"""
        media_dir = os.path.join(self.temp_dir, 'ppt', 'media')
        if not os.path.exists(media_dir):
            return

        for filename in os.listdir(media_dir):
            file_path = os.path.join(media_dir, filename)
            if os.path.isfile(file_path):
                # Read and base64 encode small images
                file_size = os.path.getsize(file_path)
                if file_size < 5 * 1024 * 1024:  # Less than 5MB
                    with open(file_path, 'rb') as f:
                        content = f.read()

                    ext = os.path.splitext(filename)[1].lower()
                    mime_types = {
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.gif': 'image/gif',
                        '.svg': 'image/svg+xml'
                    }
                    mime_type = mime_types.get(ext, 'application/octet-stream')

                    self.media[filename] = {
                        'data': base64.b64encode(content).decode('utf-8'),
                        'mime_type': mime_type,
                        'size': file_size
                    }

    def _determine_layout_type(self, slide_data):
        """Determine the layout type based on content"""
        placeholders = [s.get('placeholder_type') for s in slide_data['shapes']]

        if 'ctrTitle' in placeholders or 'subTitle' in placeholders:
            return 'title'
        elif slide_data['has_chart']:
            return 'chart'
        elif slide_data['has_table']:
            return 'table'
        elif len(slide_data['images']) > 0:
            return 'image'
        elif 'title' in placeholders and 'body' in placeholders:
            return 'title_content'
        elif len(slide_data['text_content']) == 1:
            return 'single_content'
        else:
            return 'content'


def parse_pptx(file_path):
    """Convenience function to parse a PPTX file"""
    parser = PPTXParser(file_path)
    return parser.parse()


def get_slide_thumbnails(pptx_path, output_dir):
    """Generate slide thumbnails using LibreOffice"""
    import subprocess

    # Convert to PDF first
    pdf_path = os.path.join(output_dir, 'presentation.pdf')
    subprocess.run([
        'soffice', '--headless', '--convert-to', 'pdf',
        '--outdir', output_dir, pptx_path
    ], check=True, capture_output=True)

    # Convert PDF to images
    subprocess.run([
        'pdftoppm', '-jpeg', '-r', '150', pdf_path,
        os.path.join(output_dir, 'slide')
    ], check=True, capture_output=True)

    # Collect thumbnail paths
    thumbnails = []
    for f in sorted(os.listdir(output_dir)):
        if f.startswith('slide') and f.endswith('.jpg'):
            thumbnails.append(os.path.join(output_dir, f))

    return thumbnails
