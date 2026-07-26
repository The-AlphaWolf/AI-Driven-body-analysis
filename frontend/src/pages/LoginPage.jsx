import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Frame } from '../components/Hud';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      addToast('Both fields are required', 'error');
      return;
    }
    setLoading(true);
    try {
      await login(email, password);
      addToast('Signed in', 'success');
      navigate('/dashboard');
    } catch (err) {
      addToast(err.message || 'Sign in failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: 'calc(100vh - var(--nav-h))',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
    }}>
      <Frame className="fade-in" style={{ width: '100%', maxWidth: '420px', padding: '38px 30px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          paddingBottom: '18px',
          marginBottom: '26px',
          borderBottom: '1px solid var(--line)',
        }}>
          <span className="label label-accent">Access</span>
          <span className="label">Auth / JWT</span>
        </div>

        <h1 style={{ fontSize: '1.5rem', textTransform: 'uppercase', marginBottom: '26px' }}>
          Sign In
        </h1>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '18px' }}>
            <label className="input-label" htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              className="input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div style={{ marginBottom: '26px' }}>
            <label className="input-label" htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className="input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', padding: '14px' }}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="spinner" style={{ width: '15px', height: '15px' }} />
                Authenticating…
              </span>
            ) : 'Sign In'}
          </button>
        </form>

        <p className="mono" style={{ textAlign: 'center', marginTop: '24px' }}>
          NO ACCOUNT? <Link to="/register">CREATE ONE</Link>
        </p>
      </Frame>
    </div>
  );
}
