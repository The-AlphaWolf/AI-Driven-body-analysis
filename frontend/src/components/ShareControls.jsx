import { useState } from 'react';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

/**
 * Share link and PDF download for an analysis.
 *
 * Sharing is off until the owner turns it on, and the resulting page omits
 * the photo — a style report is meant to be forwarded, a face is not.
 */
export default function ShareControls({ analysisId, shareToken, onShareChange }) {
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const { addToast } = useToast();

  const shareUrl = shareToken ? `${window.location.origin}/s/${shareToken}` : null;

  const enable = async () => {
    setBusy(true);
    try {
      const data = await api.enableSharing(analysisId);
      onShareChange(data.share_token);
      addToast('Share link created', 'success');
    } catch {
      addToast('Could not create a share link', 'error');
    } finally {
      setBusy(false);
    }
  };

  const disable = async () => {
    if (!confirm('Revoke this link? Anyone you already sent it to will lose access.')) return;
    setBusy(true);
    try {
      await api.disableSharing(analysisId);
      onShareChange(null);
      addToast('Share link revoked', 'success');
    } catch {
      addToast('Could not revoke the link', 'error');
    } finally {
      setBusy(false);
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      addToast('Copy failed — select the link and copy it manually', 'error');
    }
  };

  const download = async () => {
    setBusy(true);
    try {
      await api.downloadReport(analysisId);
    } catch {
      addToast('Could not generate the PDF', 'error');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '20px', marginTop: '32px' }}>
      <div style={{
        display: 'flex',
        gap: '12px',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <button type="button" onClick={download} disabled={busy} className="btn btn-secondary">
          📄 Download PDF
        </button>

        {shareToken ? (
          <button type="button" onClick={disable} disabled={busy} className="btn btn-secondary">
            🔒 Stop sharing
          </button>
        ) : (
          <button type="button" onClick={enable} disabled={busy} className="btn btn-secondary">
            🔗 Create share link
          </button>
        )}
      </div>

      {shareUrl && (
        <div style={{ marginTop: '16px' }}>
          <div style={{
            display: 'flex',
            gap: '8px',
            alignItems: 'center',
            flexWrap: 'wrap',
          }}>
            <input
              readOnly
              value={shareUrl}
              onFocus={(e) => e.target.select()}
              style={{
                flex: 1,
                minWidth: '220px',
                padding: '8px 12px',
                fontSize: '0.8rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
                background: 'var(--color-surface)',
                color: 'var(--color-text-muted)',
              }}
            />
            <button type="button" onClick={copy} className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.8rem' }}>
              {copied ? '✓ Copied' : 'Copy'}
            </button>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', marginTop: '8px' }}>
            Anyone with this link can see your results. Your photo is not included.
          </p>
        </div>
      )}
    </div>
  );
}
