import { useEffect, useState } from 'react';
import api from '../services/api';

/**
 * Analysis thumbnail.
 *
 * The thumbnail endpoint is JWT-protected via the Authorization header, so
 * the image is fetched as a blob and shown through an object URL rather
 * than pointed at directly with <img src>.
 */
export default function Thumbnail({ analysisId, size = 62, alt = 'Analysis thumbnail' }) {
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
    flexShrink: 0,
    border: '1px solid var(--line-mid)',
  };

  if (!url) {
    return (
      <div
        style={{ ...shared, background: 'rgba(0,0,0,0.35)', display: 'grid', placeItems: 'center' }}
        aria-hidden="true"
      >
        <svg width={size * 0.5} height={size * 0.5} viewBox="0 0 32 32">
          <ellipse
            cx="16" cy="16" rx="7" ry="9"
            fill="none" stroke="var(--line-mid)" strokeWidth="1.5"
          />
          <g fill="var(--line-mid)">
            <circle cx="13" cy="14" r="1.2" />
            <circle cx="19" cy="14" r="1.2" />
            <circle cx="16" cy="19.5" r="1.2" />
          </g>
        </svg>
      </div>
    );
  }

  return <img src={url} alt={alt} style={{ ...shared, objectFit: 'cover' }} />;
}
