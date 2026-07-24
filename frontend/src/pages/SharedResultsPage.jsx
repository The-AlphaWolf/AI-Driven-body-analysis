import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import AnalysisReport from '../components/AnalysisReport';
import { SkeletonResults } from '../components/Skeleton';
import api from '../services/api';

/**
 * Public, read-only view of a shared analysis.
 *
 * No auth, no feedback controls, and the payload carries no photo — a
 * stranger holding the link should be able to read the advice and nothing
 * more.
 */
export default function SharedResultsPage() {
  const { token } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getSharedAnalysis(token)
      .then((data) => setAnalysis(data.analysis))
      .catch((err) => setError(err.message || 'This link is no longer available'))
      .finally(() => setLoading(false));
  }, [token]);

  const download = async () => {
    setDownloading(true);
    try {
      await api.downloadReport(null, { shareToken: token });
    } catch {
      setError('Could not generate the PDF');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) return <SkeletonResults />;

  if (error || !analysis) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '80px 24px' }}>
        <span style={{ fontSize: '3rem', display: 'block', marginBottom: '16px' }}>🔗</span>
        <h2 style={{ marginBottom: '8px' }}>Link unavailable</h2>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '24px' }}>
          {error || 'This share link is not valid or has been revoked.'}
        </p>
        <Link to="/" className="btn btn-primary">Try StyleSense AI</Link>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '48px 24px', maxWidth: '1000px' }}>
      <div className="fade-in" style={{ textAlign: 'center', marginBottom: '40px' }}>
        <span className="badge badge-primary" style={{ marginBottom: '12px', display: 'inline-block' }}>
          Shared style report
        </span>
        <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>
          A Style <span style={{
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>Analysis</span>
        </h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
          {new Date(analysis.created_at).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric',
          })}
        </p>
      </div>

      <AnalysisReport analysis={analysis} />

      <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '40px', flexWrap: 'wrap' }}>
        <button type="button" onClick={download} disabled={downloading} className="btn btn-secondary">
          {downloading ? 'Preparing...' : '📄 Download PDF'}
        </button>
        <Link to="/register" className="btn btn-primary">✨ Analyze your own photo</Link>
      </div>
    </div>
  );
}
