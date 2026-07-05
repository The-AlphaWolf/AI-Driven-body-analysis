import { useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import api from '../services/api';

const CATEGORY_ICONS = {
  necklines: '👔',
  silhouettes: '👗',
  colors: '🎨',
  patterns: '🔲',
  accessories: '💍',
  hairstyles: '💇',
};

const CATEGORY_LABELS = {
  necklines: 'Necklines',
  silhouettes: 'Silhouettes & Fits',
  colors: 'Color Palette',
  patterns: 'Patterns',
  accessories: 'Accessories',
  hairstyles: 'Hairstyles',
};

export default function ResultsPage() {
  const { id } = useParams();
  const location = useLocation();
  const [analysis, setAnalysis] = useState(location.state?.analysis || null);
  const [loading, setLoading] = useState(!analysis);

  useEffect(() => {
    if (!analysis && id) {
      api.getAnalysis(id)
        .then((data) => setAnalysis(data.analysis))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [id, analysis]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '80px 24px' }}>
        <h2>Analysis not found</h2>
        <Link to="/analyze" className="btn btn-primary" style={{ marginTop: '20px' }}>New Analysis</Link>
      </div>
    );
  }

  const { face_analysis, skin_analysis, body_analysis, recommendations } = analysis;

  // Group recommendations by category
  const grouped = {};
  (recommendations || []).forEach((rec) => {
    if (!grouped[rec.category]) grouped[rec.category] = [];
    grouped[rec.category].push(rec);
  });

  return (
    <div className="container" style={{ padding: '48px 24px', maxWidth: '1000px' }}>
      {/* Header */}
      <div className="fade-in" style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>
          Your Style <span style={{
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>Analysis</span>
        </h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
          {new Date(analysis.created_at).toLocaleDateString('en-US', { 
            year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
          })}
        </p>
      </div>

      {/* ── Analysis Results Cards ──────────────────────────────────── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '20px',
        marginBottom: '48px',
      }}>
        {/* Face Shape Card */}
        {face_analysis && (
          <div className="glass-card fade-in stagger-1" style={{ padding: '28px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <span style={{ fontSize: '1.5rem' }}>👤</span>
              <h3 style={{ fontSize: '1rem', color: 'var(--color-text-muted)' }}>Face Shape</h3>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <span className="badge badge-primary" style={{
                fontSize: '1.1rem',
                padding: '8px 20px',
                textTransform: 'capitalize',
              }}>
                {face_analysis.shape}
              </span>
            </div>

            {/* Confidence bar */}
            <div style={{ marginBottom: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                <span style={{ color: 'var(--color-text-dim)' }}>Confidence</span>
                <span style={{ color: 'var(--color-primary-light)' }}>
                  {Math.round(face_analysis.confidence * 100)}%
                </span>
              </div>
              <div className="confidence-bar">
                <div className="confidence-bar-fill" style={{ width: `${face_analysis.confidence * 100}%` }} />
              </div>
            </div>
          </div>
        )}

        {/* Skin Tone Card */}
        {skin_analysis && (
          <div className="glass-card fade-in stagger-2" style={{ padding: '28px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <span style={{ fontSize: '1.5rem' }}>🎨</span>
              <h3 style={{ fontSize: '1rem', color: 'var(--color-text-muted)' }}>Skin Tone</h3>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
              {/* Color swatch */}
              <div style={{
                width: '52px',
                height: '52px',
                borderRadius: 'var(--radius-md)',
                background: skin_analysis.hex_color,
                border: '2px solid var(--color-border)',
                boxShadow: `0 0 20px ${skin_analysis.hex_color}40`,
              }} />
              <div>
                <div style={{ textTransform: 'capitalize', fontWeight: 600, fontSize: '1rem' }}>
                  {skin_analysis.depth}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                  {skin_analysis.undertone} undertone
                </div>
              </div>
            </div>

            {skin_analysis.low_confidence_flag && (
              <div className="badge badge-warning" style={{ fontSize: '0.75rem' }}>
                ⚠ Low confidence — lighting may be uneven
              </div>
            )}

            {/* Confidence bar */}
            <div style={{ marginTop: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                <span style={{ color: 'var(--color-text-dim)' }}>Confidence</span>
                <span style={{ color: 'var(--color-primary-light)' }}>
                  {Math.round(skin_analysis.confidence * 100)}%
                </span>
              </div>
              <div className="confidence-bar">
                <div className="confidence-bar-fill" style={{ width: `${skin_analysis.confidence * 100}%` }} />
              </div>
            </div>
          </div>
        )}

        {/* Body Shape Card */}
        {body_analysis && (
          <div className="glass-card fade-in stagger-3" style={{ padding: '28px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <span style={{ fontSize: '1.5rem' }}>📐</span>
              <h3 style={{ fontSize: '1rem', color: 'var(--color-text-muted)' }}>Body Shape</h3>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <span className="badge badge-accent" style={{
                fontSize: '1.1rem',
                padding: '8px 20px',
                textTransform: 'capitalize',
              }}>
                {body_analysis.shape.replace('_', ' ')}
              </span>
            </div>

            {/* Confidence bar */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                <span style={{ color: 'var(--color-text-dim)' }}>Confidence</span>
                <span style={{ color: 'var(--color-primary-light)' }}>
                  {Math.round(body_analysis.confidence * 100)}%
                </span>
              </div>
              <div className="confidence-bar">
                <div className="confidence-bar-fill" style={{ width: `${body_analysis.confidence * 100}%` }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── Recommendations ────────────────────────────────────────── */}
      {recommendations && recommendations.length > 0 && (
        <div className="fade-in" style={{ animationDelay: '0.4s' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '8px', textAlign: 'center' }}>
            Your Personalized Recommendations
          </h2>
          <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', marginBottom: '32px', fontSize: '0.9rem' }}>
            Tailored suggestions based on your unique attributes
          </p>

          {Object.entries(grouped).map(([category, recs]) => (
            <div key={category} style={{ marginBottom: '36px' }}>
              <h3 style={{
                fontSize: '1.1rem',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: 'var(--color-primary-light)',
              }}>
                <span>{CATEGORY_ICONS[category] || '📋'}</span>
                {CATEGORY_LABELS[category] || category}
              </h3>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '16px',
              }}>
                {recs.map((rec, i) => (
                  <div key={i} className="glass-card" style={{
                    padding: '20px',
                    transition: 'transform 0.2s ease',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
                  >
                    <h4 style={{ fontSize: '1rem', marginBottom: '8px' }}>{rec.recommendation}</h4>
                    <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', lineHeight: 1.6, marginBottom: '12px' }}>
                      {rec.explanation}
                    </p>

                    {/* Match reasons */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {rec.match_reasons?.slice(0, 3).map((reason, j) => (
                        <span key={j} className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                          ✓ {reason}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Actions ────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '40px', flexWrap: 'wrap' }}>
        <Link to="/analyze" className="btn btn-primary">✨ New Analysis</Link>
        <Link to="/dashboard" className="btn btn-secondary">📊 Dashboard</Link>
      </div>
    </div>
  );
}
