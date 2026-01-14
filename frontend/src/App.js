import React, { useState, useCallback } from 'react';
import { Upload, Wand2, Download, Sparkles, ChevronRight, Check, Palette, Layout, Zap, Eye, RefreshCw, Brain, Image, Lightbulb } from 'lucide-react';

/* eslint-disable no-unused-vars */

// Styles data embedded for standalone use
const STYLES_DATA = [
  { id: "executive_minimal", name: "Executive Minimal", description: "Clean, sophisticated design for C-suite presentations", category: "Corporate", preview_colors: ["#1a1a2e", "#f5f5f5", "#0077b6"] },
  { id: "corporate_blue", name: "Corporate Blue", description: "Professional blue theme for business presentations", category: "Corporate", preview_colors: ["#1e3a5f", "#ffffff", "#3498db"] },
  { id: "dark_executive", name: "Dark Executive", description: "Sophisticated dark theme for impactful presentations", category: "Corporate", preview_colors: ["#0f0f0f", "#ffffff", "#ffd700"] },
  { id: "modern_gradient", name: "Modern Gradient", description: "Vibrant gradient backgrounds with modern aesthetics", category: "Modern", preview_colors: ["#667eea", "#764ba2", "#ffffff"] },
  { id: "neon_dark", name: "Neon Dark", description: "Bold neon accents on dark background for tech presentations", category: "Modern", preview_colors: ["#0a0a0a", "#00ff88", "#ff00ff"] },
  { id: "glassmorphism", name: "Glassmorphism", description: "Frosted glass effect with depth and transparency", category: "Modern", preview_colors: ["#1a1a2e", "rgba(255,255,255,0.1)", "#a78bfa"] },
  { id: "startup_fresh", name: "Startup Fresh", description: "Energetic and fresh design for startup pitches", category: "Startup", preview_colors: ["#ffffff", "#ff6b6b", "#4ecdc4"] },
  { id: "tech_minimal", name: "Tech Minimal", description: "Clean tech aesthetic with monospace elements", category: "Startup", preview_colors: ["#fafafa", "#171717", "#6366f1"] },
  { id: "bold_creative", name: "Bold Creative", description: "Striking bold design for creative agencies", category: "Creative", preview_colors: ["#ff4757", "#2f3542", "#ffa502"] },
  { id: "pastel_dream", name: "Pastel Dream", description: "Soft pastel colors for gentle, approachable presentations", category: "Creative", preview_colors: ["#ffeef8", "#b8c1ec", "#f7d6e0"] },
  { id: "retro_vintage", name: "Retro Vintage", description: "Nostalgic retro design with warm tones", category: "Creative", preview_colors: ["#f4e4ba", "#5a3921", "#d4a373"] },
  { id: "academic_classic", name: "Academic Classic", description: "Traditional academic style for educational content", category: "Educational", preview_colors: ["#ffffff", "#1a237e", "#c62828"] },
  { id: "science_modern", name: "Science Modern", description: "Contemporary scientific presentation style", category: "Educational", preview_colors: ["#f0f4f8", "#0d47a1", "#00bfa5"] },
  { id: "healthcare_clean", name: "Healthcare Clean", description: "Professional healthcare and medical presentations", category: "Industry", preview_colors: ["#ffffff", "#00796b", "#e0f2f1"] },
  { id: "finance_professional", name: "Finance Professional", description: "Serious financial and banking presentations", category: "Industry", preview_colors: ["#1b2838", "#ffffff", "#27ae60"] },
  { id: "real_estate_luxury", name: "Real Estate Luxury", description: "Premium real estate and property presentations", category: "Industry", preview_colors: ["#1a1a1a", "#d4af37", "#ffffff"] },
  { id: "eco_green", name: "Eco Green", description: "Sustainable and environmental themed presentations", category: "Nature", preview_colors: ["#f1f8e9", "#2e7d32", "#81c784"] },
  { id: "ocean_calm", name: "Ocean Calm", description: "Serene ocean-inspired blue theme", category: "Nature", preview_colors: ["#e0f7fa", "#006064", "#4dd0e1"] },
  { id: "pure_white", name: "Pure White", description: "Ultra-minimal white design with maximum impact", category: "Minimalist", preview_colors: ["#ffffff", "#000000", "#f5f5f5"] },
  { id: "monochrome_elegant", name: "Monochrome Elegant", description: "Sophisticated black and white with gray accents", category: "Minimalist", preview_colors: ["#f8f8f8", "#1a1a1a", "#888888"] }
];

const CATEGORIES = ["All", "Corporate", "Modern", "Startup", "Creative", "Educational", "Industry", "Nature", "Minimalist"];

// API Configuration - auto-detect environment
const API_BASE = process.env.REACT_APP_API_URL || (
  window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api' 
    : `${window.location.origin}/api`
);

function App() {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [selectedStyle, setSelectedStyle] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('');
  const [previewHtml, setPreviewHtml] = useState(null);
  const [currentPreviewSlide, setCurrentPreviewSlide] = useState(1);
  const [error, setError] = useState(null);
  const [totalSlides, setTotalSlides] = useState(0);
  
  // AI Design Features (API key is now built-in)
  const [useAiDesign, setUseAiDesign] = useState(true);
  const [generateImages, setGenerateImages] = useState(false);
  const [aiInsights, setAiInsights] = useState(null);
  const [generatedImages, setGeneratedImages] = useState([]);

  // File Upload Handler
  const handleFileUpload = useCallback(async (e) => {
    const uploadedFile = e.target.files?.[0];
    if (!uploadedFile) return;

    if (!uploadedFile.name.endsWith('.pptx')) {
      setError('Please upload a .pptx file');
      return;
    }

    setFile(uploadedFile);
    setError(null);
    setIsProcessing(true);
    setProcessingStatus('Uploading presentation...');

    try {
      // Upload file
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const uploadRes = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!uploadRes.ok) {
        const errData = await uploadRes.json();
        throw new Error(errData.error || 'Upload failed');
      }
      const uploadData = await uploadRes.json();
      setSessionId(uploadData.session_id);
      setProcessingStatus('Analyzing slides...');

      // Parse presentation
      const parseRes = await fetch(`${API_BASE}/sessions/${uploadData.session_id}/parse`, {
        method: 'POST'
      });

      if (!parseRes.ok) {
        const errData = await parseRes.json();
        throw new Error(errData.error || 'Parsing failed');
      }
      const parseData = await parseRes.json();
      setParsedData(parseData);
      setTotalSlides(parseData.slide_count || parseData.slides_summary?.length || 0);

      setStep(2);
    } catch (err) {
      setError(err.message || 'Failed to process file');
    } finally {
      setIsProcessing(false);
      setProcessingStatus('');
    }
  }, []);

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer?.files?.[0];
    if (droppedFile) {
      const syntheticEvent = { target: { files: [droppedFile] } };
      handleFileUpload(syntheticEvent);
    }
  }, [handleFileUpload]);

  // Style Selection Handler
  const handleStyleSelect = (styleId) => {
    setSelectedStyle(styleId);
  };

  // Redesign Handler with AI Design Director
  const handleRedesign = async () => {
    if (!selectedStyle || !sessionId) return;

    setIsProcessing(true);
    setError(null);
    setAiInsights(null);
    setGeneratedImages([]);

    try {
      // Update status based on AI usage
      if (useAiDesign) {
        setProcessingStatus('🧠 AI Design Director analyzing your content...');
        await new Promise(r => setTimeout(r, 500));
        setProcessingStatus('🎨 Creating world-class design for each slide...');
      } else {
        setProcessingStatus('Redesigning slides...');
      }

      // Redesign with AI (API key is built-in)
      const redesignRes = await fetch(`${API_BASE}/sessions/${sessionId}/redesign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          style_id: selectedStyle,
          use_ai_design: useAiDesign,
          generate_images: generateImages
        })
      });

      if (!redesignRes.ok) {
        const errData = await redesignRes.json();
        throw new Error(errData.error || 'Redesign failed');
      }

      const redesignData = await redesignRes.json();
      setTotalSlides(redesignData.slides_count || totalSlides);
      
      // Store AI insights if available
      if (redesignData.ai_insights) {
        setAiInsights(redesignData.ai_insights);
      }
      
      // Store generated images if any
      if (redesignData.generated_images) {
        setGeneratedImages(redesignData.generated_images);
      }

      setProcessingStatus('Loading preview...');

      // Get preview of first slide
      const previewRes = await fetch(`${API_BASE}/sessions/${sessionId}/preview/1`);
      if (previewRes.ok) {
        const html = await previewRes.text();
        setPreviewHtml(html);
        setCurrentPreviewSlide(1);
      }

      setStep(3);
    } catch (err) {
      setError(err.message || 'Redesign failed');
    } finally {
      setIsProcessing(false);
      setProcessingStatus('');
    }
  };

  // Export Handler
  const handleExport = async () => {
    setIsProcessing(true);
    setProcessingStatus('Generating PowerPoint file...');
    setError(null);
    try {
      const exportRes = await fetch(`${API_BASE}/sessions/${sessionId}/export`, { method: 'POST' });
      if (!exportRes.ok) {
        const errData = await exportRes.json();
        throw new Error(errData.error || 'Export failed');
      }
      
      window.open(`${API_BASE}/sessions/${sessionId}/download`, '_blank');
      setStep(4);
    } catch (err) {
      setError(err.message || 'Export failed');
    } finally {
      setIsProcessing(false);
      setProcessingStatus('');
    }
  };

  // Preview slide navigation
  const navigatePreview = async (slideNum) => {
    try {
      const res = await fetch(`${API_BASE}/sessions/${sessionId}/preview/${slideNum}`);
      if (res.ok) {
        const html = await res.text();
        setPreviewHtml(html);
        setCurrentPreviewSlide(slideNum);
      }
    } catch (err) {
      console.error('Preview navigation failed');
    }
  };

  // Reset to start over
  const handleReset = () => {
    setStep(1);
    setFile(null);
    setSessionId(null);
    setParsedData(null);
    setSelectedStyle(null);
    setPreviewHtml(null);
    setCurrentPreviewSlide(1);
    setError(null);
    setTotalSlides(0);
    setAiInsights(null);
    setGeneratedImages([]);
  };

  const filteredStyles = selectedCategory === "All"
    ? STYLES_DATA
    : STYLES_DATA.filter(s => s.category === selectedCategory);

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.logo}>
          <Sparkles size={32} color="#a78bfa" />
          <span style={styles.logoText}>SlideStyler</span>
        </div>
        <p style={styles.tagline}>AI-Powered World-Class PowerPoint Design</p>
      </header>

      {/* Progress Steps */}
      <div style={styles.progressContainer}>
        {[
          { num: 1, label: "Upload", icon: Upload },
          { num: 2, label: "Style", icon: Palette },
          { num: 3, label: "Preview", icon: Eye },
          { num: 4, label: "Export", icon: Download }
        ].map((s, i) => (
          <React.Fragment key={s.num}>
            <div style={{
              ...styles.progressStep,
              ...(step >= s.num ? styles.progressStepActive : {})
            }}>
              <div style={{
                ...styles.progressIcon,
                ...(step >= s.num ? styles.progressIconActive : {})
              }}>
                {step > s.num ? <Check size={20} /> : <s.icon size={20} />}
              </div>
              <span style={styles.progressLabel}>{s.label}</span>
            </div>
            {i < 3 && <ChevronRight size={20} color="#4a4a6a" />}
          </React.Fragment>
        ))}
      </div>

      {/* Error Display */}
      {error && (
        <div style={styles.error}>
          {error}
          <button onClick={() => setError(null)} style={styles.errorClose}>×</button>
        </div>
      )}

      {/* Main Content */}
      <main style={styles.main}>
        {/* Step 1: Upload */}
        {step === 1 && (
          <div style={styles.uploadSection}>
            <div 
              style={styles.uploadBox}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pptx"
                onChange={handleFileUpload}
                style={styles.fileInput}
                id="file-upload"
                disabled={isProcessing}
              />
              <label htmlFor="file-upload" style={styles.uploadLabel}>
                {isProcessing ? (
                  <>
                    <div style={styles.spinner}></div>
                    <span>{processingStatus || 'Processing...'}</span>
                  </>
                ) : (
                  <>
                    <Upload size={48} color="#a78bfa" />
                    <span style={styles.uploadText}>Drop your PowerPoint here</span>
                    <span style={styles.uploadSubtext}>or click to browse (.pptx files)</span>
                  </>
                )}
              </label>
            </div>

            {/* AI Design Settings */}
            <div style={styles.aiSettings}>
              <h3 style={styles.aiSettingsTitle}>
                <Brain size={20} /> AI Design Director
              </h3>
              <p style={styles.aiSettingsDescription}>
                Powered by Llama 3 & Seedream-4. Our AI acts as the world's top PowerPoint designer, analyzing each slide and providing tailored design instructions.
              </p>
              
              <div style={styles.aiFeatures}>
                <div style={styles.aiFeature}>
                  <Zap size={16} color="#10b981" />
                  <span>Per-slide intelligent design</span>
                </div>
                <div style={styles.aiFeature}>
                  <Lightbulb size={16} color="#fbbf24" />
                  <span>Content-aware layouts</span>
                </div>
                <div style={styles.aiFeature}>
                  <Palette size={16} color="#a78bfa" />
                  <span>Consistent visual concepts</span>
                </div>
              </div>

              <div style={styles.aiToggle}>
                <label style={styles.toggleLabel}>
                  <input
                    type="checkbox"
                    checked={useAiDesign}
                    onChange={(e) => setUseAiDesign(e.target.checked)}
                    style={styles.checkbox}
                  />
                  <span style={styles.toggleText}>Enable AI-powered design (recommended)</span>
                </label>
              </div>

              {useAiDesign && (
                <label style={{...styles.toggleLabel, marginTop: 8}}>
                  <input
                    type="checkbox"
                    checked={generateImages}
                    onChange={(e) => setGenerateImages(e.target.checked)}
                    style={styles.checkbox}
                  />
                  <Image size={14} style={{marginRight: 8}} />
                  <span style={styles.toggleText}>Generate visual concepts with Seedream-4</span>
                </label>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Style Selection */}
        {step === 2 && (
          <div style={styles.styleSection}>
            <div style={styles.styleSectionHeader}>
              <h2 style={styles.sectionTitle}>Choose Your Design Style</h2>
              <div style={styles.headerRight}>
                <p style={styles.slideCount}>
                  {totalSlides} slides • {useAiDesign ? '🧠 AI Design' : 'Standard'}
                </p>
              </div>
            </div>

            {/* Category Filter */}
            <div style={styles.categoryFilter}>
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  style={{
                    ...styles.categoryBtn,
                    ...(selectedCategory === cat ? styles.categoryBtnActive : {})
                  }}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Style Grid */}
            <div style={styles.styleGrid}>
              {filteredStyles.map(style => (
                <div
                  key={style.id}
                  onClick={() => handleStyleSelect(style.id)}
                  style={{
                    ...styles.styleCard,
                    ...(selectedStyle === style.id ? styles.styleCardSelected : {})
                  }}
                >
                  {/* Color Preview */}
                  <div style={styles.colorPreview}>
                    {style.preview_colors.map((color, i) => (
                      <div
                        key={i}
                        style={{
                          ...styles.colorSwatch,
                          backgroundColor: color,
                          width: i === 0 ? '50%' : '25%'
                        }}
                      />
                    ))}
                  </div>
                  <div style={styles.styleInfo}>
                    <h3 style={styles.styleName}>{style.name}</h3>
                    <p style={styles.styleDesc}>{style.description}</p>
                    <span style={styles.styleCategory}>{style.category}</span>
                  </div>
                  {selectedStyle === style.id && (
                    <div style={styles.selectedBadge}>
                      <Check size={16} />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Redesign Button */}
            <button
              onClick={handleRedesign}
              disabled={!selectedStyle || isProcessing}
              style={{
                ...styles.primaryBtn,
                ...((!selectedStyle || isProcessing) ? styles.primaryBtnDisabled : {})
              }}
            >
              {isProcessing ? (
                <>
                  <div style={styles.spinnerSmall}></div>
                  {processingStatus || 'Redesigning...'}
                </>
              ) : (
                <>
                  <Wand2 size={20} />
                  {useAiDesign ? 'AI-Powered Redesign' : 'Redesign Presentation'}
                </>
              )}
            </button>
          </div>
        )}

        {/* Step 3: Preview */}
        {step === 3 && (
          <div style={styles.previewSection}>
            <div style={styles.previewHeader}>
              <h2 style={styles.sectionTitle}>Preview Your Redesigned Presentation</h2>
              {aiInsights && (
                <div style={styles.aiInsightsBadge}>
                  <Brain size={14} />
                  <span>AI-Designed</span>
                </div>
              )}
            </div>

            {/* AI Insights Panel */}
            {aiInsights && (
              <div style={styles.aiInsightsPanel}>
                <div style={styles.insightHeader}>
                  <Lightbulb size={18} color="#fbbf24" />
                  <span>AI Design Insights</span>
                </div>
                <div style={styles.insightContent}>
                  {aiInsights.concept_name && (
                    <div style={styles.insightItem}>
                      <strong>Visual Concept:</strong> {aiInsights.concept_name}
                    </div>
                  )}
                  {aiInsights.presentation_type && (
                    <div style={styles.insightItem}>
                      <strong>Type:</strong> {aiInsights.presentation_type}
                    </div>
                  )}
                  {aiInsights.primary_purpose && (
                    <div style={styles.insightItem}>
                      <strong>Purpose:</strong> {aiInsights.primary_purpose}
                    </div>
                  )}
                  {aiInsights.concept_description && (
                    <div style={styles.insightDescription}>
                      {aiInsights.concept_description}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Preview Frame */}
            <div style={styles.previewContainer}>
              {previewHtml ? (
                <iframe
                  srcDoc={previewHtml}
                  style={styles.previewFrame}
                  title="Slide Preview"
                  sandbox="allow-same-origin"
                />
              ) : (
                <div style={styles.previewPlaceholder}>
                  <Layout size={48} color="#4a4a6a" />
                  <p>Preview not available</p>
                </div>
              )}
            </div>

            {/* Slide Navigation */}
            <div style={styles.slideNav}>
              {Array.from({ length: totalSlides }, (_, i) => (
                <button
                  key={i}
                  onClick={() => navigatePreview(i + 1)}
                  style={{
                    ...styles.slideNavBtn,
                    ...(currentPreviewSlide === i + 1 ? styles.slideNavBtnActive : {})
                  }}
                >
                  {i + 1}
                </button>
              ))}
            </div>

            {/* Actions */}
            <div style={styles.previewActions}>
              <button
                onClick={() => setStep(2)}
                style={styles.secondaryBtn}
              >
                Change Style
              </button>
              <button
                onClick={handleExport}
                disabled={isProcessing}
                style={styles.primaryBtn}
              >
                {isProcessing ? (
                  <>
                    <div style={styles.spinnerSmall}></div>
                    {processingStatus || 'Generating...'}
                  </>
                ) : (
                  <>
                    <Download size={20} />
                    Download PPTX
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Success */}
        {step === 4 && (
          <div style={styles.successSection}>
            <div style={styles.successIcon}>
              <Check size={48} color="#10b981" />
            </div>
            <h2 style={styles.successTitle}>Your Presentation is Ready!</h2>
            <p style={styles.successText}>
              {aiInsights ? (
                <>Your presentation has been redesigned with AI-powered world-class design tailored to each slide's content.</>
              ) : (
                <>Your redesigned presentation has been downloaded.</>
              )}
            </p>
            {aiInsights?.concept_name && (
              <div style={styles.successConcept}>
                <Brain size={16} />
                <span>Design Concept: <strong>{aiInsights.concept_name}</strong></span>
              </div>
            )}
            <button onClick={handleReset} style={styles.primaryBtn}>
              <RefreshCw size={20} />
              Redesign Another Presentation
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>AI Design Director • World-Class PowerPoint Design • SlideStyler</p>
      </footer>
    </div>
  );
}

// Styles
const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    color: '#ffffff',
  },
  header: {
    textAlign: 'center',
    padding: '40px 20px 20px',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
  },
  logoText: {
    fontSize: '32px',
    fontWeight: '800',
    background: 'linear-gradient(135deg, #a78bfa 0%, #f472b6 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  tagline: {
    marginTop: '8px',
    color: '#8888aa',
    fontSize: '16px',
  },
  progressContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '20px',
    flexWrap: 'wrap',
  },
  progressStep: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    opacity: 0.5,
    transition: 'opacity 0.3s',
  },
  progressStepActive: {
    opacity: 1,
  },
  progressIcon: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: 'rgba(255,255,255,0.1)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.3s',
  },
  progressIconActive: {
    background: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)',
  },
  progressLabel: {
    fontSize: '14px',
    fontWeight: '500',
  },
  error: {
    background: 'rgba(239, 68, 68, 0.2)',
    border: '1px solid rgba(239, 68, 68, 0.5)',
    color: '#fca5a5',
    padding: '12px 20px',
    margin: '0 20px',
    borderRadius: '8px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  errorClose: {
    background: 'none',
    border: 'none',
    color: '#fca5a5',
    fontSize: '20px',
    cursor: 'pointer',
  },
  main: {
    flex: 1,
    padding: '20px',
    maxWidth: '1400px',
    margin: '0 auto',
    width: '100%',
  },
  uploadSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '30px',
  },
  uploadBox: {
    width: '100%',
    maxWidth: '600px',
  },
  fileInput: {
    display: 'none',
  },
  uploadLabel: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '16px',
    padding: '60px 40px',
    background: 'rgba(255,255,255,0.05)',
    border: '2px dashed rgba(167, 139, 250, 0.4)',
    borderRadius: '16px',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  uploadText: {
    fontSize: '20px',
    fontWeight: '600',
  },
  uploadSubtext: {
    color: '#8888aa',
    fontSize: '14px',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '3px solid rgba(167, 139, 250, 0.3)',
    borderTopColor: '#a78bfa',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  spinnerSmall: {
    width: '20px',
    height: '20px',
    border: '2px solid rgba(255,255,255,0.3)',
    borderTopColor: '#ffffff',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  aiSettings: {
    width: '100%',
    maxWidth: '600px',
    background: 'linear-gradient(135deg, rgba(167, 139, 250, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%)',
    borderRadius: '16px',
    padding: '24px',
    border: '1px solid rgba(167, 139, 250, 0.2)',
  },
  aiSettingsTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '18px',
    fontWeight: '700',
    marginBottom: '8px',
    color: '#a78bfa',
  },
  aiSettingsDescription: {
    fontSize: '14px',
    color: '#8888aa',
    marginBottom: '16px',
    lineHeight: '1.5',
  },
  aiFeatures: {
    display: 'flex',
    gap: '16px',
    flexWrap: 'wrap',
    marginBottom: '20px',
    padding: '12px 0',
    borderTop: '1px solid rgba(255,255,255,0.1)',
    borderBottom: '1px solid rgba(255,255,255,0.1)',
  },
  aiFeature: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
    color: '#d1d5db',
  },
  aiToggle: {
    marginBottom: '16px',
  },
  toggleLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    cursor: 'pointer',
    padding: '8px 0',
  },
  checkbox: {
    width: '20px',
    height: '20px',
    accentColor: '#a78bfa',
  },
  toggleText: {
    fontSize: '15px',
    color: '#ffffff',
  },
  aiAdvanced: {
    borderTop: '1px solid rgba(255,255,255,0.1)',
    paddingTop: '16px',
    marginTop: '8px',
  },
  inputGroup: {
    marginBottom: '16px',
  },
  inputLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '13px',
    color: '#a78bfa',
    marginBottom: '8px',
  },
  input: {
    width: '100%',
    padding: '12px 16px',
    background: 'rgba(255,255,255,0.1)',
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '14px',
  },
  inputHint: {
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '6px',
    display: 'block',
  },
  link: {
    color: '#a78bfa',
    textDecoration: 'none',
  },
  styleSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  styleSectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '12px',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  sectionTitle: {
    fontSize: '24px',
    fontWeight: '700',
  },
  slideCount: {
    background: 'rgba(167, 139, 250, 0.2)',
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '14px',
    color: '#a78bfa',
  },
  categoryFilter: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  categoryBtn: {
    padding: '8px 16px',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '20px',
    color: '#8888aa',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  categoryBtnActive: {
    background: 'rgba(167, 139, 250, 0.2)',
    borderColor: '#a78bfa',
    color: '#a78bfa',
  },
  styleGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '16px',
  },
  styleCard: {
    background: 'rgba(255,255,255,0.05)',
    borderRadius: '12px',
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'all 0.2s',
    border: '2px solid transparent',
    position: 'relative',
  },
  styleCardSelected: {
    borderColor: '#a78bfa',
    background: 'rgba(167, 139, 250, 0.1)',
  },
  colorPreview: {
    height: '80px',
    display: 'flex',
  },
  colorSwatch: {
    height: '100%',
  },
  styleInfo: {
    padding: '16px',
  },
  styleName: {
    fontSize: '16px',
    fontWeight: '600',
    marginBottom: '4px',
  },
  styleDesc: {
    fontSize: '13px',
    color: '#8888aa',
    marginBottom: '8px',
    lineHeight: '1.4',
  },
  styleCategory: {
    fontSize: '12px',
    background: 'rgba(255,255,255,0.1)',
    padding: '4px 8px',
    borderRadius: '4px',
    color: '#aaaacc',
  },
  selectedBadge: {
    position: 'absolute',
    top: '12px',
    right: '12px',
    width: '28px',
    height: '28px',
    borderRadius: '50%',
    background: '#a78bfa',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '16px 32px',
    background: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)',
    border: 'none',
    borderRadius: '12px',
    color: '#ffffff',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    alignSelf: 'center',
    marginTop: '20px',
    transition: 'all 0.2s',
  },
  primaryBtnDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  secondaryBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 24px',
    background: 'rgba(255,255,255,0.1)',
    border: '1px solid rgba(255,255,255,0.2)',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '14px',
    cursor: 'pointer',
  },
  previewSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '24px',
  },
  previewHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  aiInsightsBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    background: 'linear-gradient(135deg, rgba(167, 139, 250, 0.3) 0%, rgba(139, 92, 246, 0.2) 100%)',
    padding: '6px 14px',
    borderRadius: '20px',
    fontSize: '13px',
    color: '#a78bfa',
    fontWeight: '500',
  },
  aiInsightsPanel: {
    width: '100%',
    maxWidth: '960px',
    background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%)',
    borderRadius: '12px',
    padding: '20px',
    border: '1px solid rgba(251, 191, 36, 0.2)',
  },
  insightHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '15px',
    fontWeight: '600',
    color: '#fbbf24',
    marginBottom: '12px',
  },
  insightContent: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '16px',
  },
  insightItem: {
    fontSize: '14px',
    color: '#d1d5db',
  },
  insightDescription: {
    width: '100%',
    fontSize: '13px',
    color: '#9ca3af',
    fontStyle: 'italic',
    marginTop: '8px',
    lineHeight: '1.5',
  },
  previewContainer: {
    width: '100%',
    maxWidth: '960px',
    aspectRatio: '16/9',
    background: 'rgba(0,0,0,0.3)',
    borderRadius: '12px',
    overflow: 'hidden',
    border: '1px solid rgba(255,255,255,0.1)',
  },
  previewFrame: {
    width: '100%',
    height: '100%',
    border: 'none',
  },
  previewPlaceholder: {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    color: '#4a4a6a',
  },
  slideNav: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  slideNavBtn: {
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    background: 'rgba(255,255,255,0.1)',
    border: 'none',
    color: '#8888aa',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.2s',
  },
  slideNavBtnActive: {
    background: '#a78bfa',
    color: '#ffffff',
  },
  previewActions: {
    display: 'flex',
    gap: '16px',
    marginTop: '20px',
  },
  successSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '24px',
    minHeight: '400px',
    textAlign: 'center',
  },
  successIcon: {
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: 'rgba(16, 185, 129, 0.2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  successTitle: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#ffffff',
  },
  successText: {
    fontSize: '16px',
    color: '#8888aa',
    maxWidth: '500px',
    lineHeight: '1.6',
  },
  successConcept: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    background: 'rgba(167, 139, 250, 0.15)',
    padding: '10px 20px',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#a78bfa',
  },
  footer: {
    textAlign: 'center',
    padding: '30px',
    color: '#4a4a6a',
    fontSize: '14px',
  },
};

// Add keyframes for spinner animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  label:hover {
    border-color: rgba(167, 139, 250, 0.6) !important;
    background: rgba(255,255,255,0.08) !important;
  }
  
  button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(167, 139, 250, 0.3);
  }
`;
document.head.appendChild(styleSheet);

export default App;
