import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  // Password strength indicator
  const getStrength = (pwd) => {
    if (!pwd) return { level: 0, label: '', color: 'transparent' };
    let score = 0;
    if (pwd.length >= 8) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    const levels = [
      { level: 1, label: 'Weak', color: 'var(--color-error)' },
      { level: 2, label: 'Fair', color: 'var(--color-warning)' },
      { level: 3, label: 'Good', color: 'var(--color-primary-light)' },
      { level: 4, label: 'Strong', color: 'var(--color-success)' },
    ];
    return levels[score - 1] || { level: 0, label: '', color: 'transparent' };
  };

  const strength = getStrength(password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password || !confirm) {
      addToast('Please fill in all fields', 'error');
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
      addToast('Account created! Welcome to StyleSense AI', 'success');
      navigate('/analyze');
    } catch (err) {
      addToast(err.message || 'Registration failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: 'calc(100vh - 64px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 24px',
    }}>
      <div className="glass-card fade-in" style={{ width: '100%', maxWidth: '420px', padding: '40px 32px' }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{ fontSize: '1.8rem', marginBottom: '8px' }}>Create Account</h1>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
            Join StyleSense AI and discover your perfect style
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label className="input-label">Email</label>
            <input
              type="email"
              className="input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div style={{ marginBottom: '6px' }}>
            <label className="input-label">Password</label>
            <input
              type="password"
              className="input"
              placeholder="Min 8 chars, 1 letter + 1 number"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              disabled={loading}
            />
          </div>

          {/* Password strength bar */}
          {password && (
            <div style={{ marginBottom: '20px' }}>
              <div style={{
                height: '4px',
                background: 'var(--color-border)',
                borderRadius: 'var(--radius-full)',
                overflow: 'hidden',
                marginBottom: '6px',
              }}>
                <div style={{
                  height: '100%',
                  width: `${strength.level * 25}%`,
                  background: strength.color,
                  borderRadius: 'var(--radius-full)',
                  transition: 'all 0.3s ease',
                }} />
              </div>
              <span style={{ fontSize: '0.75rem', color: strength.color }}>{strength.label}</span>
            </div>
          )}

          <div style={{ marginBottom: '28px' }}>
            <label className="input-label">Confirm Password</label>
            <input
              type="password"
              className="input"
              placeholder="••••••••"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
              disabled={loading}
              style={confirm && confirm !== password ? { borderColor: 'var(--color-error)' } : {}}
            />
            {confirm && confirm !== password && (
              <p style={{ fontSize: '0.8rem', color: 'var(--color-error)', marginTop: '4px' }}>
                Passwords do not match
              </p>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', padding: '14px' }}
          >
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} />
                Creating account...
              </span>
            ) : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ fontWeight: 600 }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
