/**
 * Loading placeholders.
 *
 * These hold the page's shape while data loads, so content does not appear
 * to jump when it arrives. A bare spinner cannot do that.
 */

export function SkeletonCard({ lines = 3, height = null }) {
  return (
    <div className="glass-card" style={{ padding: '20px' }} aria-hidden="true">
      {height ? (
        <div className="skeleton" style={{ height }} />
      ) : (
        <>
          <div className="skeleton skeleton-line" style={{ width: '40%', height: '10px' }} />
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

export function SkeletonGrid({ count = 6, lines = 3, minWidth = '280px' }) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(auto-fill, minmax(${minWidth}, 1fr))`,
        gap: '20px',
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
    <div className="container" style={{ padding: '48px 24px', maxWidth: '1000px' }} role="status" aria-label="Loading results">
      <div style={{ maxWidth: '380px', margin: '0 auto 40px' }}>
        <div className="skeleton skeleton-line" style={{ height: '28px', marginBottom: '12px' }} />
        <div className="skeleton skeleton-line" style={{ width: '55%', margin: '0 auto' }} />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '20px',
        marginBottom: '48px',
      }}>
        {Array.from({ length: 3 }).map((_, i) => (
          <SkeletonCard key={i} height="120px" />
        ))}
      </div>

      <SkeletonGrid count={6} lines={4} minWidth="260px" />
    </div>
  );
}
