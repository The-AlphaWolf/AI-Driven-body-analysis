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
      addToast('Logged out successfully', 'success');
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
      background: 'var(--color-card)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid var(--color-border)',
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px',
      }}>
        {/* Logo */}
        <Link to="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontWeight: 700,
          fontSize: '1.2rem',
          color: 'var(--color-text)',
          textDecoration: 'none',
        }}>
          <span style={{
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontSize: '1.4rem',
          }}>✦</span>
          <span>StyleSense<span style={{
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}> AI</span></span>
        </Link>

        {/* Navigation Links */}
        <div className="nav-links" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {user ? (
            <>
              <Link to="/analyze" className="btn btn-primary" style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
                ✨ New Analysis
              </Link>
              <Link to="/dashboard" className="btn btn-secondary" style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
                Dashboard
              </Link>
              <Link to="/saved" className="btn btn-secondary" style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
                ❤️ Saved
              </Link>
              <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary" style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
                Sign In
              </Link>
              <Link to="/register" className="btn btn-primary" style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
