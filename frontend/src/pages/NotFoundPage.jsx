import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Frame } from '../components/Hud';

/**
 * Catch-all for unknown paths.
 *
 * The host rewrites every unmatched URL to index.html so the router can own
 * client-side routes, which means a typo used to render an empty page rather
 * than anything explaining itself.
 */
export default function NotFoundPage() {
  const { user } = useAuth();

  return (
    <div style={{
      minHeight: 'calc(100vh - var(--nav-h))',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
    }}>
      <Frame className="fade-in" style={{ width: '100%', maxWidth: '520px', padding: '46px 30px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          paddingBottom: '18px',
          marginBottom: '28px',
          borderBottom: '1px solid var(--line)',
        }}>
          <span className="label label-accent">Error</span>
          <span className="label">No Route</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(3rem, 12vw, 5rem)',
          color: 'var(--accent)',
          lineHeight: 1,
          marginBottom: '16px',
        }}>
          404
        </h1>

        <h2 style={{ fontSize: '1.15rem', textTransform: 'uppercase', marginBottom: '10px' }}>
          Page not found
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '30px' }}>
          That address does not match anything here. It may have been a typo, or
          a link to something that has since been deleted.
        </p>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <Link to="/" className="btn btn-primary">Home</Link>
          {user
            ? <Link to="/dashboard" className="btn btn-secondary">Archive</Link>
            : <Link to="/login" className="btn btn-secondary">Sign In</Link>}
        </div>
      </Frame>
    </div>
  );
}
