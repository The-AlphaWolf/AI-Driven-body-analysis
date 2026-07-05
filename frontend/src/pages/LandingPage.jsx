import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const { user } = useAuth();

  const features = [
    {
      icon: '👤',
      title: 'Face Shape Analysis',
      desc: 'AI-powered detection using 478 facial landmarks to classify your face shape with confidence scoring.',
    },
    {
      icon: '🎨',
      title: 'Skin Tone Classification',
      desc: 'K-means clustering in LAB color space to determine your skin depth and undertone — warm, cool, or neutral.',
    },
    {
      icon: '📐',
      title: 'Body Proportion Mapping',
      desc: 'Full-body pose estimation to compute shoulder-to-hip ratios and classify your body shape.',
    },
    {
      icon: '✨',
      title: 'Smart Recommendations',
      desc: 'Weighted scoring engine matching your unique attributes to clothing, colors, hairstyles, and accessories.',
    },
  ];

  return (
    <div>
      {/* ── Hero Section ─────────────────────────────────────────── */}
      <section style={{
        minHeight: 'calc(100vh - 64px)',
        display: 'flex',
        alignItems: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background glow */}
        <div style={{
          position: 'absolute',
          top: '-20%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '800px',
          height: '800px',
          background: 'var(--gradient-glow)',
          borderRadius: '50%',
          pointerEvents: 'none',
        }} />

        <div className="container" style={{ position: 'relative', textAlign: 'center', padding: '60px 24px' }}>
          <div className="fade-in">
            <span className="badge badge-primary" style={{ marginBottom: '24px' }}>
              🔬 Powered by Computer Vision
            </span>
          </div>

          <h1 className="fade-in stagger-1" style={{
            fontSize: 'clamp(2.5rem, 6vw, 4rem)',
            marginBottom: '20px',
            lineHeight: 1.1,
          }}>
            Discover Your
            <br />
            <span style={{
              background: 'var(--gradient-primary)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>Perfect Style</span>
          </h1>

          <p className="fade-in stagger-2" style={{
            fontSize: 'clamp(1rem, 2vw, 1.2rem)',
            color: 'var(--color-text-muted)',
            maxWidth: '600px',
            margin: '0 auto 40px',
            lineHeight: 1.7,
          }}>
            Upload your photo and let AI analyze your face shape, skin tone, and body
            proportions to generate personalized fashion recommendations tailored just for you.
          </p>

          <div className="fade-in stagger-3" style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to={user ? '/analyze' : '/register'} className="btn btn-primary" style={{ padding: '14px 32px', fontSize: '1rem' }}>
              {user ? '✨ Start Analysis' : '🚀 Get Started Free'}
            </Link>
            <a href="#features" className="btn btn-secondary" style={{ padding: '14px 32px', fontSize: '1rem' }}>
              Learn More ↓
            </a>
          </div>
        </div>
      </section>

      {/* ── Features Section ──────────────────────────────────────── */}
      <section id="features" style={{ padding: '80px 0' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '12px' }}>
            How It Works
          </h2>
          <p style={{
            textAlign: 'center',
            color: 'var(--color-text-muted)',
            marginBottom: '48px',
            maxWidth: '500px',
            margin: '0 auto 48px',
          }}>
            Real computer vision and machine learning — no gimmicks, no paid APIs.
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '24px',
          }}>
            {features.map((f, i) => (
              <div key={i} className="glass-card" style={{
                padding: '32px 24px',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
              >
                <span style={{ fontSize: '2rem', display: 'block', marginBottom: '16px' }}>{f.icon}</span>
                <h3 style={{ fontSize: '1.15rem', marginBottom: '10px' }}>{f.title}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Process Section ────────────────────────────────────────── */}
      <section style={{ padding: '80px 0', background: 'var(--color-surface-hover)' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '48px' }}>
            Three Simple Steps
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '32px',
            textAlign: 'center',
          }}>
            {[
              { step: '01', title: 'Upload Photos', desc: 'Upload a face photo and/or full-body photo' },
              { step: '02', title: 'AI Analysis', desc: 'Our CV pipeline detects your shape, tone & proportions' },
              { step: '03', title: 'Get Styled', desc: 'Receive personalized recommendations with explanations' },
            ].map((s, i) => (
              <div key={i} style={{ padding: '24px' }}>
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '50%',
                  background: 'var(--gradient-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  fontWeight: 700,
                  fontSize: '1.1rem',
                }}>
                  {s.step}
                </div>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '8px' }}>{s.title}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Section ────────────────────────────────────────────── */}
      <section style={{ padding: '80px 0', textAlign: 'center' }}>
        <div className="container">
          <h2 style={{ fontSize: '2rem', marginBottom: '16px' }}>
            Ready to Find Your Style?
          </h2>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: '32px' }}>
            Free to use. No subscriptions. Just upload and discover.
          </p>
          <Link to={user ? '/analyze' : '/register'} className="btn btn-primary" style={{ padding: '16px 40px', fontSize: '1.1rem' }}>
            {user ? '✨ Analyze Now' : '🚀 Create Free Account'}
          </Link>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <footer style={{
        borderTop: '1px solid var(--color-border)',
        padding: '24px 0',
        textAlign: 'center',
        fontSize: '0.85rem',
        color: 'var(--color-text-dim)',
      }}>
        <div className="container">
          <p>© 2025 StyleSense AI — Built with MediaPipe, OpenCV, Flask & React</p>
        </div>
      </footer>
    </div>
  );
}
