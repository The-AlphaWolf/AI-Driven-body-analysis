import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Frame } from '../components/Hud';

const LEVELS = [
  { label: 'Weak', color: 'var(--danger)' },
  { label: 'Fair', color: 'var(--warn)' },
  { label: 'Good', color: 'var(--accent-soft)' },
  { label: 'Strong', color: 'var(--ok)' },
];

function strengthOf(pwd) {
  if (!pwd) return { level: 0, label: '', color: 'transparent' };
  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  const level = LEVELS[score - 1];
  return level ? { level: score, ...level } : { level: 0, label: '', color: 'transparent' };
}

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const strength = strengthOf(password);
  const mismatch = confirm && confirm !== password;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || !confirm) {
      addToast('All fields are required', 'error');
      return;
    }
    if (password !== confirm) {
      addToast('Passwords do not match', 'error');
      return;
    }
    if (password.length < 8) {
      addToast('Password must be at least 8 characters', 'error');
      return;
    }

    setLoading(true);
    try {
      await register(email, password);
      addToast('Account created', 'success');
      navigate('/analyze');
    } catch (err) {
      addToast(err.message || 'Registration failed', 'error');
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
          <span className="label label-accent">Register</span>
          <span className="label">Free / No Card</span>
        </div>

        <h1 style={{ fontSize: '1.5rem', textTransform: 'uppercase', marginBottom: '26px' }}>
          Create Account
        </h1>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '18px' }}>
            <label className="input-label" htmlFor="reg-email">Email</label>
            <input
              id="reg-email"
              type="email"
              className="input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div style={{ marginBottom: password ? '10px' : '18px' }}>
            <label className="input-label" htmlFor="reg-password">Password</label>
            <input
              id="reg-password"
              type="password"
              className="input"
              placeholder="Min 8 chars, 1 letter + 1 number"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              disabled={loading}
            />
          </div>

          {password && (
            <div style={{ marginBottom: '18px' }}>
              <div style={{ height: '3px', background: 'rgba(255,255,255,0.07)', marginBottom: '7px' }}>
                <div style={{
                  height: '100%',
                  width: `${strength.level * 25}%`,
                  background: strength.color,
                  transition: 'width 0.3s ease, background 0.3s ease',
                }} />
              </div>
              <span className="label" style={{ color: strength.color }}>{strength.label}</span>
            </div>
          )}

          <div style={{ marginBottom: '26px' }}>
            <label className="input-label" htmlFor="reg-confirm">Confirm Password</label>
            <input
              id="reg-confirm"
              type="password"
              className="input"
              placeholder="••••••••"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
              disabled={loading}
              aria-invalid={mismatch || undefined}
              style={mismatch ? { borderColor: 'var(--danger)' } : undefined}
            />
            {mismatch && (
              <span className="label" style={{ color: 'var(--danger)', marginTop: '7px' }}>
                Passwords do not match
              </span>
            )}
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
                Creating…
              </span>
            ) : 'Create Account'}
          </button>
        </form>

        <p className="mono" style={{ textAlign: 'center', marginTop: '24px' }}>
          ALREADY REGISTERED? <Link to="/login">SIGN IN</Link>
        </p>
      </Frame>
    </div>
  );
}
