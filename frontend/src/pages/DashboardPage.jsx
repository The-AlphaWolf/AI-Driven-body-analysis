import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import Thumbnail from '../components/Thumbnail';
import { SkeletonGrid } from '../components/Skeleton';
import { Frame } from '../components/Hud';
import api from '../services/api';

const titleCase = (value) => (value || '').replace(/_/g, ' ');

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [deleting, setDeleting] = useState(null);
  const { addToast } = useToast();

  const fetchHistory = useCallback(async (p = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHistory(p);
      setAnalyses(data.analyses);
      setTotal(data.total);
      setPage(data.page);
      setPages(data.pages);
    } catch (err) {
      // A failed load leaves the page with nothing to show, so it gets an
      // inline retry rather than a toast that vanishes.
      setError(err.message || 'Could not load your analyses');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleDelete = async (id) => {
    if (!confirm('Delete this analysis? This cannot be undone.')) return;
    setDeleting(id);
    try {
      await api.deleteAnalysis(id);
      addToast('Analysis deleted', 'success');
      fetchHistory(page);
    } catch {
      addToast('Delete failed', 'error');
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '48px 28px' }}>
        <div style={{ marginBottom: '32px', maxWidth: '260px' }}>
          <div className="skeleton skeleton-line" style={{ height: '26px', marginBottom: '10px' }} />
          <div className="skeleton skeleton-line" style={{ width: '50%' }} />
        </div>
        <SkeletonGrid count={6} lines={3} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ padding: '48px 28px', maxWidth: '620px' }}>
        <Frame className="fade-in" style={{ padding: '48px 26px', textAlign: 'center' }}>
          <span className="label" style={{ color: 'var(--danger)', marginBottom: '14px' }}>
            Load failed
          </span>
          <h2 style={{ textTransform: 'uppercase', marginBottom: '10px' }}>Archive unreachable</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '26px' }}>
            {error}
          </p>
          <button type="button" onClick={() => fetchHistory(page)} className="btn btn-primary">
            Retry
          </button>
        </Frame>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '48px 28px 80px' }}>
      <div className="section-head fade-in">
        <div>
          <span className="label label-accent" style={{ marginBottom: '10px' }}>Archive</span>
          <h1 style={{ fontSize: 'clamp(1.7rem, 4vw, 2.4rem)', textTransform: 'uppercase' }}>
            Your Reports
          </h1>
          <p className="mono" style={{ marginTop: '8px' }}>
            {String(total).padStart(2, '0')} {total === 1 ? 'RECORD' : 'RECORDS'} STORED
          </p>
        </div>
        <Link to="/analyze" className="btn btn-primary">New Scan</Link>
      </div>

      {analyses.length === 0 ? (
        <Frame className="fade-in" style={{ padding: '60px 26px', textAlign: 'center' }}>
          <span className="label label-accent" style={{ marginBottom: '14px' }}>Empty</span>
          <h2 style={{ textTransform: 'uppercase', marginBottom: '10px' }}>No reports yet</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '26px' }}>
            Upload a photo to generate your first style analysis.
          </p>
          <Link to="/analyze" className="btn btn-primary">Run First Scan</Link>
        </Frame>
      ) : (
        <>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))',
            gap: '16px',
            marginBottom: '32px',
          }}>
            {analyses.map((a, i) => {
              const stamp = new Date(a.created_at);
              return (
                <Frame
                  key={a.id}
                  hover
                  className="fade-in"
                  style={{ padding: '18px', animationDelay: `${i * 0.04}s`, position: 'relative' }}
                >
                  <Link to={`/results/${a.id}`} style={{ color: 'inherit', display: 'block' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'baseline',
                      justifyContent: 'space-between',
                      gap: '10px',
                      marginBottom: '16px',
                      paddingRight: '22px',
                    }}>
                      <span className="label">
                        {stamp.toLocaleDateString('en-GB', {
                          year: 'numeric', month: '2-digit', day: '2-digit',
                        })}
                      </span>
                      <span className="label">
                        {stamp.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                      {a.thumbnail_url && <Thumbnail analysisId={a.id} size={62} />}

                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
                          {a.face_shape && (
                            <span className="tag tag-accent">{titleCase(a.face_shape)}</span>
                          )}
                          {a.body_shape && (
                            <span className="tag">{titleCase(a.body_shape)}</span>
                          )}
                        </div>

                        {a.skin_depth && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
                            <span
                              aria-hidden="true"
                              style={{
                                width: '14px',
                                height: '14px',
                                background: a.skin_hex_color || 'transparent',
                                border: '1px solid rgba(255,255,255,0.18)',
                                flexShrink: 0,
                              }}
                            />
                            <span className="mono">
                              {`${a.skin_depth} · ${a.skin_undertone}`.toUpperCase()}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </Link>

                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); handleDelete(a.id); }}
                    disabled={deleting === a.id}
                    title="Delete this analysis"
                    aria-label="Delete this analysis"
                    style={{
                      position: 'absolute',
                      top: '14px',
                      right: '14px',
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-dim)',
                      cursor: 'pointer',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.75rem',
                      padding: '2px 4px',
                      lineHeight: 1,
                      transition: 'color 0.18s ease',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--danger)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-dim)'; }}
                  >
                    {deleting === a.id ? '···' : '✕'}
                  </button>
                </Frame>
              );
            })}
          </div>

          {pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '6px', flexWrap: 'wrap' }}>
              {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => fetchHistory(p)}
                  aria-current={p === page ? 'page' : undefined}
                  className={p === page ? 'btn btn-primary' : 'btn btn-secondary'}
                  style={{ padding: '8px 14px', minWidth: '38px' }}
                >
                  {String(p).padStart(2, '0')}
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
