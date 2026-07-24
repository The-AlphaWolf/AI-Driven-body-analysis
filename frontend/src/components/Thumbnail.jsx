import { useEffect, useState } from 'react';
import api from '../services/api';

/**
 * Analysis thumbnail.
 *
 * The thumbnail endpoint is JWT-protected via the Authorization header, so
 * the image is fetched as a blob and shown through an object URL rather
 * than pointed at directly with <img src>.
 */
export default function Thumbnail({ analysisId, size = 64, alt = 'Analysis thumbnail' }) {
  const [url, setUrl] = useState(null);

  useEffect(() => {
    let objectUrl = null;
    let cancelled = false;

    api.getThumbnailObjectUrl(analysisId).then((result) => {
      if (cancelled) {
        if (result) URL.revokeObjectURL(result);
        return;
      }
      objectUrl = result;
      setUrl(result);
    }).catch(() => {
      // A missing thumbnail is not worth surfacing — the placeholder stands in.
    });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [analysisId]);

  const shared = {
    width: size,
    height: size,
    borderRadius: '12px',
    flexShrink: 0,
    border: '1px solid var(--color-border)',
  };

  if (!url) {
    return (
      <div
        style={{
          ...shared,
          background: 'var(--color-surface)',
          display: 'grid',
          placeItems: 'center',
          fontSize: `${size * 0.4}px`,
        }}
        aria-hidden="true"
      >
        👤
      </div>
    );
  }

  return <img src={url} alt={alt} style={{ ...shared, objectFit: 'cover' }} />;
}
