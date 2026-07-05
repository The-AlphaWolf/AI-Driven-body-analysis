import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [deleting, setDeleting] = useState(null);
  const { addToast } = useToast();

  const fetchHistory = async (p = 1) => {
    try {
      const data = await api.getHistory(p);
      setAnalyses(data.analyses);
      setTotal(data.total);
      setPage(data.page);
      setPages(data.pages);
    } catch (err) {
      addToast('Failed to load history', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this analysis?')) return;
    setDeleting(id);
    try {
      await api.deleteAnalysis(id);
      addToast('Analysis deleted', 'success');
      fetchHistory(page);
    } catch {
      addToast('Failed to delete', 'error');
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '48px 24px' }}>
      <div className="fade-in" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '4px' }}>
            <span style={{
              background: 'var(--gradient-primary)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>Dashboard</span>
          </h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
            {total} analysis{total !== 1 ? 'es' : ''} saved
          </p>
        </div>
        <Link to="/analyze" className="btn btn-primary">✨ New Analysis</Link>
      </div>

      {/* Empty state */}
      {analyses.length === 0 ? (
        <div className="glass-card fade-in" style={{ textAlign: 'center', padding: '60px 24px' }}>
          <span style={{ fontSize: '3rem', display: 'block', marginBottom: '16px' }}>📸</span>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '8px' }}>No analyses yet</h2>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: '24px' }}>
            Upload your first photo to get personalized style recommendations
          </p>
          <Link to="/analyze" className="btn btn-primary">Get Started</Link>
        </div>
      ) : (
        <>
          {/* Analysis cards grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '20px',
            marginBottom: '32px',
          }}>
            {analyses.map((a, i) => (
              <div
                key={a.id}
                className="glass-card fade-in"
                style={{
                  padding: '20px',
                  animationDelay: `${i * 0.05}s`,
                  transition: 'transform 0.2s ease',
                  cursor: 'pointer',
                  position: 'relative',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-3px)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; }}
              >
                <Link to={`/results/${a.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  {/* Date */}
                  <p style={{ fontSize: '0.8rem', color: 'var(--color-text-dim)', marginBottom: '12px' }}>
                    {new Date(a.created_at).toLocaleDateString('en-US', {
                      month: 'short', day: 'numeric', year: 'numeric',
                      hour: '2-digit', minute: '2-digit',
                    })}
                  </p>

                  {/* Badges */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
                    {a.face_shape && (
                      <span className="badge badge-primary" style={{ textTransform: 'capitalize' }}>
                        👤 {a.face_shape}
                      </span>
                    )}
                    {a.body_shape && (
                      <span className="badge badge-accent" style={{ textTransform: 'capitalize' }}>
                        📐 {a.body_shape.replace('_', ' ')}
                      </span>
                    )}
                  </div>

                  {/* Skin info */}
                  {a.skin_depth && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        border: '1px solid var(--color-border)',
                        background: 'var(--color-surface)',
                      }} />
                      <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                        {a.skin_depth} • {a.skin_undertone}
                      </span>
                    </div>
                  )}
                </Link>

                {/* Delete button */}
                <button
                  onClick={(e) => { e.stopPropagation(); handleDelete(a.id); }}
                  disabled={deleting === a.id}
                  style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--color-text-dim)',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    padding: '4px',
                    borderRadius: '4px',
                    transition: 'color 0.2s',
                  }}
                  onMouseEnter={(e) => { e.target.style.color = 'var(--color-error)'; }}
                  onMouseLeave={(e) => { e.target.style.color = 'var(--color-text-dim)'; }}
                  title="Delete analysis"
                >
                  {deleting === a.id ? '...' : '🗑'}
                </button>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}>
              {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => { setLoading(true); fetchHistory(p); }}
                  className={p === page ? 'btn btn-primary' : 'btn btn-secondary'}
                  style={{ padding: '8px 16px', fontSize: '0.85rem', minWidth: '40px' }}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
