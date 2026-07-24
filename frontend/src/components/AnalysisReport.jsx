import FeedbackButtons from './FeedbackButtons';

/** Feedback rows are keyed by category and recommendation text, not by id. */
const feedbackKey = (category, recommendation) => `${category}::${recommendation}`;

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

function ConfidenceBar({ value }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
        <span style={{ color: 'var(--color-text-dim)' }}>Confidence</span>
        <span style={{ color: 'var(--color-primary-light)' }}>{Math.round(value * 100)}%</span>
      </div>
      <div className="confidence-bar">
        <div className="confidence-bar-fill" style={{ width: `${value * 100}%` }} />
      </div>
    </div>
  );
}

/**
 * The attribute cards and recommendation grid for one analysis.
 *
 * Shared by the owner's results page and the public share page. The public
 * view passes no feedback handler, which hides the like/dislike controls —
 * a stranger with a link should not be writing to the owner's data.
 */
export default function AnalysisReport({
  analysis,
  analysisId = null,
  feedback = {},
  onFeedbackChange = null,
}) {
  const { face_analysis, skin_analysis, body_analysis, recommendations } = analysis;
  const interactive = Boolean(onFeedbackChange && analysisId);

  const grouped = {};
  (recommendations || []).forEach((rec) => {
    if (!grouped[rec.category]) grouped[rec.category] = [];
    grouped[rec.category].push(rec);
  });

  return (
    <>
      {/* ── Detected attributes ─────────────────────────────────────── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '20px',
        marginBottom: '48px',
      }}>
        {face_analysis && (
          <div className="glass-card fade-in stagger-1" style={{ padding: '28px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <span style={{ fontSize: '1.5rem' }}>👤</span>
              <h3 style={{ fontSize: '1rem', color: 'var(--color-text-muted)' }}>Face Shape</h3>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <span className="badge badge-primary" style={{ fontSize: '1.1rem', padding: '8px 20px', textTransform: 'capitalize' }}>
                {face_analysis.shape}
              </span>
            </div>
            <ConfidenceBar value={face_analysis.confidence} />
          </div>
        )}

        {skin_analysis && (
          <div className="glass-card fade-in stagger-2" style={{ padding: '28px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <span style={{ fontSize: '1.5rem' }}>🎨</span>
              <h3 style={{ fontSize: '1rem', color: 'var(--color-text-muted)' }}>Skin Tone</h3>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
              <div style={{
                width: '52px',
                height: '52px',
                borderRadius: 'var(--radius-md)',
                background: skin_analysis.hex_color,
                border: '2px solid var(--color-border)',
                boxShadow: `0 0 20px ${skin_analysis.hex_color}40`,
                flexShrink: 0,
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
              <div className="badge badge-warning" style={{ fontSize: '0.75rem', marginBottom: '8px' }}>
                ⚠ Low confidence — lighting may be uneven
              </div>
            )}

            <ConfidenceBar value={skin_analysis.confidence} />
          </div>
        )}

        {body_analysis && (
          <div className="glass-card fade-in stagger-3" style={{ padding: '28px 24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <span style={{ fontSize: '1.5rem' }}>📐</span>
              <h3 style={{ fontSize: '1rem', color: 'var(--color-text-muted)' }}>Body Shape</h3>
            </div>
            <div style={{ marginBottom: '16px' }}>
              <span className="badge badge-accent" style={{ fontSize: '1.1rem', padding: '8px 20px', textTransform: 'capitalize' }}>
                {body_analysis.shape.replace('_', ' ')}
              </span>
            </div>
            <ConfidenceBar value={body_analysis.confidence} />
          </div>
        )}
      </div>

      {/* ── Recommendations ─────────────────────────────────────────── */}
      {recommendations && recommendations.length > 0 && (
        <div className="fade-in" style={{ animationDelay: '0.4s' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '8px', textAlign: 'center' }}>
            Personalized Recommendations
          </h2>
          <p style={{ textAlign: 'center', color: 'var(--color-text-muted)', marginBottom: '32px', fontSize: '0.9rem' }}>
            {interactive
              ? 'Tap the heart to keep one, or thumbs-down to hide it from future advice'
              : 'Tailored suggestions based on the detected attributes'}
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
                gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                gap: '16px',
              }}>
                {recs.map((rec, i) => {
                  const key = feedbackKey(rec.category, rec.recommendation);
                  const verdict = feedback[key] || null;

                  return (
                    <div
                      key={i}
                      className="glass-card"
                      style={{
                        padding: '20px',
                        transition: 'transform 0.2s ease, opacity 0.2s ease',
                        opacity: verdict === 'dislike' ? 0.55 : 1,
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
                    >
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
                        <h4 style={{ fontSize: '1rem', flex: 1 }}>{rec.recommendation}</h4>
                        {interactive && (
                          <FeedbackButtons
                            analysisId={analysisId}
                            category={rec.category}
                            recommendation={rec.recommendation}
                            verdict={verdict}
                            onChange={(next) => onFeedbackChange(key, next)}
                          />
                        )}
                      </div>

                      <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', lineHeight: 1.6, marginBottom: '12px' }}>
                        {rec.explanation}
                      </p>

                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {rec.match_reasons?.slice(0, 3).map((reason, j) => (
                          <span key={j} className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                            ✓ {reason}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
