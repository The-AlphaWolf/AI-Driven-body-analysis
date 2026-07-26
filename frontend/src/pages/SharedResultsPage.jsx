import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import AnalysisReport from '../components/AnalysisReport';
import { SkeletonResults } from '../components/Skeleton';
import { Frame } from '../components/Hud';
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
      <div className="container" style={{ padding: '80px 28px', maxWidth: '620px' }}>
        <Frame style={{ padding: '48px 28px', textAlign: 'center' }}>
          <span className="label" style={{ color: 'var(--danger)', marginBottom: '14px' }}>
            Link Revoked
          </span>
          <h2 style={{ textTransform: 'uppercase', marginBottom: '10px' }}>Unavailable</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '26px' }}>
            {error || 'This share link is not valid or has been revoked.'}
          </p>
          <Link to="/" className="btn btn-primary">Try StyleSense AI</Link>
        </Frame>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '48px 28px 80px', maxWidth: '1040px' }}>
      <div className="section-head fade-in">
        <div>
          <span className="label label-accent" style={{ marginBottom: '10px' }}>Shared Report</span>
          <h1 style={{ fontSize: 'clamp(1.7rem, 4vw, 2.4rem)', textTransform: 'uppercase' }}>
            Style Analysis
          </h1>
          <p className="mono" style={{ marginTop: '8px' }}>READ-ONLY — NO PHOTO INCLUDED</p>
        </div>
        <span className="label">
          {new Date(analysis.created_at).toLocaleDateString('en-GB', {
            year: 'numeric', month: '2-digit', day: '2-digit',
          })}
        </span>
      </div>

      <AnalysisReport analysis={analysis} />

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '40px', flexWrap: 'wrap' }}>
        <button type="button" onClick={download} disabled={downloading} className="btn btn-secondary">
          {downloading ? 'Preparing…' : 'Download PDF'}
        </button>
        <Link to="/register" className="btn btn-primary">Analyse Your Own Photo</Link>
      </div>
    </div>
  );
}
