import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from '../context/ToastContext';
import { SkeletonGrid } from '../components/Skeleton';
import { Frame } from '../components/Hud';
import api from '../services/api';

const CATEGORY_LABELS = {
  necklines: 'Necklines',
  silhouettes: 'Silhouettes & Fits',
  colors: 'Colour Palette',
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
      .catch(() => addToast('Could not load kept items', 'error'))
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
      <div className="container" style={{ padding: '48px 28px', maxWidth: '900px' }}>
        <div style={{ marginBottom: '32px', maxWidth: '220px' }}>
          <div className="skeleton skeleton-line" style={{ height: '26px', marginBottom: '10px' }} />
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
    <div className="container" style={{ padding: '48px 28px 80px', maxWidth: '900px' }}>
      <div className="section-head fade-in">
        <div>
          <span className="label label-accent" style={{ marginBottom: '10px' }}>Kept</span>
          <h1 style={{ fontSize: 'clamp(1.7rem, 4vw, 2.4rem)', textTransform: 'uppercase' }}>
            Your Selections
          </h1>
          <p className="mono" style={{ marginTop: '8px' }}>
            {String(total).padStart(2, '0')} {total === 1 ? 'ITEM' : 'ITEMS'} KEPT
          </p>
        </div>
        <Link to="/analyze" className="btn btn-secondary">New Scan</Link>
      </div>

      {saved.length === 0 ? (
        <Frame className="fade-in" style={{ padding: '60px 26px', textAlign: 'center' }}>
          <span className="label label-accent" style={{ marginBottom: '14px' }}>Empty</span>
          <h2 style={{ textTransform: 'uppercase', marginBottom: '10px' }}>Nothing kept yet</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '26px' }}>
            Keep any recommendation on a report and it collects here.
          </p>
          <Link to="/dashboard" className="btn btn-primary">Browse Archive</Link>
        </Frame>
      ) : (
        Object.entries(grouped).map(([category, items]) => (
          <section key={category} style={{ marginBottom: '36px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'baseline',
              justifyContent: 'space-between',
              gap: '14px',
              marginBottom: '14px',
            }}>
              <h3 style={{
                fontSize: '0.95rem',
                textTransform: 'uppercase',
                color: 'var(--accent)',
                letterSpacing: '0.04em',
              }}>
                {CATEGORY_LABELS[category] || category}
              </h3>
              <span className="label">{String(items.length).padStart(2, '0')} Kept</span>
            </div>

            <div style={{ display: 'grid', gap: '10px' }}>
              {items.map((item) => (
                <Frame
                  key={item.id}
                  style={{
                    padding: '15px 18px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    flexWrap: 'wrap',
                  }}
                >
                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <div style={{
                      fontFamily: 'var(--font-display)',
                      fontWeight: 700,
                      fontSize: '0.92rem',
                      textTransform: 'uppercase',
                      marginBottom: '5px',
                    }}>
                      {item.recommendation}
                    </div>
                    <Link to={`/results/${item.analysis_id}`} className="mono">
                      FROM REPORT{' '}
                      {new Date(item.created_at).toLocaleDateString('en-GB', {
                        year: 'numeric', month: '2-digit', day: '2-digit',
                      })}
                    </Link>
                  </div>

                  <button
                    type="button"
                    onClick={() => remove(item)}
                    disabled={removing === item.id}
                    className="btn btn-secondary"
                    style={{ padding: '7px 14px' }}
                  >
                    {removing === item.id ? '···' : 'Remove'}
                  </button>
                </Frame>
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  );
}
