/**
 * The interface's vocabulary of parts.
 *
 * Every screen is assembled from these, so a change to the instrument look
 * happens in one file rather than across nine pages.
 */

/** A bracketed hairline box, optionally captioned along its top rule. */
export function Frame({ label, slug, children, hover = false, className = '', style, ...rest }) {
  return (
    <div
      className={`frame${hover ? ' frame-hover' : ''}${className ? ` ${className}` : ''}`}
      style={{ padding: '22px 20px', ...style }}
      {...rest}
    >
      {(label || slug) && (
        <div style={{
          display: 'flex',
          alignItems: 'baseline',
          justifyContent: 'space-between',
          gap: '12px',
          marginBottom: '16px',
        }}>
          {label && <span className="label">{label}</span>}
          {slug && <span className="label" style={{ letterSpacing: '0.14em' }}>{slug}</span>}
        </div>
      )}
      {children}
    </div>
  );
}

/** A captioned value with a confidence meter beneath it — the image's core row. */
export function Readout({ label, value, confidence = null, children }) {
  return (
    <div style={{ marginBottom: '4px' }}>
      <span className="label" style={{ marginBottom: '6px' }}>{label}</span>
      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        justifyContent: 'space-between',
        gap: '16px',
        marginBottom: confidence === null ? 0 : '10px',
      }}>
        <span className="readout">{value}</span>
        {confidence !== null && (
          <span className="meter-value">{Math.round(confidence * 100)}%</span>
        )}
      </div>
      {confidence !== null && <Meter value={confidence} />}
      {children}
    </div>
  );
}

/** The hairline confidence track. */
export function Meter({ value, label = null }) {
  const pct = Math.max(0, Math.min(1, value || 0)) * 100;
  return (
    <>
      {label && (
        <div className="meter-row">
          <span className="label">{label}</span>
          <span className="meter-value">{Math.round(pct)}%</span>
        </div>
      )}
      <div
        className="meter"
        role="meter"
        aria-valuenow={Math.round(pct)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Confidence'}
      >
        <span className="meter-fill" style={{ width: `${pct}%` }} />
      </div>
    </>
  );
}

/**
 * A colour palette as swatches.
 *
 * The engine names palettes ("jewel tones"), which is not something you can
 * hold against a shirt — so the colour rules carry hex values and they get
 * shown, with the code, rather than described.
 */
export function Swatches({ palette }) {
  if (!palette?.length) return null;

  return (
    <div className="swatch-grid">
      {palette.map((swatch) => (
        <div key={swatch.hex} className="swatch" title={`${swatch.name} — ${swatch.hex}`}>
          <div className="swatch-chip" style={{ background: swatch.hex }} />
          <span className="swatch-hex">{swatch.name}</span>
          <span className="swatch-hex" style={{ marginTop: '1px', opacity: 0.6 }}>
            {swatch.hex}
          </span>
        </div>
      ))}
    </div>
  );
}

/** Title on the left, monospace slug on the right, hairline between. */
export function SectionHead({ title, sub = null, slug = null, children = null }) {
  return (
    <div className="section-head">
      <div>
        <h2 style={{ textTransform: 'uppercase' }}>{title}</h2>
        {sub && (
          <p className="mono" style={{ marginTop: '6px' }}>{sub}</p>
        )}
      </div>
      {children || (slug && <span className="label label-accent">{slug}</span>)}
    </div>
  );
}
