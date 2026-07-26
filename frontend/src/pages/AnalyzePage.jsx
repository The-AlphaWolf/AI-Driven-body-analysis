import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import PhotoUpload from '../components/PhotoUpload';
import { Frame } from '../components/Hud';
import api from '../services/api';

const TIPS = [
  'Even lighting — avoid harsh shadows and backlighting',
  'Face the camera directly, head level',
  'Full-body shots: stand naturally, arms slightly away from the body',
  'A plain background helps pose estimation find your outline',
];

export default function AnalyzePage() {
  const [faceFile, setFaceFile] = useState(null);
  const [bodyFile, setBodyFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();
  const navigate = useNavigate();

  const canSubmit = (faceFile || bodyFile) && !loading;

  const handleAnalyze = async () => {
    if (!faceFile && !bodyFile) {
      addToast('Upload at least one photo', 'error');
      return;
    }

    setLoading(true);
    try {
      const data = await api.analyze(faceFile, bodyFile);
      addToast('Analysis complete', 'success');
      navigate(`/results/${data.analysis.id}`, { state: { analysis: data.analysis } });
    } catch (err) {
      addToast(err.message || 'Analysis failed. Try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '48px 28px 80px', maxWidth: '880px' }}>
      <div className="section-head fade-in">
        <div>
          <span className="label label-accent" style={{ marginBottom: '10px' }}>Input</span>
          <h1 style={{ fontSize: 'clamp(1.7rem, 4vw, 2.4rem)', textTransform: 'uppercase' }}>
            New Scan
          </h1>
          <p className="mono" style={{ marginTop: '8px' }}>
            JPEG · PNG · WEBP — MAX 10MB — DECODED IN MEMORY, NEVER WRITTEN TO DISK
          </p>
        </div>
        <span className="label">02 Sources</span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '18px',
        marginBottom: '24px',
      }}>
        <div className="fade-in stagger-1">
          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            justifyContent: 'space-between',
            marginBottom: '10px',
          }}>
            <span className="label">Source 01 — Face</span>
            <span className="label">Optional</span>
          </div>
          <PhotoUpload
            label="Face photo"
            description="Front-facing, well lit"
            onFileSelect={setFaceFile}
          />
        </div>

        <div className="fade-in stagger-2">
          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            justifyContent: 'space-between',
            marginBottom: '10px',
          }}>
            <span className="label">Source 02 — Body</span>
            <span className="label">Optional</span>
          </div>
          <PhotoUpload
            label="Full-body photo"
            description="Standing, front-facing"
            onFileSelect={setBodyFile}
          />
        </div>
      </div>

      <Frame
        className="fade-in stagger-3"
        label="Capture guidance"
        slug="04 Notes"
        style={{ marginBottom: '32px' }}
      >
        <ul style={{ listStyle: 'none', display: 'grid', gap: '9px' }}>
          {TIPS.map((tip, i) => (
            <li
              key={i}
              style={{
                display: 'flex',
                gap: '12px',
                fontSize: '0.85rem',
                color: 'var(--text-muted)',
              }}
            >
              <span className="mono" style={{ color: 'var(--accent)', flexShrink: 0 }}>
                {String(i + 1).padStart(2, '0')}
              </span>
              {tip}
            </li>
          ))}
        </ul>
      </Frame>

      <div className="fade-in stagger-4" style={{ textAlign: 'center' }}>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleAnalyze}
          disabled={!canSubmit}
          style={{ padding: '16px 40px', fontSize: '0.8rem' }}
        >
          {loading ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span className="spinner" style={{ width: '16px', height: '16px' }} />
              Analysing…
            </span>
          ) : 'Run Analysis'}
        </button>

        <p className="mono" style={{ marginTop: '14px' }}>
          {loading
            ? 'LANDMARKS · CLUSTERING · SCORING — THIS TAKES A MOMENT'
            : (!faceFile && !bodyFile)
              ? 'AWAITING AT LEAST ONE SOURCE'
              : 'READY'}
        </p>
      </div>
    </div>
  );
}
