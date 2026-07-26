import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import FaceMesh from '../components/FaceMesh';
import { Frame, Meter, SectionHead, Swatches } from '../components/Hud';

/**
 * The landing page is built as a worked example: rather than describing what
 * the analysis produces, it shows a finished readout panel and lets the
 * layout carry the explanation.
 */

const MODULES = [
  {
    index: '01',
    title: 'Face Shape',
    slug: 'MEDIAPIPE / 478 PTS',
    desc: 'Landmark geometry from a face mesh, reduced to the width, length and jaw ratios that separate oval from heart from square.',
  },
  {
    index: '02',
    title: 'Skin Tone',
    slug: 'K-MEANS / LAB',
    desc: 'Sampled skin pixels clustered in LAB colour space, resolved into a depth band and a warm, cool or neutral undertone.',
  },
  {
    index: '03',
    title: 'Body Proportion',
    slug: 'POSE / 33 PTS',
    desc: 'Shoulder, waist and hip landmarks from pose estimation, compared as ratios to classify the silhouette.',
  },
  {
    index: '04',
    title: 'Recommendation',
    slug: 'WEIGHTED SCORING',
    desc: 'A rules dataset scored against your attribute vector, with category-dependent weights and hard exclusion of contradicting advice.',
  },
];

/* A representative reading — the same shape the analyser returns. */
const SPECIMEN = {
  rows: [
    { label: 'Face Shape', value: 'Oval', confidence: 0.93 },
    { label: 'Undertone', value: 'Warm — Autumn', confidence: 0.87 },
    { label: 'Body Type', value: 'Inverted Triangle', confidence: 0.81 },
    { label: 'Contrast', value: 'Medium-High', confidence: 0.76 },
  ],
  palette: [
    { name: 'Terracotta', hex: '#C1663F' },
    { name: 'Marigold', hex: '#D98324' },
    { name: 'Camel', hex: '#C19A6B' },
    { name: 'Olive', hex: '#6B7A4B' },
    { name: 'Deep Teal', hex: '#14615E' },
    { name: 'Rust', hex: '#A5442A' },
    { name: 'Cream', hex: '#EDE3D2' },
    { name: 'Espresso', hex: '#4A3728' },
  ],
};

export default function LandingPage() {
  const { user } = useAuth();
  const startTo = user ? '/analyze' : '/register';
  const startLabel = user ? 'Start Analysis' : 'Get Started Free';

  return (
    <div>
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section className="container" style={{ padding: '72px 28px 40px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr)',
          gap: '48px',
          alignItems: 'center',
        }}>
          <div className="fade-in" style={{ maxWidth: '660px' }}>
            <span className="label label-accent" style={{ marginBottom: '18px' }}>
              Facial structure + skin-tone fashion engine
            </span>

            <h1 style={{
              fontSize: 'clamp(2.4rem, 6.5vw, 4.2rem)',
              lineHeight: 1.02,
              textTransform: 'uppercase',
              marginBottom: '22px',
            }}>
              AI Style &amp;<br />
              <span style={{ color: 'var(--accent)' }}>Body Analysis</span>
            </h1>

            <p style={{
              color: 'var(--text-muted)',
              fontSize: '1rem',
              maxWidth: '540px',
              marginBottom: '32px',
            }}>
              Upload a photo. Computer vision reads your face shape, skin tone and
              body proportions, then a scoring engine turns those measurements into
              styling advice that shows its working.
            </p>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '28px' }}>
              <Link to={startTo} className="btn btn-primary" style={{ padding: '14px 30px' }}>
                {startLabel}
              </Link>
              <a href="#modules" className="btn btn-secondary" style={{ padding: '14px 30px' }}>
                How it works ↓
              </a>
            </div>

            <p className="mono">
              MEDIAPIPE · 478 LANDMARKS · LAB ΔE MATCHING · NO PAID APIS
            </p>
          </div>
        </div>
      </section>

      {/* ── Worked example ────────────────────────────────────────────── */}
      <section className="container" style={{ padding: '20px 28px 80px' }}>
        <Frame className="fade-in stagger-1" style={{ padding: '28px 26px 24px' }}>
          {/* Top rail */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
            gap: '16px',
            paddingBottom: '20px',
            marginBottom: '26px',
            borderBottom: '1px solid var(--line)',
          }}>
            <span className="label">Sample Report / 01</span>
            <span className="label">Representative output</span>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))',
            gap: '40px',
            alignItems: 'center',
          }}>
            {/* Mesh */}
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <FaceMesh />
            </div>

            {/* Readouts */}
            <div>
              <span className="label label-accent" style={{ marginBottom: '20px' }}>Analysis</span>

              <div style={{ display: 'grid', gap: '20px' }}>
                {SPECIMEN.rows.map((row) => (
                  <div key={row.label}>
                    <span className="label" style={{ marginBottom: '5px' }}>{row.label}</span>
                    <div style={{
                      display: 'flex',
                      alignItems: 'baseline',
                      justifyContent: 'space-between',
                      gap: '16px',
                      marginBottom: '9px',
                    }}>
                      <span className="readout">{row.value}</span>
                      <span className="meter-value">{Math.round(row.confidence * 100)}%</span>
                    </div>
                    <Meter value={row.confidence} />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Palette */}
          <div style={{ marginTop: '36px' }}>
            <span className="label" style={{ marginBottom: '14px' }}>Recommended palette</span>
            <Swatches palette={SPECIMEN.palette} />
          </div>

          {/* Bottom rail */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-end',
            gap: '16px',
            flexWrap: 'wrap',
            paddingTop: '24px',
            marginTop: '30px',
            borderTop: '1px solid var(--line)',
          }}>
            <div>
              <h2 style={{ fontSize: 'clamp(1.2rem, 3vw, 1.7rem)' }}>
                AI Style &amp; Body Analysis
              </h2>
              <span className="label" style={{ marginTop: '6px' }}>
                Facial structure + skin-tone fashion engine
              </span>
            </div>
            <span className="label label-accent" style={{ fontSize: '0.72rem' }}>
              Style-Analysis
            </span>
          </div>
        </Frame>
      </section>

      {/* ── Modules ───────────────────────────────────────────────────── */}
      <section id="modules" className="container" style={{ padding: '20px 28px 80px' }}>
        <SectionHead
          title="Pipeline"
          sub="Real computer vision and machine learning — no gimmicks, no paid APIs."
          slug="04 Modules"
        />

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '18px',
        }}>
          {MODULES.map((m, i) => (
            <Frame
              key={m.index}
              hover
              className={`fade-in stagger-${i + 1}`}
              style={{ padding: '26px 22px' }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'baseline',
                justifyContent: 'space-between',
                marginBottom: '18px',
              }}>
                <span style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.7rem',
                  fontWeight: 700,
                  color: 'var(--accent)',
                  lineHeight: 1,
                }}>
                  {m.index}
                </span>
                <span className="label">{m.slug}</span>
              </div>

              <h3 style={{
                fontSize: '1.05rem',
                textTransform: 'uppercase',
                marginBottom: '10px',
              }}>
                {m.title}
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.65 }}>
                {m.desc}
              </p>
            </Frame>
          ))}
        </div>
      </section>

      {/* ── Sequence ──────────────────────────────────────────────────── */}
      <section className="container" style={{ padding: '0 28px 90px' }}>
        <SectionHead title="Sequence" slug="03 Steps" />

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
          gap: '0',
        }}>
          {[
            { step: '01', title: 'Upload', desc: 'A face photo, a full-body photo, or both. Each is optional.' },
            { step: '02', title: 'Measure', desc: 'Landmarks, clustering and ratios run server-side, in memory.' },
            { step: '03', title: 'Style', desc: 'Ranked advice, each item carrying the reasons it was chosen.' },
          ].map((s, i) => (
            <div
              key={s.step}
              style={{
                padding: '26px 24px',
                borderLeft: i === 0 ? '1px solid var(--line)' : 'none',
                borderRight: '1px solid var(--line)',
                borderTop: '1px solid var(--line)',
                borderBottom: '1px solid var(--line)',
              }}
            >
              <span className="label label-accent" style={{ marginBottom: '14px' }}>
                Step {s.step}
              </span>
              <h3 style={{ fontSize: '1.15rem', textTransform: 'uppercase', marginBottom: '8px' }}>
                {s.title}
              </h3>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)' }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Close ─────────────────────────────────────────────────────── */}
      <section className="container" style={{ padding: '0 28px 90px' }}>
        <Frame style={{ padding: '54px 28px', textAlign: 'center' }}>
          <span className="label label-accent" style={{ marginBottom: '16px' }}>
            Free · No subscription
          </span>
          <h2 style={{
            fontSize: 'clamp(1.6rem, 4vw, 2.4rem)',
            textTransform: 'uppercase',
            marginBottom: '14px',
          }}>
            Run your first scan
          </h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '30px', fontSize: '0.92rem' }}>
            Photos are decoded in memory and never written to disk.
          </p>
          <Link to={startTo} className="btn btn-primary" style={{ padding: '15px 36px' }}>
            {startLabel}
          </Link>
        </Frame>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────── */}
      <footer style={{ borderTop: '1px solid var(--line)', padding: '22px 0' }}>
        <div className="container" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap',
        }}>
          <span className="label">
            StyleSense AI — MediaPipe · OpenCV · Flask · React
          </span>
          <span className="label">Style-Analysis</span>
        </div>
      </footer>
    </div>
  );
}
