"""
PowerPoint Redesigner - Flask Backend
Full API for uploading, analyzing, and redesigning PowerPoint presentations
"""

import os
import json
import uuid
import tempfile
import shutil
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import our services
from services.pptx_parser import PPTXParser, parse_pptx
from services.ai_analyzer import AIAnalyzer, DesignIntelligence
from services.ai_design_director import AIDesignDirector, get_ai_design_instructions
from services.redesign_engine import RedesignEngine, SlideDesigner
from services.pptx_exporter import PPTXExporter, export_presentation
from styles.style_library import (
    get_all_styles,
    get_style_by_name,
    get_styles_by_category,
    get_categories,
    get_style_preview_data
)

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app, origins=[
    "http://localhost:3000", 
    "http://localhost:8000", 
    "http://localhost:5000",
    "https://slidestyler.vercel.app",
    "https://slidestyler-*.vercel.app"
], supports_credentials=True)

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
OUTPUT_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'pptx'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Store for active sessions
sessions = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_session(session_id):
    """Get or create a session"""
    if session_id not in sessions:
        sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'status': 'initialized',
            'original_file': None,
            'parsed_content': None,
            'selected_style': None,
            'redesigned_slides': None,
            'output_file': None
        }
    return sessions[session_id]


# ============ API Routes ============

@app.route('/')
def serve_frontend():
    """Serve the React frontend"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'service': 'pptx-redesigner'
    })


# ============ Style Endpoints ============

@app.route('/api/styles', methods=['GET'])
def get_styles():
    """Get all available styles"""
    category = request.args.get('category')

    if category:
        styles = get_styles_by_category(category)
        return jsonify({
            'styles': [
                {
                    'id': k,
                    'name': v['name'],
                    'description': v['description'],
                    'category': v['category'],
                    'preview_colors': v['preview_colors']
                }
                for k, v in styles.items()
            ]
        })

    return jsonify({
        'styles': get_style_preview_data(),
        'categories': get_categories()
    })


@app.route('/api/styles/<style_id>', methods=['GET'])
def get_style_details(style_id):
    """Get detailed style information"""
    style = get_style_by_name(style_id)
    if not style:
        return jsonify({'error': 'Style not found'}), 404

    return jsonify({
        'id': style_id,
        **style
    })


# ============ Upload & Parse Endpoints ============

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a PowerPoint file for redesign"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .pptx files are allowed'}), 400

    # Create session
    session_id = str(uuid.uuid4())
    session = get_session(session_id)

    # Save file
    filename = secure_filename(file.filename)
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)

    file_path = os.path.join(session_dir, filename)
    file.save(file_path)

    session['original_file'] = file_path
    session['original_filename'] = filename
    session['status'] = 'uploaded'

    return jsonify({
        'session_id': session_id,
        'filename': filename,
        'status': 'uploaded',
        'message': 'File uploaded successfully'
    })


@app.route('/api/sessions/<session_id>/parse', methods=['POST'])
def parse_presentation(session_id):
    """Parse an uploaded presentation"""
    session = get_session(session_id)

    if not session.get('original_file'):
        return jsonify({'error': 'No file uploaded for this session'}), 400

    try:
        # Parse the presentation
        parsed = parse_pptx(session['original_file'])
        session['parsed_content'] = parsed
        session['status'] = 'parsed'

        # Generate thumbnails
        thumbnail_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id, 'thumbnails')
        os.makedirs(thumbnail_dir, exist_ok=True)

        try:
            # Convert to PDF and then to images
            subprocess.run([
                'soffice', '--headless', '--convert-to', 'pdf',
                '--outdir', thumbnail_dir, session['original_file']
            ], check=True, capture_output=True, timeout=60)

            pdf_files = [f for f in os.listdir(thumbnail_dir) if f.endswith('.pdf')]
            if pdf_files:
                pdf_path = os.path.join(thumbnail_dir, pdf_files[0])
                subprocess.run([
                    'pdftoppm', '-jpeg', '-r', '100', pdf_path,
                    os.path.join(thumbnail_dir, 'slide')
                ], check=True, capture_output=True, timeout=60)

            session['thumbnails_ready'] = True
        except Exception as e:
            session['thumbnails_ready'] = False
            print(f"Thumbnail generation failed: {e}")

        return jsonify({
            'session_id': session_id,
            'status': 'parsed',
            'slide_count': parsed.get('slide_count', len(parsed.get('slides', []))),
            'metadata': parsed.get('metadata', {}),
            'slides_summary': [
                {
                    'slide_number': s.get('slide_number'),
                    'layout_type': s.get('layout_type'),
                    'has_chart': s.get('has_chart'),
                    'has_table': s.get('has_table'),
                    'text_preview': s.get('text_content', [{}])[0].get('text', '')[:100] if s.get('text_content') else ''
                }
                for s in parsed.get('slides', [])
            ],
            'thumbnails_ready': session.get('thumbnails_ready', False)
        })

    except Exception as e:
        session['status'] = 'error'
        session['error'] = str(e)
        return jsonify({'error': f'Failed to parse presentation: {str(e)}'}), 500


@app.route('/api/sessions/<session_id>/thumbnails/<int:slide_num>', methods=['GET'])
def get_thumbnail(session_id, slide_num):
    """Get thumbnail for a specific slide"""
    thumbnail_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id, 'thumbnails')

    # Find the thumbnail file
    thumbnail_file = f'slide-{slide_num}.jpg'
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_file)

    if os.path.exists(thumbnail_path):
        return send_file(thumbnail_path, mimetype='image/jpeg')

    return jsonify({'error': 'Thumbnail not found'}), 404


# ============ AI Analysis Endpoints ============

@app.route('/api/sessions/<session_id>/analyze', methods=['POST'])
def analyze_presentation(session_id):
    """Run AI analysis on the presentation"""
    session = get_session(session_id)

    if not session.get('parsed_content'):
        return jsonify({'error': 'Presentation not parsed yet'}), 400

    data = request.get_json() or {}
    provider = data.get('ai_provider', 'gemini')
    api_key = data.get('api_key')

    try:
        # Use design intelligence for rule-based analysis
        design_intel = DesignIntelligence()
        slides = session['parsed_content'].get('slides', [])

        analysis_results = {
            'slides': [],
            'presentation': {}
        }

        for i, slide in enumerate(slides):
            content_type = design_intel.analyze_content_type(slide)
            layout_rec = design_intel.get_layout_recommendation(
                content_type,
                len(slide.get('text_content', []))
            )
            font_sizes = design_intel.calculate_font_sizes(
                slide.get('text_content', []),
                960, 540
            )

            analysis_results['slides'].append({
                'slide_number': i + 1,
                'content_type': content_type,
                'layout_recommendation': layout_rec,
                'font_sizes': font_sizes
            })

        # Run async AI analysis if API key provided
        if api_key:
            async def run_ai_analysis():
                analyzer = AIAnalyzer(provider=provider, api_key=api_key)
                struct_analysis = await analyzer.analyze_presentation_structure(slides)
                analysis_results['presentation'] = struct_analysis

                # Get style recommendations
                style_match = await analyzer.suggest_style_match(
                    struct_analysis,
                    get_style_preview_data()
                )
                analysis_results['style_recommendations'] = style_match

            asyncio.run(run_ai_analysis())

        session['analysis'] = analysis_results
        session['status'] = 'analyzed'

        return jsonify({
            'session_id': session_id,
            'status': 'analyzed',
            'analysis': analysis_results
        })

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


# ============ Redesign Endpoints ============

@app.route('/api/sessions/<session_id>/redesign', methods=['POST'])
def redesign_presentation(session_id):
    """Redesign the presentation with AI-powered world-class design"""
    session = get_session(session_id)

    if not session.get('parsed_content'):
        return jsonify({'error': 'Presentation not parsed yet'}), 400

    data = request.get_json() or {}
    style_id = data.get('style_id')
    use_ai_design = data.get('use_ai_design', True)  # Enable AI by default
    api_key = data.get('api_key')  # Replicate API key for AI features
    generate_images = data.get('generate_images', False)  # Optional image generation

    if not style_id:
        return jsonify({'error': 'No style selected'}), 400

    style = get_style_by_name(style_id)
    if not style:
        return jsonify({'error': 'Invalid style'}), 400

    try:
        session['selected_style'] = style_id
        session['status'] = 'redesigning'

        slides_data = session['parsed_content'].get('slides', [])
        ai_design_result = None

        # Step 1: Get AI Design Director instructions if enabled
        if use_ai_design:
            session['status'] = 'ai_analyzing'
            
            async def run_ai_design():
                return await get_ai_design_instructions(
                    slides_data=slides_data,
                    style_theme=style.get('theme', {}),
                    api_key=api_key,
                    generate_images=generate_images
                )
            
            try:
                ai_design_result = asyncio.run(run_ai_design())
                session['ai_design_result'] = ai_design_result
            except Exception as e:
                print(f"AI Design analysis failed, using fallback: {e}")
                ai_design_result = None

        session['status'] = 'redesigning'

        # Step 2: Create redesign engine with AI instructions
        engine = RedesignEngine(
            style=style,
            parsed_content=session['parsed_content'],
            ai_design_result=ai_design_result
        )

        # Step 3: Redesign all slides with AI-guided design
        redesigned = engine.redesign()
        session['redesigned_slides'] = redesigned

        # Step 4: Write HTML files
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(output_dir, exist_ok=True)

        html_paths = engine.get_html_files(output_dir)
        session['html_files'] = html_paths
        session['status'] = 'redesigned'

        # Prepare response with AI insights
        response_data = {
            'session_id': session_id,
            'status': 'redesigned',
            'style_applied': style_id,
            'slides_count': len(redesigned),
            'ai_powered': ai_design_result is not None,
            'slides': [
                {
                    'slide_number': s.get('slide_number'),
                    'layout_type': s.get('layout_type'),
                    'has_chart': s.get('has_chart'),
                    'has_table': s.get('has_table'),
                    'ai_purpose': s.get('ai_instructions', {}).get('purpose') if s.get('ai_instructions') else None
                }
                for s in redesigned
            ]
        }

        # Include AI insights if available
        if ai_design_result:
            presentation_analysis = ai_design_result.get('presentation_analysis', {})
            visual_concept = ai_design_result.get('visual_concept', {})
            
            response_data['ai_insights'] = {
                'presentation_type': presentation_analysis.get('presentation_type'),
                'primary_purpose': presentation_analysis.get('primary_purpose'),
                'visual_mood': presentation_analysis.get('visual_mood'),
                'concept_name': visual_concept.get('concept_name'),
                'concept_description': visual_concept.get('concept_description')
            }
            
            # Include generated images if any
            if ai_design_result.get('generated_images'):
                response_data['generated_images'] = ai_design_result['generated_images']

        return jsonify(response_data)

    except Exception as e:
        session['status'] = 'error'
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Redesign failed: {str(e)}'}), 500


@app.route('/api/sessions/<session_id>/preview/<int:slide_num>', methods=['GET'])
def preview_slide(session_id, slide_num):
    """Get HTML preview of a redesigned slide"""
    session = get_session(session_id)

    if not session.get('redesigned_slides'):
        return jsonify({'error': 'Presentation not redesigned yet'}), 400

    if slide_num < 1 or slide_num > len(session['redesigned_slides']):
        return jsonify({'error': 'Invalid slide number'}), 400

    slide = session['redesigned_slides'][slide_num - 1]
    return slide['html'], 200, {'Content-Type': 'text/html'}


# ============ Export Endpoints ============

@app.route('/api/sessions/<session_id>/export', methods=['POST'])
def export_presentation_endpoint(session_id):
    """Export the redesigned presentation as PPTX"""
    session = get_session(session_id)

    if not session.get('redesigned_slides'):
        return jsonify({'error': 'Presentation not redesigned yet'}), 400

    try:
        # Generate the professional PPTX directly
        output_path = generate_professional_pptx(session)
        
        if output_path:
            session['output_file'] = output_path
            session['status'] = 'exported'

            return jsonify({
                'session_id': session_id,
                'status': 'exported',
                'download_url': f'/api/sessions/{session_id}/download'
            })
        else:
            return jsonify({'error': 'Failed to generate PPTX'}), 500

    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@app.route('/api/sessions/<session_id>/download', methods=['GET'])
def download_presentation(session_id):
    """Download the exported presentation"""
    session = get_session(session_id)

    if not session.get('output_file') or not os.path.exists(session['output_file']):
        # Generate professional PPTX
        output_path = generate_professional_pptx(session)
        if output_path:
            session['output_file'] = output_path

    if session.get('output_file') and os.path.exists(session['output_file']):
        return send_file(
            session['output_file'],
            as_attachment=True,
            download_name=f"redesigned_{session.get('original_filename', 'presentation.pptx')}"
        )

    return jsonify({'error': 'File not found'}), 404


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """Get current session status"""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404

    session = sessions[session_id]
    return jsonify({
        'id': session['id'],
        'status': session['status'],
        'created_at': session['created_at'],
        'original_filename': session.get('original_filename'),
        'selected_style': session.get('selected_style'),
        'slide_count': len(session.get('redesigned_slides', []))
    })


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session and its files"""
    if session_id in sessions:
        session = sessions[session_id]

        # Clean up files
        session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        session_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)

        if os.path.exists(session_upload_dir):
            shutil.rmtree(session_upload_dir)
        if os.path.exists(session_output_dir):
            shutil.rmtree(session_output_dir)

        del sessions[session_id]

    return jsonify({'status': 'deleted'})


# ============ Helper Functions ============

def generate_conversion_script(html_files: list, output_path: str, style: dict) -> str:
    """Generate the Node.js script for HTML to PPTX conversion"""
    slides_code = []
    for i, html_file in enumerate(html_files):
        slides_code.append(f'await html2pptx("{html_file}", pptx);')

    return f"""
const pptxgen = require("pptxgenjs");
const {{ html2pptx }} = require("./html2pptx");

async function convert() {{
    const pptx = new pptxgen();
    pptx.layout = "LAYOUT_16x9";
    pptx.title = "Redesigned Presentation";
    pptx.author = "PPTX Redesigner";

    {chr(10).join(slides_code)}

    await pptx.writeFile("{output_path}");
    console.log("Presentation created successfully!");
}}

convert().catch(console.error);
"""


def generate_professional_pptx(session: dict, use_ai: bool = True) -> str:
    """Generate a professional PPTX - optionally using AI for design"""
    try:
        slides_data = session.get('redesigned_slides', [])
        
        if not slides_data:
            return None
        
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session['id'])
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'redesigned_presentation.pptx')
        
        if use_ai:
            # Use AI-powered generator for custom designs
            from services.ai_pptx_generator import generate_ai_presentation
            api_key = os.environ.get('REPLICATE_API_TOKEN')
            
            try:
                asyncio.run(generate_ai_presentation(slides_data, output_path, api_key))
                print(f"[AI Generator] Successfully created AI-designed presentation")
                return output_path
            except Exception as ai_error:
                print(f"[AI Generator] Failed: {ai_error}, falling back to template")
        
        # Fallback to template-based exporter
        style = get_style_by_name(session.get('selected_style', 'executive_minimal'))
        export_presentation(style, slides_data, output_path)
        
        return output_path

    except Exception as e:
        print(f"PPTX generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============ Main ============

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    print("Starting SlideStyler API...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"Server running at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
