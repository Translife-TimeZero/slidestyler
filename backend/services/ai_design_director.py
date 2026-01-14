"""
AI Design Director - World-Class PowerPoint Designer
Uses AI to analyze content and provide per-slide design instructions
with consistent visual concepts across the entire presentation.
"""

import os
import json
import httpx
import asyncio
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


# The World-Class Designer Persona
DESIGNER_SYSTEM_PROMPT = """You are the world's most acclaimed PowerPoint designer, renowned for transforming ordinary presentations into visual masterpieces that captivate audiences and communicate ideas with unprecedented clarity.

Your design philosophy:
- Every slide tells a story - design should amplify the message, not distract
- Visual hierarchy guides the eye naturally through content
- White space is not empty - it's a powerful design element
- Consistency creates professionalism; intentional variation creates emphasis
- Typography is the voice of content - choose fonts that speak the right tone
- Color psychology influences perception and emotion
- Less is more - remove anything that doesn't serve the message

Your expertise includes:
- Information architecture and content flow
- Visual storytelling and narrative design
- Data visualization and infographic design
- Brand consistency and style systems
- Accessibility and readability optimization
- Modern design trends (glassmorphism, neumorphism, minimalism)

When analyzing presentations, you:
1. First understand the overall PURPOSE and AUDIENCE
2. Identify the NARRATIVE ARC across all slides
3. Determine the EMOTIONAL JOURNEY you want viewers to experience
4. Create a VISUAL CONCEPT that ties everything together
5. Design each slide to serve its specific role in the story

You communicate design decisions clearly, explaining not just WHAT to do but WHY it enhances communication."""


@dataclass
class SlideDesignInstructions:
    """Design instructions for a single slide"""
    slide_number: int
    purpose: str  # What this slide aims to achieve
    emotional_tone: str  # The feeling it should evoke
    layout_type: str  # Recommended layout
    typography: Dict[str, Any]  # Font sizes, weights, styles
    color_emphasis: Dict[str, str]  # Which colors to emphasize where
    visual_elements: List[str]  # Suggested visual elements
    spacing_notes: str  # Guidance on spacing and breathing room
    key_message: str  # The one thing viewers should remember
    design_rationale: str  # Why these choices work


class AIDesignDirector:
    """
    AI-powered design director that analyzes presentations
    and provides world-class design instructions per slide.
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "replicate"):
        # API key from parameter, environment variable, or will use fallback
        self.api_key = api_key or os.environ.get("REPLICATE_API_TOKEN")
        self.provider = provider
        self.replicate_base_url = "https://api.replicate.com/v1"
        self.visual_concept = None
        self.presentation_analysis = None
    
    async def analyze_and_design(
        self, 
        slides_data: List[Dict],
        style_theme: Dict,
        generate_images: bool = False
    ) -> Dict:
        """
        Main entry point: Analyze entire presentation and generate
        per-slide design instructions with consistent visual concept.
        """
        # Step 1: Analyze the entire presentation
        self.presentation_analysis = await self._analyze_presentation_holistically(slides_data)
        
        # Step 2: Generate a consistent visual concept
        self.visual_concept = await self._generate_visual_concept(
            self.presentation_analysis, 
            style_theme
        )
        
        # Step 3: Generate per-slide design instructions
        slide_instructions = []
        for i, slide in enumerate(slides_data):
            instructions = await self._design_single_slide(
                slide=slide,
                slide_index=i,
                total_slides=len(slides_data),
                presentation_context=self.presentation_analysis,
                visual_concept=self.visual_concept,
                style_theme=style_theme
            )
            slide_instructions.append(instructions)
        
        # Step 4: Optionally generate consistent imagery using Seedream-4
        generated_images = []
        if generate_images and self.api_key:
            generated_images = await self._generate_consistent_visuals(
                self.visual_concept,
                slides_data
            )
        
        return {
            "presentation_analysis": self.presentation_analysis,
            "visual_concept": self.visual_concept,
            "slide_instructions": slide_instructions,
            "generated_images": generated_images
        }
    
    async def _analyze_presentation_holistically(self, slides_data: List[Dict]) -> Dict:
        """Analyze the entire presentation to understand its purpose and flow."""
        
        # Prepare slide summaries for analysis
        slides_summary = []
        for i, slide in enumerate(slides_data):
            text_content = slide.get("text_content", [])
            texts = [t.get("text", "") for t in text_content if t.get("text")]
            slides_summary.append({
                "slide_number": i + 1,
                "layout_type": slide.get("layout_type", "content"),
                "has_chart": slide.get("has_chart", False),
                "has_table": slide.get("has_table", False),
                "has_images": len(slide.get("images", [])) > 0,
                "content_preview": texts[:3] if texts else []
            })
        
        prompt = f"""{DESIGNER_SYSTEM_PROMPT}

I need you to analyze this presentation holistically and understand its strategic purpose.

PRESENTATION STRUCTURE:
{json.dumps(slides_summary, indent=2)}

Analyze this presentation and provide a JSON response with:
{{
    "presentation_type": "pitch|report|educational|proposal|keynote|training|other",
    "primary_purpose": "The main goal this presentation aims to achieve",
    "target_audience": "Who this presentation is designed for",
    "narrative_arc": "The story structure (problem-solution, chronological, comparison, etc.)",
    "emotional_journey": ["emotion for intro", "emotion for middle", "emotion for conclusion"],
    "key_themes": ["theme1", "theme2", "theme3"],
    "visual_mood": "The overall visual feeling (professional, energetic, calm, bold, etc.)",
    "pacing_assessment": "How information density varies across slides",
    "critical_slides": [slide_numbers that need extra design attention],
    "design_challenges": ["challenge1", "challenge2"],
    "recommended_approach": "Overall design strategy recommendation"
}}

Respond ONLY with valid JSON."""

        return await self._call_ai(prompt)
    
    async def _generate_visual_concept(self, analysis: Dict, style_theme: Dict) -> Dict:
        """Generate a cohesive visual concept for the entire presentation."""
        
        prompt = f"""{DESIGNER_SYSTEM_PROMPT}

Based on this presentation analysis and style theme, create a unified visual concept.

PRESENTATION ANALYSIS:
{json.dumps(analysis, indent=2)}

STYLE THEME:
- Primary Color: {style_theme.get('primary', '#0077b6')}
- Background: {style_theme.get('background', '#ffffff')}
- Text Color: {style_theme.get('text', '#1a1a2e')}
- Accent Color: {style_theme.get('accent', '#00b4d8')}

Create a visual concept that will ensure consistency and impact. Respond with JSON:
{{
    "concept_name": "A memorable name for this visual approach",
    "concept_description": "2-3 sentence description of the visual direction",
    "image_style_prompt": "A detailed prompt for generating consistent imagery (for AI image generation)",
    "visual_motif": "A recurring visual element or pattern",
    "color_strategy": {{
        "primary_usage": "How to use primary color",
        "accent_usage": "When and where to use accent color",
        "background_treatment": "Background approach (solid, gradient, texture)"
    }},
    "typography_system": {{
        "title_treatment": "How titles should be styled",
        "body_treatment": "How body text should be treated",
        "emphasis_method": "How to emphasize key points"
    }},
    "spacing_philosophy": "Overall approach to white space",
    "transition_style": "How slides should flow visually",
    "signature_elements": ["element1", "element2"]
}}

Respond ONLY with valid JSON."""

        return await self._call_ai(prompt)
    
    async def _design_single_slide(
        self,
        slide: Dict,
        slide_index: int,
        total_slides: int,
        presentation_context: Dict,
        visual_concept: Dict,
        style_theme: Dict
    ) -> Dict:
        """Generate specific design instructions for a single slide."""
        
        text_content = slide.get("text_content", [])
        slide_position = "opening" if slide_index == 0 else "closing" if slide_index == total_slides - 1 else "middle"
        
        # Determine slide role
        title = ""
        body_texts = []
        for item in text_content:
            item_type = item.get("type", "body")
            text = item.get("text", "").strip()
            if item_type in ["title", "ctrTitle", "TITLE", "CENTER_TITLE"]:
                title = text
            elif text:
                body_texts.append(text)
        
        prompt = f"""{DESIGNER_SYSTEM_PROMPT}

Design slide {slide_index + 1} of {total_slides} to perfectly serve its role in the presentation.

PRESENTATION CONTEXT:
- Type: {presentation_context.get('presentation_type', 'general')}
- Purpose: {presentation_context.get('primary_purpose', 'inform')}
- Audience: {presentation_context.get('target_audience', 'general')}
- Visual Mood: {presentation_context.get('visual_mood', 'professional')}

VISUAL CONCEPT:
{json.dumps(visual_concept, indent=2)}

SLIDE CONTENT:
- Position: {slide_position} (slide {slide_index + 1} of {total_slides})
- Title: "{title}"
- Body Content: {json.dumps(body_texts[:5], indent=2)}
- Has Chart: {slide.get('has_chart', False)}
- Has Table: {slide.get('has_table', False)}
- Has Images: {len(slide.get('images', [])) > 0}
- Original Layout: {slide.get('layout_type', 'content')}

STYLE THEME COLORS:
- Primary: {style_theme.get('primary', '#0077b6')}
- Background: {style_theme.get('background', '#ffffff')}
- Text: {style_theme.get('text', '#1a1a2e')}
- Accent: {style_theme.get('accent', '#00b4d8')}

As a world-class designer, provide specific design instructions for this slide:
{{
    "slide_number": {slide_index + 1},
    "slide_role": "What role this slide plays in the narrative",
    "purpose": "The specific goal of this slide",
    "emotional_tone": "The feeling this slide should evoke",
    "key_message": "The ONE thing viewers should take away",
    
    "layout": {{
        "type": "title|content|two_column|stats|image_content|chart|closing|section_break",
        "content_alignment": "left|center|right",
        "visual_weight": "top|center|bottom - where the visual focus should be"
    }},
    
    "typography": {{
        "title_size": "large|medium|small based on content",
        "title_weight": "bold|semibold|normal",
        "title_color": "primary|text|accent",
        "body_size": "standard|small for dense content",
        "body_emphasis": ["words or phrases to emphasize"],
        "hierarchy_levels": number of visual hierarchy levels needed
    }},
    
    "color_application": {{
        "background": "solid|gradient|accent_block",
        "title_color_override": null or specific hex if different from theme,
        "accent_elements": ["where to apply accent color"],
        "contrast_strategy": "high|medium|subtle"
    }},
    
    "visual_elements": {{
        "accent_bar": "none|left|top|bottom",
        "decorative_shapes": true|false,
        "icons_recommended": ["icon suggestions if applicable"],
        "image_style": "if images, what style they should have"
    }},
    
    "spacing": {{
        "content_density": "sparse|balanced|dense",
        "padding_style": "generous|standard|tight",
        "element_spacing": "relaxed|normal|compact"
    }},
    
    "special_instructions": "Any specific design notes for this slide",
    "design_rationale": "Brief explanation of why these choices serve the message"
}}

Respond ONLY with valid JSON."""

        result = await self._call_ai(prompt)
        result["slide_number"] = slide_index + 1
        return result
    
    async def _generate_consistent_visuals(
        self, 
        visual_concept: Dict,
        slides_data: List[Dict]
    ) -> List[Dict]:
        """
        Generate consistent visual elements using Seedream-4.
        Creates a cohesive visual language across all slides.
        """
        if not self.api_key:
            return []
        
        generated_images = []
        
        # Create the base style prompt from visual concept
        base_style = visual_concept.get("image_style_prompt", "")
        concept_name = visual_concept.get("concept_name", "Professional")
        visual_motif = visual_concept.get("visual_motif", "geometric shapes")
        
        # Generate a hero/concept image for the presentation
        hero_prompt = f"""Create a sophisticated, abstract visual for a professional presentation.
Style: {concept_name}
Visual motif: {visual_motif}
{base_style}
The image should be:
- Abstract and not literal
- Suitable as a subtle background or accent
- Professional and modern
- Using smooth gradients and clean lines
- High quality, 4K resolution aesthetic"""

        try:
            hero_image = await self._generate_image_seedream(
                prompt=hero_prompt,
                purpose="hero_concept"
            )
            if hero_image:
                generated_images.append({
                    "type": "hero_concept",
                    "image_url": hero_image,
                    "purpose": "Main visual concept for presentation"
                })
        except Exception as e:
            print(f"Hero image generation failed: {e}")
        
        # Generate slide-specific accents for key slides
        for i, slide in enumerate(slides_data):
            # Only generate for important slides (first, last, section breaks)
            if i == 0 or i == len(slides_data) - 1 or slide.get("layout_type") == "section_break":
                text_content = slide.get("text_content", [])
                title = next((t.get("text", "") for t in text_content 
                             if t.get("type") in ["title", "ctrTitle"]), "")
                
                slide_prompt = f"""Create an abstract visual accent for a presentation slide.
Theme: {concept_name}
Slide topic: {title if title else 'Professional content'}
Visual motif: {visual_motif}
{base_style}
Requirements:
- Abstract and symbolic, not literal
- Works as a corner accent or subtle background
- Complements text content, doesn't compete
- Professional, modern aesthetic
- Clean, minimal design"""

                try:
                    slide_image = await self._generate_image_seedream(
                        prompt=slide_prompt,
                        purpose=f"slide_{i+1}_accent"
                    )
                    if slide_image:
                        generated_images.append({
                            "type": "slide_accent",
                            "slide_number": i + 1,
                            "image_url": slide_image,
                            "purpose": f"Visual accent for slide {i+1}"
                        })
                except Exception as e:
                    print(f"Slide {i+1} image generation failed: {e}")
        
        return generated_images
    
    async def _generate_image_seedream(self, prompt: str, purpose: str) -> Optional[str]:
        """Generate an image using Replicate's Seedream-4 model."""
        
        url = f"{self.replicate_base_url}/models/bytedance/seedream-4/predictions"
        
        payload = {
            "input": {
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "16:9",
                "output_format": "webp",
                "output_quality": 90,
                "negative_prompt": "text, words, letters, watermark, logo, low quality, blurry, distorted"
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Start prediction
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Prefer": "wait"  # Wait for result
                    }
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    
                    # If we got the result directly
                    if data.get("status") == "succeeded":
                        output = data.get("output", [])
                        if output:
                            return output[0] if isinstance(output, list) else output
                    
                    # If we need to poll
                    elif data.get("status") in ["starting", "processing"]:
                        prediction_url = data.get("urls", {}).get("get")
                        if prediction_url:
                            # Poll for result
                            for _ in range(60):  # Max 2 minutes
                                await asyncio.sleep(2)
                                poll_response = await client.get(
                                    prediction_url,
                                    headers={"Authorization": f"Bearer {self.api_key}"}
                                )
                                poll_data = poll_response.json()
                                
                                if poll_data.get("status") == "succeeded":
                                    output = poll_data.get("output", [])
                                    if output:
                                        return output[0] if isinstance(output, list) else output
                                    break
                                elif poll_data.get("status") == "failed":
                                    print(f"Image generation failed: {poll_data.get('error')}")
                                    break
                    
                    return None
                else:
                    print(f"Seedream API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"Image generation error: {e}")
            return None
    
    async def _call_ai(self, prompt: str) -> Dict:
        """Call AI model for text analysis (using Replicate or fallback)."""
        
        if not self.api_key:
            return self._get_intelligent_fallback(prompt)
        
        # Try using a text model on Replicate
        try:
            url = f"{self.replicate_base_url}/models/meta/meta-llama-3-70b-instruct/predictions"
            
            payload = {
                "input": {
                    "prompt": prompt,
                    "max_tokens": 2000,
                    "temperature": 0.3,
                    "system_prompt": DESIGNER_SYSTEM_PROMPT
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Prefer": "wait"
                    }
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    
                    # Handle different response formats
                    output = data.get("output", "")
                    if isinstance(output, list):
                        output = "".join(output)
                    
                    # Parse JSON from response
                    output = output.strip()
                    if "```json" in output:
                        output = output.split("```json")[1].split("```")[0]
                    elif "```" in output:
                        output = output.split("```")[1].split("```")[0]
                    
                    return json.loads(output.strip())
                    
        except Exception as e:
            print(f"AI call failed: {e}")
        
        return self._get_intelligent_fallback(prompt)
    
    def _get_intelligent_fallback(self, prompt: str) -> Dict:
        """Provide intelligent fallback responses when AI is unavailable."""
        
        # Detect what kind of response is needed
        if "presentation_type" in prompt:
            return {
                "presentation_type": "professional",
                "primary_purpose": "Communicate key information effectively",
                "target_audience": "Business professionals",
                "narrative_arc": "Introduction → Key Points → Conclusion",
                "emotional_journey": ["curiosity", "engagement", "confidence"],
                "key_themes": ["clarity", "impact", "professionalism"],
                "visual_mood": "modern professional",
                "pacing_assessment": "balanced",
                "critical_slides": [1],
                "design_challenges": ["content density", "visual consistency"],
                "recommended_approach": "Clean, modern design with clear hierarchy"
            }
        
        elif "concept_name" in prompt:
            return {
                "concept_name": "Modern Professional",
                "concept_description": "A sophisticated, clean design approach that emphasizes clarity and professionalism while maintaining visual interest through subtle accents and thoughtful typography.",
                "image_style_prompt": "Abstract geometric shapes, soft gradients, professional aesthetic, modern minimalist, clean lines, subtle depth",
                "visual_motif": "Subtle geometric accents",
                "color_strategy": {
                    "primary_usage": "Titles and key emphasis points",
                    "accent_usage": "Decorative elements and highlights",
                    "background_treatment": "Clean solid with subtle texture"
                },
                "typography_system": {
                    "title_treatment": "Bold, clear, with ample breathing room",
                    "body_treatment": "Clean and readable with good line spacing",
                    "emphasis_method": "Color accent and weight variation"
                },
                "spacing_philosophy": "Generous white space to let content breathe",
                "transition_style": "Smooth, consistent visual flow",
                "signature_elements": ["accent bar", "clean typography"]
            }
        
        elif "slide_role" in prompt:
            return {
                "slide_number": 1,
                "slide_role": "Content delivery",
                "purpose": "Communicate information clearly",
                "emotional_tone": "professional",
                "key_message": "Key information presented clearly",
                "layout": {
                    "type": "content",
                    "content_alignment": "left",
                    "visual_weight": "top"
                },
                "typography": {
                    "title_size": "medium",
                    "title_weight": "bold",
                    "title_color": "primary",
                    "body_size": "standard",
                    "body_emphasis": [],
                    "hierarchy_levels": 2
                },
                "color_application": {
                    "background": "solid",
                    "title_color_override": None,
                    "accent_elements": ["title underline"],
                    "contrast_strategy": "high"
                },
                "visual_elements": {
                    "accent_bar": "left",
                    "decorative_shapes": False,
                    "icons_recommended": [],
                    "image_style": None
                },
                "spacing": {
                    "content_density": "balanced",
                    "padding_style": "generous",
                    "element_spacing": "normal"
                },
                "special_instructions": "Focus on readability and clear hierarchy",
                "design_rationale": "Clean design ensures message clarity"
            }
        
        return {"error": "Fallback response", "status": "using defaults"}


async def get_ai_design_instructions(
    slides_data: List[Dict],
    style_theme: Dict,
    api_key: Optional[str] = None,
    generate_images: bool = False
) -> Dict:
    """Convenience function to get AI design instructions."""
    director = AIDesignDirector(api_key=api_key)
    return await director.analyze_and_design(
        slides_data=slides_data,
        style_theme=style_theme,
        generate_images=generate_images
    )
