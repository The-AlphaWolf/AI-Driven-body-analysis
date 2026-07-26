import { useState } from 'react';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

/**
 * Keep / reject control for a single recommendation.
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

  const button = (kind, glyph, label, activeColor) => {
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
          width: '26px',
          height: '26px',
          display: 'grid',
          placeItems: 'center',
          background: active ? `color-mix(in srgb, ${activeColor} 14%, transparent)` : 'transparent',
          border: `1px solid ${active ? activeColor : 'var(--line-mid)'}`,
          color: active ? activeColor : 'var(--text-dim)',
          cursor: pending ? 'wait' : 'pointer',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.72rem',
          lineHeight: 1,
          opacity: pending ? 0.5 : 1,
          transition: 'border-color 0.15s ease, color 0.15s ease, background 0.15s ease',
        }}
      >
        {glyph}
      </button>
    );
  };

  return (
    <div style={{ display: 'flex', gap: '5px', flexShrink: 0 }}>
      {button('like', '+', 'Keep this recommendation', 'var(--ok)')}
      {button('dislike', '−', 'Not for me', 'var(--danger)')}
    </div>
  );
}
