import { useState } from 'react';
import { useToast } from '../context/ToastContext';
import { Frame } from './Hud';
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
    <Frame label="Export" slug={shareToken ? 'Sharing On' : 'Sharing Off'} style={{ marginTop: '36px' }}>
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button type="button" onClick={download} disabled={busy} className="btn btn-secondary">
          Download PDF
        </button>

        {shareToken ? (
          <button type="button" onClick={disable} disabled={busy} className="btn btn-secondary">
            Revoke Link
          </button>
        ) : (
          <button type="button" onClick={enable} disabled={busy} className="btn btn-secondary">
            Create Share Link
          </button>
        )}
      </div>

      {shareUrl && (
        <div style={{ marginTop: '18px' }}>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'stretch', flexWrap: 'wrap' }}>
            <input
              readOnly
              className="input"
              value={shareUrl}
              onFocus={(e) => e.target.select()}
              aria-label="Public share link"
              style={{ flex: 1, minWidth: '220px', fontSize: '0.72rem', color: 'var(--text-muted)' }}
            />
            <button type="button" onClick={copy} className="btn btn-primary">
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>
          <p className="mono" style={{ marginTop: '10px' }}>
            ANYONE WITH THIS LINK CAN READ THE ADVICE. YOUR PHOTO IS NOT INCLUDED.
          </p>
        </div>
      )}
    </Frame>
  );
}
