import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      addToast('Session ended', 'success');
      navigate('/');
    } catch {
      addToast('Logout failed', 'error');
    }
  };

  return (
    <nav style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'rgba(8, 3, 6, 0.82)',
      backdropFilter: 'blur(18px)',
      WebkitBackdropFilter: 'blur(18px)',
      borderBottom: '1px solid var(--line)',
    }}>
      {/* Layout lives in CSS, not inline, so the narrow-width rules that stack
          this into two rows can actually win the cascade. */}
      <div className="container nav-bar">
        {/* Wordmark — the frame motif, then the name in monospace. */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '11px', color: 'var(--text)' }}>
          <svg width="18" height="18" viewBox="0 0 32 32" aria-hidden="true" style={{ flexShrink: 0 }}>
            <g stroke="var(--accent)" strokeWidth="2.4" fill="none" strokeLinecap="square">
              <path d="M4 10V4h6M22 4h6v6M28 22v6h-6M10 28H4v-6" />
            </g>
            <circle cx="16" cy="16" r="3.4" fill="var(--accent)" />
          </svg>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.8rem',
            fontWeight: 700,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
          }}>
            StyleSense<span style={{ color: 'var(--accent)' }}>//</span>AI
          </span>
        </Link>

        <div className="nav-links" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {user ? (
            <>
              <Link to="/analyze" className="btn btn-primary">New Scan</Link>
              <Link to="/dashboard" className="btn btn-secondary">Archive</Link>
              <Link to="/saved" className="btn btn-secondary">Kept</Link>
              <button type="button" onClick={handleLogout} className="btn btn-secondary">
                Exit
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary">Sign In</Link>
              <Link to="/register" className="btn btn-primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
