# SlideStyler

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Translife-TimeZero/slidestyler) - AI-Powered World-Class PowerPoint Redesigner

Transform your PowerPoint presentations with an AI Design Director that acts as the world's top PowerPoint designer. Get per-slide design instructions tailored to your content with consistent visual concepts across your entire presentation.

![SlideStyler Preview](https://via.placeholder.com/1200x630/1a1a2e/a78bfa?text=SlideStyler+-+AI+Design+Director)

## ✨ What Makes SlideStyler Special

### 🧠 AI Design Director
Our AI acts as a **world-class PowerPoint designer** who:
- Analyzes your entire presentation to understand its purpose and audience
- Creates a unified **visual concept** that ties everything together
- Provides **per-slide design instructions** tailored to each slide's content
- Ensures **visual consistency** while highlighting what matters

### 🎨 Per-Slide Intelligence
For each slide, the AI determines:
- **Layout type** - Best structure for the content
- **Typography** - Font sizes, weights, and emphasis points  
- **Color application** - How to use theme colors effectively
- **Visual elements** - Accent bars, shapes, and decorative elements
- **Spacing** - Content density and breathing room
- **Key message** - What viewers should take away

### 🖼️ Visual Concept Generation (Seedream-4)
Optionally generate **consistent visual elements** using ByteDance's Seedream-4:
- Abstract imagery that matches your presentation's mood
- Consistent visual motifs across all slides
- Professional backgrounds and accents

## 🎯 20+ Professional Styles

| Category | Styles |
|----------|--------|
| **Corporate** | Executive Minimal, Corporate Blue, Dark Executive |
| **Modern** | Modern Gradient, Neon Dark, Glassmorphism |
| **Startup** | Startup Fresh, Tech Minimal |
| **Creative** | Bold Creative, Pastel Dream, Retro Vintage |
| **Educational** | Academic Classic, Science Modern |
| **Industry** | Healthcare Clean, Finance Professional, Real Estate Luxury |
| **Nature** | Eco Green, Ocean Calm |
| **Minimalist** | Pure White, Monochrome Elegant |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+

### Local Development

```bash
# Clone or download the project
cd SlideStyler

# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# In a new terminal - Frontend setup  
cd frontend
npm install
npm start
```

Visit `http://localhost:3000` in your browser.

## 🧠 How the AI Design Director Works

### 1. Presentation Analysis
```
The AI first analyzes your entire presentation holistically:
- What type of presentation is this? (pitch, report, educational, etc.)
- Who is the target audience?
- What's the narrative arc?
- What emotional journey should viewers experience?
```

### 2. Visual Concept Creation
```
Based on the analysis, it creates a unified visual concept:
- Concept name and description
- Color strategy (when to use primary, accent, backgrounds)
- Typography system (how titles, body text, emphasis should look)
- Signature visual elements
```

### 3. Per-Slide Design
```
For each slide, specific instructions are generated:
- Purpose: What this slide aims to achieve
- Layout: Best structure for the content
- Typography: Exact styling for titles and body
- Colors: How to apply the theme colors
- Visual elements: Accent bars, shapes, icons
- Key message: The ONE thing viewers should remember
```

## 🔑 Using the Replicate API

For enhanced AI features, add your Replicate API key:

1. Get your API key from [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)
2. Enter it in the SlideStyler UI under "AI Design Director"
3. Optionally enable "Generate consistent visual concepts" for Seedream-4 imagery

### What You Get with Replicate API:
- **Meta Llama 3 70B** for intelligent design analysis
- **Seedream-4** for generating consistent visual elements
- More nuanced per-slide design recommendations

### Without API Key:
- Rule-based intelligent design system
- Professional layouts and styling
- All 20+ style themes

## 🚢 Deployment

### Deploy to Render
```bash
# Push to GitHub, then on render.com:
# New → Web Service → Connect repo → It auto-detects render.yaml
```

### Deploy to Railway
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Docker
```bash
docker build -t slidestyler .
docker run -p 8000:8000 slidestyler
```

## 🔧 API Endpoints

### Core Flow
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload a PPTX file |
| `/api/sessions/{id}/parse` | POST | Parse uploaded presentation |
| `/api/sessions/{id}/redesign` | POST | AI-powered redesign with selected style |
| `/api/sessions/{id}/preview/{n}` | GET | HTML preview of slide n |
| `/api/sessions/{id}/export` | POST | Generate PPTX |
| `/api/sessions/{id}/download` | GET | Download result |

### Redesign Options
```json
POST /api/sessions/{id}/redesign
{
  "style_id": "executive_minimal",
  "use_ai_design": true,
  "api_key": "r8_your_replicate_key",
  "generate_images": true
}
```

### Response with AI Insights
```json
{
  "status": "redesigned",
  "ai_powered": true,
  "ai_insights": {
    "presentation_type": "pitch",
    "primary_purpose": "Convince investors to fund the startup",
    "visual_mood": "energetic and confident",
    "concept_name": "Bold Momentum",
    "concept_description": "A dynamic design approach emphasizing forward movement..."
  },
  "slides": [
    {
      "slide_number": 1,
      "layout_type": "title",
      "ai_purpose": "Create strong first impression and establish brand presence"
    }
  ]
}
```

## 📁 Project Structure

```
SlideStyler/
├── backend/
│   ├── app.py                      # Flask API server
│   ├── requirements.txt
│   └── services/
│       ├── pptx_parser.py          # PowerPoint parsing
│       ├── ai_design_director.py   # 🧠 AI Design Director
│       ├── redesign_engine.py      # HTML generation with AI
│       └── pptx_exporter.py        # PPTX export
├── frontend/
│   └── src/App.js                  # React application
├── Dockerfile
└── render.yaml
```

## 🎨 The AI Designer Persona

Our AI is trained to think like the world's best PowerPoint designer:

> *"Every slide tells a story - design should amplify the message, not distract. Visual hierarchy guides the eye naturally through content. White space is not empty - it's a powerful design element. Consistency creates professionalism; intentional variation creates emphasis."*

### Design Philosophy:
- **Purpose-driven** - Every element serves the message
- **Audience-aware** - Design adapts to who's viewing
- **Emotionally intelligent** - Creates the right feelings at the right moments
- **Technically excellent** - Typography, color, and spacing are world-class

## 📝 License

MIT License - feel free to use and modify for your projects.

---

Built with ❤️ using Flask, React, and AI
