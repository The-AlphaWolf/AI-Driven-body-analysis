import { useState } from 'react';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

/**
 * Like / dislike control for a single recommendation.
 *
 * Updates optimistically — the verdict is a preference, so a failed write is
 * worth a toast but not worth blocking the card behind a spinner. On failure
 * the button snaps back to the server's last known state.
 */
export default function FeedbackButtons({ analysisId, category, recommendation, verdict, onChange }) {
  const [pending, setPending] = useState(false);
  const { addToast } = useToast();

  const send = async (next) => {
    // Clicking the active verdict clears it.
    const value = verdict === next ? null : next;
    const previous = verdict;

    setPending(true);
    onChange(value);

    try {
      await api.setFeedback(analysisId, category, recommendation, value);
    } catch {
      onChange(previous);
      addToast('Could not save your feedback', 'error');
    } finally {
      setPending(false);
    }
  };

  const button = (kind, icon, label) => {
    const active = verdict === kind;
    return (
      <button
        type="button"
        onClick={() => send(kind)}
        disabled={pending}
        aria-pressed={active}
        aria-label={label}
        title={label}
        style={{
          background: active ? 'var(--color-surface-hover, rgba(255,255,255,0.08))' : 'transparent',
          border: `1px solid ${active ? 'var(--color-primary)' : 'var(--color-border)'}`,
          borderRadius: '999px',
          cursor: pending ? 'wait' : 'pointer',
          padding: '4px 10px',
          fontSize: '0.85rem',
          lineHeight: 1.2,
          opacity: pending ? 0.6 : 1,
          filter: active ? 'none' : 'grayscale(1)',
          transition: 'border-color 0.15s, filter 0.15s',
        }}
      >
        {icon}
      </button>
    );
  };

  return (
    <div style={{ display: 'flex', gap: '6px' }}>
      {button('like', '❤️', 'Save this recommendation')}
      {button('dislike', '👎', 'Not for me')}
    </div>
  );
}
