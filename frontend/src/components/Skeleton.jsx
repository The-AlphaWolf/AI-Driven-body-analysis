/**
 * Loading placeholders.
 *
 * These hold the page's shape while data loads, so content does not appear
 * to jump when it arrives. A bare spinner cannot do that.
 */

export function SkeletonCard({ lines = 3, height = null }) {
  return (
    <div className="frame" style={{ padding: '20px' }} aria-hidden="true">
      {height ? (
        <div className="skeleton" style={{ height }} />
      ) : (
        <>
          <div className="skeleton skeleton-line" style={{ width: '38%', height: '8px' }} />
          {Array.from({ length: lines }).map((_, i) => (
            <div
              key={i}
              className="skeleton skeleton-line"
              style={{ width: i === lines - 1 ? '60%' : '100%' }}
            />
          ))}
        </>
      )}
    </div>
  );
}

export function SkeletonGrid({ count = 6, lines = 3, minWidth = '290px' }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(auto-fill, minmax(${minWidth}, 1fr))`,
        gap: '16px',
      }}
      role="status"
      aria-label="Loading"
    >
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} lines={lines} />
      ))}
    </div>
  );
}

export function SkeletonResults() {
  return (
    <div
      className="container"
      style={{ padding: '48px 28px', maxWidth: '1040px' }}
      role="status"
      aria-label="Loading results"
    >
      <div style={{ maxWidth: '300px', marginBottom: '36px' }}>
        <div className="skeleton skeleton-line" style={{ height: '26px', marginBottom: '12px' }} />
        <div className="skeleton skeleton-line" style={{ width: '55%' }} />
      </div>

      <div style={{ marginBottom: '40px' }}>
        <SkeletonCard height="260px" />
      </div>

      <SkeletonGrid count={6} lines={4} minWidth="280px" />
    </div>
  );
}
