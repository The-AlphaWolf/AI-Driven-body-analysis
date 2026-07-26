import { useCallback, useEffect, useState } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import AnalysisReport from '../components/AnalysisReport';
import ShareControls from '../components/ShareControls';
import { SkeletonResults } from '../components/Skeleton';
import { Frame } from '../components/Hud';
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

  if (loading) return <SkeletonResults />;

  if (!analysis) {
    return (
      <div className="container" style={{ padding: '80px 28px', maxWidth: '620px' }}>
        <Frame style={{ padding: '48px 28px', textAlign: 'center' }}>
          <span className="label label-accent" style={{ marginBottom: '14px' }}>Error 404</span>
          <h2 style={{ textTransform: 'uppercase', marginBottom: '10px' }}>Report not found</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '26px' }}>
            It may have been deleted, or it belongs to another account.
          </p>
          <Link to="/analyze" className="btn btn-primary">New Scan</Link>
        </Frame>
      </div>
    );
  }

  const stamp = new Date(analysis.created_at);

  return (
    <div className="container" style={{ padding: '48px 28px 80px', maxWidth: '1040px' }}>
      <div className="section-head fade-in">
        <div>
          <span className="label label-accent" style={{ marginBottom: '10px' }}>Style Report</span>
          <h1 style={{ fontSize: 'clamp(1.7rem, 4vw, 2.4rem)', textTransform: 'uppercase' }}>
            Your Analysis
          </h1>
        </div>
        <span className="label">
          {stamp.toLocaleDateString('en-GB', { year: 'numeric', month: '2-digit', day: '2-digit' })}
          {' · '}
          {stamp.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
        </span>
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

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '28px', flexWrap: 'wrap' }}>
        <Link to="/analyze" className="btn btn-primary">New Scan</Link>
        <Link to="/dashboard" className="btn btn-secondary">Archive</Link>
      </div>
    </div>
  );
}
