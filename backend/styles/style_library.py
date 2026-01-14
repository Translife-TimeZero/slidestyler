"""
World-Class Style Library for PowerPoint Redesign
20+ Professional Design Styles with comprehensive theming
"""

STYLE_LIBRARY = {
    # === CORPORATE & PROFESSIONAL ===
    "executive_minimal": {
        "name": "Executive Minimal",
        "description": "Clean, sophisticated design for C-suite presentations",
        "category": "Corporate",
        "preview_colors": ["#1a1a2e", "#f5f5f5", "#0077b6"],
        "theme": {
            "primary": "#0077b6",
            "primary_light": "#0096c7",
            "primary_dark": "#005f8d",
            "secondary": "#f5f5f5",
            "background": "#ffffff",
            "surface": "#fafafa",
            "text": "#1a1a2e",
            "text_muted": "#6b7280",
            "accent": "#00b4d8",
            "border": "#e5e7eb"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "42px",
            "heading_size": "28px",
            "body_size": "16px",
            "letter_spacing": "0.5px"
        },
        "layout": {
            "style": "asymmetric",
            "margins": "generous",
            "content_alignment": "left",
            "accent_position": "left-bar"
        },
        "effects": {
            "shadows": "subtle",
            "borders": "minimal",
            "gradients": False,
            "animations": "fade"
        }
    },

    "corporate_blue": {
        "name": "Corporate Blue",
        "description": "Professional blue theme for business presentations",
        "category": "Corporate",
        "preview_colors": ["#1e3a5f", "#ffffff", "#3498db"],
        "theme": {
            "primary": "#1e3a5f",
            "primary_light": "#2c5282",
            "primary_dark": "#1a365d",
            "secondary": "#f7fafc",
            "background": "#ffffff",
            "surface": "#edf2f7",
            "text": "#2d3748",
            "text_muted": "#718096",
            "accent": "#3498db",
            "border": "#e2e8f0"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "700",
            "title_size": "40px",
            "heading_size": "26px",
            "body_size": "15px",
            "letter_spacing": "0.3px"
        },
        "layout": {
            "style": "classic",
            "margins": "standard",
            "content_alignment": "left",
            "accent_position": "top-bar"
        },
        "effects": {
            "shadows": "medium",
            "borders": "subtle",
            "gradients": True,
            "animations": "slide"
        }
    },

    "dark_executive": {
        "name": "Dark Executive",
        "description": "Sophisticated dark theme for impactful presentations",
        "category": "Corporate",
        "preview_colors": ["#0f0f0f", "#ffffff", "#ffd700"],
        "theme": {
            "primary": "#ffd700",
            "primary_light": "#ffe34d",
            "primary_dark": "#ccac00",
            "secondary": "#1a1a1a",
            "background": "#0f0f0f",
            "surface": "#1f1f1f",
            "text": "#ffffff",
            "text_muted": "#a0a0a0",
            "accent": "#ffd700",
            "border": "#333333"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "44px",
            "heading_size": "30px",
            "body_size": "16px",
            "letter_spacing": "1px"
        },
        "layout": {
            "style": "centered",
            "margins": "generous",
            "content_alignment": "center",
            "accent_position": "bottom-line"
        },
        "effects": {
            "shadows": "dramatic",
            "borders": "gold-accent",
            "gradients": True,
            "animations": "fade"
        }
    },

    # === MODERN & CREATIVE ===
    "modern_gradient": {
        "name": "Modern Gradient",
        "description": "Vibrant gradient backgrounds with modern aesthetics",
        "category": "Modern",
        "preview_colors": ["#667eea", "#764ba2", "#ffffff"],
        "theme": {
            "primary": "#667eea",
            "primary_light": "#818cf8",
            "primary_dark": "#4f46e5",
            "secondary": "#764ba2",
            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "surface": "rgba(255,255,255,0.15)",
            "text": "#ffffff",
            "text_muted": "rgba(255,255,255,0.8)",
            "accent": "#f093fb",
            "border": "rgba(255,255,255,0.3)"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "700",
            "title_size": "48px",
            "heading_size": "32px",
            "body_size": "18px",
            "letter_spacing": "0.5px"
        },
        "layout": {
            "style": "bold",
            "margins": "standard",
            "content_alignment": "left",
            "accent_position": "none"
        },
        "effects": {
            "shadows": "glow",
            "borders": "glass",
            "gradients": True,
            "animations": "float"
        }
    },

    "neon_dark": {
        "name": "Neon Dark",
        "description": "Bold neon accents on dark background for tech presentations",
        "category": "Modern",
        "preview_colors": ["#0a0a0a", "#00ff88", "#ff00ff"],
        "theme": {
            "primary": "#00ff88",
            "primary_light": "#4fffaa",
            "primary_dark": "#00cc6a",
            "secondary": "#ff00ff",
            "background": "#0a0a0a",
            "surface": "#151515",
            "text": "#ffffff",
            "text_muted": "#888888",
            "accent": "#00d4ff",
            "border": "#333333"
        },
        "typography": {
            "heading_font": "Impact",
            "body_font": "Arial",
            "heading_weight": "700",
            "title_size": "52px",
            "heading_size": "34px",
            "body_size": "16px",
            "letter_spacing": "2px"
        },
        "layout": {
            "style": "asymmetric",
            "margins": "tight",
            "content_alignment": "left",
            "accent_position": "glow-border"
        },
        "effects": {
            "shadows": "neon-glow",
            "borders": "neon",
            "gradients": True,
            "animations": "pulse"
        }
    },

    "glassmorphism": {
        "name": "Glassmorphism",
        "description": "Frosted glass effect with depth and transparency",
        "category": "Modern",
        "preview_colors": ["#1a1a2e", "rgba(255,255,255,0.1)", "#a78bfa"],
        "theme": {
            "primary": "#a78bfa",
            "primary_light": "#c4b5fd",
            "primary_dark": "#8b5cf6",
            "secondary": "rgba(255,255,255,0.1)",
            "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            "surface": "rgba(255,255,255,0.08)",
            "text": "#ffffff",
            "text_muted": "rgba(255,255,255,0.7)",
            "accent": "#f472b6",
            "border": "rgba(255,255,255,0.2)"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "46px",
            "heading_size": "30px",
            "body_size": "17px",
            "letter_spacing": "0.5px"
        },
        "layout": {
            "style": "cards",
            "margins": "generous",
            "content_alignment": "center",
            "accent_position": "glass-cards"
        },
        "effects": {
            "shadows": "glass",
            "borders": "glass",
            "gradients": True,
            "animations": "float"
        }
    },

    # === STARTUP & TECH ===
    "startup_fresh": {
        "name": "Startup Fresh",
        "description": "Energetic and fresh design for startup pitches",
        "category": "Startup",
        "preview_colors": ["#ffffff", "#ff6b6b", "#4ecdc4"],
        "theme": {
            "primary": "#ff6b6b",
            "primary_light": "#ff8585",
            "primary_dark": "#ee5a5a",
            "secondary": "#4ecdc4",
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "text": "#2d3436",
            "text_muted": "#636e72",
            "accent": "#4ecdc4",
            "border": "#dfe6e9"
        },
        "typography": {
            "heading_font": "Impact",
            "body_font": "Arial",
            "heading_weight": "800",
            "title_size": "50px",
            "heading_size": "32px",
            "body_size": "17px",
            "letter_spacing": "0px"
        },
        "layout": {
            "style": "dynamic",
            "margins": "tight",
            "content_alignment": "left",
            "accent_position": "corner-shapes"
        },
        "effects": {
            "shadows": "playful",
            "borders": "rounded",
            "gradients": False,
            "animations": "bounce"
        }
    },

    "tech_minimal": {
        "name": "Tech Minimal",
        "description": "Clean tech aesthetic with monospace elements",
        "category": "Startup",
        "preview_colors": ["#fafafa", "#171717", "#6366f1"],
        "theme": {
            "primary": "#171717",
            "primary_light": "#404040",
            "primary_dark": "#0a0a0a",
            "secondary": "#f5f5f5",
            "background": "#fafafa",
            "surface": "#ffffff",
            "text": "#171717",
            "text_muted": "#737373",
            "accent": "#6366f1",
            "border": "#e5e5e5"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "44px",
            "heading_size": "28px",
            "body_size": "15px",
            "letter_spacing": "0.3px"
        },
        "layout": {
            "style": "grid",
            "margins": "standard",
            "content_alignment": "left",
            "accent_position": "underline"
        },
        "effects": {
            "shadows": "minimal",
            "borders": "thin",
            "gradients": False,
            "animations": "fade"
        }
    },

    # === CREATIVE & ARTISTIC ===
    "bold_creative": {
        "name": "Bold Creative",
        "description": "Striking bold design for creative agencies",
        "category": "Creative",
        "preview_colors": ["#ff4757", "#2f3542", "#ffa502"],
        "theme": {
            "primary": "#ff4757",
            "primary_light": "#ff6b7a",
            "primary_dark": "#e63946",
            "secondary": "#ffa502",
            "background": "#2f3542",
            "surface": "#3d4555",
            "text": "#ffffff",
            "text_muted": "#a4b0be",
            "accent": "#ffa502",
            "border": "#57606f"
        },
        "typography": {
            "heading_font": "Impact",
            "body_font": "Arial",
            "heading_weight": "900",
            "title_size": "56px",
            "heading_size": "36px",
            "body_size": "18px",
            "letter_spacing": "2px"
        },
        "layout": {
            "style": "asymmetric",
            "margins": "dynamic",
            "content_alignment": "left",
            "accent_position": "diagonal"
        },
        "effects": {
            "shadows": "bold",
            "borders": "thick",
            "gradients": False,
            "animations": "slide"
        }
    },

    "pastel_dream": {
        "name": "Pastel Dream",
        "description": "Soft pastel colors for gentle, approachable presentations",
        "category": "Creative",
        "preview_colors": ["#ffeef8", "#b8c1ec", "#f7d6e0"],
        "theme": {
            "primary": "#b8c1ec",
            "primary_light": "#c8cef5",
            "primary_dark": "#9fa8da",
            "secondary": "#f7d6e0",
            "background": "#ffeef8",
            "surface": "#ffffff",
            "text": "#5c5470",
            "text_muted": "#8a819e",
            "accent": "#f2b5d4",
            "border": "#e6dff0"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "42px",
            "heading_size": "28px",
            "body_size": "16px",
            "letter_spacing": "0.5px"
        },
        "layout": {
            "style": "soft",
            "margins": "generous",
            "content_alignment": "center",
            "accent_position": "rounded-shapes"
        },
        "effects": {
            "shadows": "soft",
            "borders": "rounded",
            "gradients": True,
            "animations": "float"
        }
    },

    "retro_vintage": {
        "name": "Retro Vintage",
        "description": "Nostalgic retro design with warm tones",
        "category": "Creative",
        "preview_colors": ["#f4e4ba", "#5a3921", "#d4a373"],
        "theme": {
            "primary": "#5a3921",
            "primary_light": "#7a5235",
            "primary_dark": "#3d2515",
            "secondary": "#d4a373",
            "background": "#f4e4ba",
            "surface": "#faf6eb",
            "text": "#3d2515",
            "text_muted": "#6b5344",
            "accent": "#bc6c25",
            "border": "#d4a373"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Times New Roman",
            "heading_weight": "700",
            "title_size": "48px",
            "heading_size": "32px",
            "body_size": "18px",
            "letter_spacing": "1px"
        },
        "layout": {
            "style": "classic",
            "margins": "generous",
            "content_alignment": "center",
            "accent_position": "ornamental"
        },
        "effects": {
            "shadows": "vintage",
            "borders": "decorative",
            "gradients": False,
            "animations": "fade"
        }
    },

    # === EDUCATIONAL & ACADEMIC ===
    "academic_classic": {
        "name": "Academic Classic",
        "description": "Traditional academic style for educational content",
        "category": "Educational",
        "preview_colors": ["#ffffff", "#1a237e", "#c62828"],
        "theme": {
            "primary": "#1a237e",
            "primary_light": "#3949ab",
            "primary_dark": "#0d1642",
            "secondary": "#f5f5f5",
            "background": "#ffffff",
            "surface": "#fafafa",
            "text": "#212121",
            "text_muted": "#757575",
            "accent": "#c62828",
            "border": "#e0e0e0"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Times New Roman",
            "heading_weight": "700",
            "title_size": "40px",
            "heading_size": "28px",
            "body_size": "16px",
            "letter_spacing": "0px"
        },
        "layout": {
            "style": "structured",
            "margins": "standard",
            "content_alignment": "left",
            "accent_position": "header-line"
        },
        "effects": {
            "shadows": "none",
            "borders": "simple",
            "gradients": False,
            "animations": "none"
        }
    },

    "science_modern": {
        "name": "Science Modern",
        "description": "Contemporary scientific presentation style",
        "category": "Educational",
        "preview_colors": ["#f0f4f8", "#0d47a1", "#00bfa5"],
        "theme": {
            "primary": "#0d47a1",
            "primary_light": "#1565c0",
            "primary_dark": "#0a3d8a",
            "secondary": "#e3f2fd",
            "background": "#f0f4f8",
            "surface": "#ffffff",
            "text": "#1a237e",
            "text_muted": "#5c6bc0",
            "accent": "#00bfa5",
            "border": "#bbdefb"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "42px",
            "heading_size": "26px",
            "body_size": "15px",
            "letter_spacing": "0.3px"
        },
        "layout": {
            "style": "grid",
            "margins": "standard",
            "content_alignment": "left",
            "accent_position": "data-highlight"
        },
        "effects": {
            "shadows": "subtle",
            "borders": "clean",
            "gradients": False,
            "animations": "fade"
        }
    },

    # === INDUSTRY SPECIFIC ===
    "healthcare_clean": {
        "name": "Healthcare Clean",
        "description": "Professional healthcare and medical presentations",
        "category": "Industry",
        "preview_colors": ["#ffffff", "#00796b", "#e0f2f1"],
        "theme": {
            "primary": "#00796b",
            "primary_light": "#26a69a",
            "primary_dark": "#004d40",
            "secondary": "#e0f2f1",
            "background": "#ffffff",
            "surface": "#f5fffe",
            "text": "#004d40",
            "text_muted": "#4db6ac",
            "accent": "#00bcd4",
            "border": "#b2dfdb"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "40px",
            "heading_size": "26px",
            "body_size": "15px",
            "letter_spacing": "0.3px"
        },
        "layout": {
            "style": "clean",
            "margins": "generous",
            "content_alignment": "left",
            "accent_position": "side-accent"
        },
        "effects": {
            "shadows": "soft",
            "borders": "rounded",
            "gradients": False,
            "animations": "fade"
        }
    },

    "finance_professional": {
        "name": "Finance Professional",
        "description": "Serious financial and banking presentations",
        "category": "Industry",
        "preview_colors": ["#1b2838", "#ffffff", "#27ae60"],
        "theme": {
            "primary": "#1b2838",
            "primary_light": "#2c3e50",
            "primary_dark": "#0f1923",
            "secondary": "#ecf0f1",
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "text": "#1b2838",
            "text_muted": "#7f8c8d",
            "accent": "#27ae60",
            "border": "#bdc3c7"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "42px",
            "heading_size": "28px",
            "body_size": "15px",
            "letter_spacing": "0.3px"
        },
        "layout": {
            "style": "structured",
            "margins": "standard",
            "content_alignment": "left",
            "accent_position": "bottom-bar"
        },
        "effects": {
            "shadows": "subtle",
            "borders": "thin",
            "gradients": False,
            "animations": "fade"
        }
    },

    "real_estate_luxury": {
        "name": "Real Estate Luxury",
        "description": "Premium real estate and property presentations",
        "category": "Industry",
        "preview_colors": ["#1a1a1a", "#d4af37", "#ffffff"],
        "theme": {
            "primary": "#d4af37",
            "primary_light": "#e5c76b",
            "primary_dark": "#b8952f",
            "secondary": "#2c2c2c",
            "background": "#1a1a1a",
            "surface": "#252525",
            "text": "#ffffff",
            "text_muted": "#b0b0b0",
            "accent": "#d4af37",
            "border": "#404040"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Arial",
            "heading_weight": "400",
            "title_size": "48px",
            "heading_size": "32px",
            "body_size": "17px",
            "letter_spacing": "3px"
        },
        "layout": {
            "style": "luxury",
            "margins": "generous",
            "content_alignment": "center",
            "accent_position": "gold-line"
        },
        "effects": {
            "shadows": "elegant",
            "borders": "gold",
            "gradients": True,
            "animations": "fade"
        }
    },

    # === NATURE & SUSTAINABILITY ===
    "eco_green": {
        "name": "Eco Green",
        "description": "Sustainable and environmental themed presentations",
        "category": "Nature",
        "preview_colors": ["#f1f8e9", "#2e7d32", "#81c784"],
        "theme": {
            "primary": "#2e7d32",
            "primary_light": "#4caf50",
            "primary_dark": "#1b5e20",
            "secondary": "#dcedc8",
            "background": "#f1f8e9",
            "surface": "#ffffff",
            "text": "#1b5e20",
            "text_muted": "#558b2f",
            "accent": "#81c784",
            "border": "#c5e1a5"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Arial",
            "heading_weight": "600",
            "title_size": "44px",
            "heading_size": "30px",
            "body_size": "16px",
            "letter_spacing": "0.5px"
        },
        "layout": {
            "style": "organic",
            "margins": "generous",
            "content_alignment": "left",
            "accent_position": "leaf-accent"
        },
        "effects": {
            "shadows": "natural",
            "borders": "organic",
            "gradients": True,
            "animations": "grow"
        }
    },

    "ocean_calm": {
        "name": "Ocean Calm",
        "description": "Serene ocean-inspired blue theme",
        "category": "Nature",
        "preview_colors": ["#e0f7fa", "#006064", "#4dd0e1"],
        "theme": {
            "primary": "#006064",
            "primary_light": "#0097a7",
            "primary_dark": "#004d40",
            "secondary": "#b2ebf2",
            "background": "#e0f7fa",
            "surface": "#ffffff",
            "text": "#006064",
            "text_muted": "#00838f",
            "accent": "#4dd0e1",
            "border": "#80deea"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Arial",
            "heading_weight": "500",
            "title_size": "44px",
            "heading_size": "28px",
            "body_size": "16px",
            "letter_spacing": "0.5px"
        },
        "layout": {
            "style": "flowing",
            "margins": "generous",
            "content_alignment": "center",
            "accent_position": "wave"
        },
        "effects": {
            "shadows": "soft",
            "borders": "flowing",
            "gradients": True,
            "animations": "wave"
        }
    },

    # === MINIMALIST ===
    "pure_white": {
        "name": "Pure White",
        "description": "Ultra-minimal white design with maximum impact",
        "category": "Minimalist",
        "preview_colors": ["#ffffff", "#000000", "#f5f5f5"],
        "theme": {
            "primary": "#000000",
            "primary_light": "#333333",
            "primary_dark": "#000000",
            "secondary": "#f5f5f5",
            "background": "#ffffff",
            "surface": "#fafafa",
            "text": "#000000",
            "text_muted": "#666666",
            "accent": "#000000",
            "border": "#eeeeee"
        },
        "typography": {
            "heading_font": "Arial",
            "body_font": "Arial",
            "heading_weight": "300",
            "title_size": "56px",
            "heading_size": "36px",
            "body_size": "18px",
            "letter_spacing": "2px"
        },
        "layout": {
            "style": "ultra-minimal",
            "margins": "extra-generous",
            "content_alignment": "left",
            "accent_position": "none"
        },
        "effects": {
            "shadows": "none",
            "borders": "none",
            "gradients": False,
            "animations": "fade"
        }
    },

    "monochrome_elegant": {
        "name": "Monochrome Elegant",
        "description": "Sophisticated black and white with gray accents",
        "category": "Minimalist",
        "preview_colors": ["#f8f8f8", "#1a1a1a", "#888888"],
        "theme": {
            "primary": "#1a1a1a",
            "primary_light": "#404040",
            "primary_dark": "#000000",
            "secondary": "#f8f8f8",
            "background": "#ffffff",
            "surface": "#f8f8f8",
            "text": "#1a1a1a",
            "text_muted": "#888888",
            "accent": "#555555",
            "border": "#e0e0e0"
        },
        "typography": {
            "heading_font": "Georgia",
            "body_font": "Arial",
            "heading_weight": "400",
            "title_size": "48px",
            "heading_size": "32px",
            "body_size": "17px",
            "letter_spacing": "1px"
        },
        "layout": {
            "style": "classic-minimal",
            "margins": "generous",
            "content_alignment": "left",
            "accent_position": "thin-line"
        },
        "effects": {
            "shadows": "subtle",
            "borders": "thin",
            "gradients": False,
            "animations": "fade"
        }
    }
}

def get_all_styles():
    """Return all available styles"""
    return STYLE_LIBRARY

def get_style_by_name(name):
    """Get a specific style by its key name"""
    return STYLE_LIBRARY.get(name)

def get_styles_by_category(category):
    """Get all styles in a specific category"""
    return {k: v for k, v in STYLE_LIBRARY.items() if v.get("category") == category}

def get_categories():
    """Get all unique categories"""
    return list(set(v.get("category") for v in STYLE_LIBRARY.values()))

def get_style_preview_data():
    """Get minimal data for style previews"""
    return [
        {
            "id": key,
            "name": value["name"],
            "description": value["description"],
            "category": value["category"],
            "preview_colors": value["preview_colors"]
        }
        for key, value in STYLE_LIBRARY.items()
    ]
