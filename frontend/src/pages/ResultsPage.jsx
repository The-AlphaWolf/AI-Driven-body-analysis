import { useCallback, useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import AnalysisReport from '../components/AnalysisReport';
import ShareControls from '../components/ShareControls';
import api from '../services/api';

export default function ResultsPage() {
  const { id } = useParams();
  const location = useLocation();
  const [analysis, setAnalysis] = useState(location.state?.analysis || null);
  const [loading, setLoading] = useState(!analysis);
  const [feedback, setFeedback] = useState({});
  const [shareToken, setShareToken] = useState(location.state?.analysis?.share_token || null);

  useEffect(() => {
    if (!analysis && id) {
      api.getAnalysis(id)
        .then((data) => {
          setAnalysis(data.analysis);
          setShareToken(data.analysis.share_token || null);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [id, analysis]);

  const analysisId = analysis?.id || id;

  useEffect(() => {
    if (!analysisId) return;
    api.getFeedback(analysisId)
      .then((data) => setFeedback(data.feedback || {}))
      .catch(() => {
        // Feedback is additive — the results are still worth showing without it.
      });
  }, [analysisId]);

  const updateFeedback = useCallback((key, verdict) => {
    setFeedback((current) => {
      const next = { ...current };
      if (verdict === null) delete next[key];
      else next[key] = verdict;
      return next;
    });
  }, []);

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

  return (
    <div className="container" style={{ padding: '48px 24px', maxWidth: '1000px' }}>
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
            year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit',
          })}
        </p>
      </div>

      <AnalysisReport
        analysis={analysis}
        analysisId={analysisId}
        feedback={feedback}
        onFeedbackChange={updateFeedback}
      />

      <ShareControls
        analysisId={analysisId}
        shareToken={shareToken}
        onShareChange={setShareToken}
      />

      <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '32px', flexWrap: 'wrap' }}>
        <Link to="/analyze" className="btn btn-primary">✨ New Analysis</Link>
        <Link to="/dashboard" className="btn btn-secondary">📊 Dashboard</Link>
      </div>
    </div>
  );
}
