import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import { SkeletonGrid } from '../components/Skeleton';
import api from '../services/api';

const CATEGORY_ICONS = {
  necklines: '👔',
  silhouettes: '👗',
  colors: '🎨',
  patterns: '🔲',
  accessories: '💍',
  hairstyles: '💇',
};

const CATEGORY_LABELS = {
  necklines: 'Necklines',
  silhouettes: 'Silhouettes & Fits',
  colors: 'Color Palette',
  patterns: 'Patterns',
  accessories: 'Accessories',
  hairstyles: 'Hairstyles',
};

export default function SavedPage() {
  const [saved, setSaved] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [removing, setRemoving] = useState(null);
  const { addToast } = useToast();

  useEffect(() => {
    api.getSaved()
      .then((data) => {
        setSaved(data.saved);
        setTotal(data.total);
      })
      .catch(() => addToast('Failed to load saved items', 'error'))
      .finally(() => setLoading(false));
  }, [addToast]);

  const remove = async (item) => {
    setRemoving(item.id);
    try {
      await api.setFeedback(item.analysis_id, item.category, item.recommendation, null);
      setSaved((current) => current.filter((s) => s.id !== item.id));
      setTotal((t) => t - 1);
    } catch {
      addToast('Could not remove that', 'error');
    } finally {
      setRemoving(null);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '48px 24px', maxWidth: '900px' }}>
        <div style={{ marginBottom: '32px', maxWidth: '220px' }}>
          <div className="skeleton skeleton-line" style={{ height: '28px', marginBottom: '10px' }} />
          <div className="skeleton skeleton-line" style={{ width: '60%' }} />
        </div>
        <SkeletonGrid count={4} lines={2} minWidth="100%" />
      </div>
    );
  }

  // Group by category so the page reads like a wardrobe list, not a log.
  const grouped = {};
  saved.forEach((item) => {
    if (!grouped[item.category]) grouped[item.category] = [];
    grouped[item.category].push(item);
  });

  return (
    <div className="container" style={{ padding: '48px 24px', maxWidth: '900px' }}>
      <div className="fade-in" style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '4px' }}>
          <span style={{
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>Saved</span>
        </h1>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
          {total} recommendation{total !== 1 ? 's' : ''} you liked
        </p>
      </div>

      {saved.length === 0 ? (
        <div className="glass-card fade-in" style={{ textAlign: 'center', padding: '60px 24px' }}>
          <span style={{ fontSize: '3rem', display: 'block', marginBottom: '16px' }}>❤️</span>
          <h2 style={{ fontSize: '1.3rem', marginBottom: '8px' }}>Nothing saved yet</h2>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: '24px' }}>
            Tap the heart on any recommendation to keep it here
          </p>
          <Link to="/dashboard" className="btn btn-primary">Browse your analyses</Link>
        </div>
      ) : (
        Object.entries(grouped).map(([category, items]) => (
          <div key={category} style={{ marginBottom: '32px' }}>
            <h3 style={{
              fontSize: '1.1rem',
              marginBottom: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: 'var(--color-primary-light)',
            }}>
              <span>{CATEGORY_ICONS[category] || '📋'}</span>
              {CATEGORY_LABELS[category] || category}
            </h3>

            <div style={{ display: 'grid', gap: '12px' }}>
              {items.map((item) => (
                <div key={item.id} className="glass-card" style={{
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  flexWrap: 'wrap',
                }}>
                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <div style={{ fontSize: '0.95rem', marginBottom: '4px' }}>
                      {item.recommendation}
                    </div>
                    <Link
                      to={`/results/${item.analysis_id}`}
                      style={{ fontSize: '0.78rem', color: 'var(--color-text-dim)' }}
                    >
                      From your analysis on{' '}
                      {new Date(item.created_at).toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', year: 'numeric',
                      })}
                    </Link>
                  </div>

                  <button
                    type="button"
                    onClick={() => remove(item)}
                    disabled={removing === item.id}
                    className="btn btn-secondary"
                    style={{ padding: '6px 14px', fontSize: '0.8rem' }}
                  >
                    {removing === item.id ? '...' : 'Remove'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
