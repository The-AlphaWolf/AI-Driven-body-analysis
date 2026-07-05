import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import PhotoUpload from '../components/PhotoUpload';
import api from '../services/api';

export default function AnalyzePage() {
  const [faceFile, setFaceFile] = useState(null);
  const [bodyFile, setBodyFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();
  const navigate = useNavigate();

  const canSubmit = (faceFile || bodyFile) && !loading;

  const handleAnalyze = async () => {
    if (!faceFile && !bodyFile) {
      addToast('Please upload at least one photo', 'error');
      return;
    }

    setLoading(true);
    try {
      const data = await api.analyze(faceFile, bodyFile);
      addToast('Analysis complete!', 'success');
      navigate(`/results/${data.analysis.id}`, { state: { analysis: data.analysis } });
    } catch (err) {
      addToast(err.message || 'Analysis failed. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '48px 24px', maxWidth: '800px' }}>
      <div className="fade-in" style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '12px' }}>
          <span style={{
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>✨ New Analysis</span>
        </h1>
        <p style={{ color: 'var(--color-text-muted)', maxWidth: '500px', margin: '0 auto' }}>
          Upload a face photo for shape & skin tone analysis, a full-body photo for body proportion analysis, or both for complete recommendations.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        <div className="fade-in stagger-1">
          <h3 style={{ fontSize: '1rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            👤 Face Photo
            <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>Optional</span>
          </h3>
          <PhotoUpload
            label="Upload Face Photo"
            description="Clear, front-facing photo with good lighting"
            onFileSelect={setFaceFile}
          />
        </div>

        <div className="fade-in stagger-2">
          <h3 style={{ fontSize: '1rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🧍 Full Body Photo
            <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>Optional</span>
          </h3>
          <PhotoUpload
            label="Upload Body Photo"
            description="Full-body, front-facing, standing pose"
            onFileSelect={setBodyFile}
          />
        </div>
      </div>

      {/* Tips */}
      <div className="glass-card fade-in stagger-3" style={{ padding: '20px 24px', marginBottom: '32px' }}>
        <h4 style={{ fontSize: '0.9rem', marginBottom: '10px', color: 'var(--color-primary-light)' }}>📸 Tips for Best Results</h4>
        <ul style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', listStyle: 'none', display: 'grid', gap: '6px' }}>
          <li>• Good, even lighting — avoid harsh shadows or backlighting</li>
          <li>• Face camera directly — avoid tilting or turning your head</li>
          <li>• For body photo — stand naturally with arms slightly away from body</li>
          <li>• Plain background works best for body proportion detection</li>
        </ul>
      </div>

      {/* Submit Button */}
      <div className="fade-in stagger-4" style={{ textAlign: 'center' }}>
        <button
          className="btn btn-primary"
          onClick={handleAnalyze}
          disabled={!canSubmit}
          style={{ padding: '16px 48px', fontSize: '1.05rem' }}
        >
          {loading ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }} />
              Analyzing... This may take a moment
            </span>
          ) : (
            '🔍 Analyze My Style'
          )}
        </button>

        {!faceFile && !bodyFile && (
          <p style={{ marginTop: '12px', fontSize: '0.85rem', color: 'var(--color-text-dim)' }}>
            Upload at least one photo to begin
          </p>
        )}
      </div>
    </div>
  );
}
