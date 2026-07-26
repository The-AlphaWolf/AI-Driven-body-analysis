import FeedbackButtons from './FeedbackButtons';
import FaceMesh from './FaceMesh';
import { Frame, Meter, Swatches } from './Hud';

/** Feedback rows are keyed by category and recommendation text, not by id. */
const feedbackKey = (category, recommendation) => `${category}::${recommendation}`;

const CATEGORY_LABELS = {
  necklines: 'Necklines',
  silhouettes: 'Silhouettes & Fits',
  colors: 'Colour Palette',
  patterns: 'Patterns',
  accessories: 'Accessories',
  hairstyles: 'Hairstyles',
};

const CATEGORY_SLUGS = {
  necklines: 'NECK / FACE-WEIGHTED',
  silhouettes: 'FIT / BODY-WEIGHTED',
  colors: 'LAB / SKIN-WEIGHTED',
  patterns: 'SCALE / BODY-WEIGHTED',
  accessories: 'DETAIL / MIXED',
  hairstyles: 'CROWN / FACE-WEIGHTED',
};

const titleCase = (value) => (value || '').replace(/_/g, ' ');

/**
 * The attribute panel and recommendation list for one analysis.
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

  // The first colour recommendation's swatches double as the report's palette.
  const headlinePalette = (grouped.colors || []).find((r) => r.palette?.length)?.palette;

  const detected = Boolean(face_analysis || skin_analysis || body_analysis);

  return (
    <>
      {/* ── Instrument panel ────────────────────────────────────────── */}
      {detected && (
        <Frame className="fade-in" style={{ padding: '28px 26px', marginBottom: '40px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
            gap: '16px',
            paddingBottom: '20px',
            marginBottom: '26px',
            borderBottom: '1px solid var(--line)',
          }}>
            <span className="label label-accent">Analysis</span>
            <span className="label">MediaPipe · K-Means · LAB</span>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '40px',
            alignItems: 'center',
          }}>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <FaceMesh />
            </div>

            <div style={{ display: 'grid', gap: '22px' }}>
              {face_analysis && (
                <AttributeRow
                  label="Face Shape"
                  value={titleCase(face_analysis.shape)}
                  confidence={face_analysis.confidence}
                />
              )}

              {skin_analysis && (
                <AttributeRow
                  label="Skin Tone"
                  value={`${titleCase(skin_analysis.depth)} — ${titleCase(skin_analysis.undertone)}`}
                  confidence={skin_analysis.confidence}
                  chip={skin_analysis.hex_color}
                  warning={skin_analysis.low_confidence_flag
                    ? 'Uneven lighting — reading may be unreliable'
                    : null}
                />
              )}

              {body_analysis && (
                <AttributeRow
                  label="Body Type"
                  value={titleCase(body_analysis.shape)}
                  confidence={body_analysis.confidence}
                />
              )}
            </div>
          </div>

          {headlinePalette && (
            <div style={{ marginTop: '36px' }}>
              <span className="label" style={{ marginBottom: '14px' }}>Recommended palette</span>
              <Swatches palette={headlinePalette} />
            </div>
          )}
        </Frame>
      )}

      {/* ── Recommendations ─────────────────────────────────────────── */}
      {recommendations?.length > 0 && (
        <div className="fade-in stagger-2">
          <div className="section-head">
            <div>
              <h2 style={{ textTransform: 'uppercase' }}>Recommendations</h2>
              <p className="mono" style={{ marginTop: '6px' }}>
                {interactive
                  ? 'KEEP OR REJECT — REJECTED ITEMS INFORM FUTURE ADVICE'
                  : 'TAILORED TO THE DETECTED ATTRIBUTES'}
              </p>
            </div>
            <span className="label label-accent">
              {recommendations.length} Items
            </span>
          </div>

          {Object.entries(grouped).map(([category, recs]) => (
            <section key={category} style={{ marginBottom: '44px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'baseline',
                justifyContent: 'space-between',
                gap: '14px',
                marginBottom: '16px',
              }}>
                <h3 style={{
                  fontSize: '0.95rem',
                  textTransform: 'uppercase',
                  color: 'var(--accent)',
                  letterSpacing: '0.04em',
                }}>
                  {CATEGORY_LABELS[category] || category}
                </h3>
                <span className="label">{CATEGORY_SLUGS[category] || category}</span>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '16px',
              }}>
                {recs.map((rec, i) => {
                  const key = feedbackKey(rec.category, rec.recommendation);
                  const verdict = feedback[key] || null;

                  return (
                    <Frame
                      key={i}
                      hover
                      style={{
                        padding: '20px 18px',
                        opacity: verdict === 'dislike' ? 0.45 : 1,
                        transition: 'opacity 0.25s ease',
                      }}
                    >
                      <div style={{
                        display: 'flex',
                        gap: '12px',
                        alignItems: 'flex-start',
                        marginBottom: '10px',
                      }}>
                        <h4 style={{
                          fontSize: '0.98rem',
                          flex: 1,
                          textTransform: 'uppercase',
                          lineHeight: 1.3,
                        }}>
                          {rec.recommendation}
                        </h4>
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

                      <p style={{
                        fontSize: '0.83rem',
                        color: 'var(--text-muted)',
                        lineHeight: 1.65,
                        marginBottom: rec.palette ? '16px' : '12px',
                      }}>
                        {rec.explanation}
                      </p>

                      {rec.palette && (
                        <div style={{ marginBottom: '14px' }}>
                          <Swatches palette={rec.palette} />
                        </div>
                      )}

                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {rec.match_reasons?.slice(0, 3).map((reason, j) => (
                          <span key={j} className="tag tag-ok">{reason}</span>
                        ))}
                      </div>
                    </Frame>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  );
}

/** One measured attribute: caption, value, percentage, meter. */
function AttributeRow({ label, value, confidence, chip = null, warning = null }) {
  return (
    <div>
      <span className="label" style={{ marginBottom: '5px' }}>{label}</span>

      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        justifyContent: 'space-between',
        gap: '16px',
        marginBottom: '9px',
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '11px', minWidth: 0 }}>
          {chip && (
            <span
              aria-hidden="true"
              style={{
                width: '17px',
                height: '17px',
                background: chip,
                border: '1px solid rgba(255,255,255,0.2)',
                flexShrink: 0,
              }}
            />
          )}
          <span className="readout">{value}</span>
        </span>
        <span className="meter-value">{Math.round((confidence || 0) * 100)}%</span>
      </div>

      <Meter value={confidence} />

      {chip && (
        <span className="mono" style={{ display: 'block', marginTop: '7px' }}>
          {chip.toUpperCase()}
        </span>
      )}

      {warning && (
        <span className="tag tag-warn" style={{ marginTop: '10px' }}>{warning}</span>
      )}
    </div>
  );
}
