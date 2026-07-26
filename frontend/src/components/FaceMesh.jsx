import { useMemo } from 'react';

/**
 * The biometric mesh diagram.
 *
 * A stylised standin for the 478-point face mesh the backend actually fits —
 * concentric rings of landmark dots over a face outline, with the vertical
 * thirds the shape classifier measures drawn in. Generated from a seed so
 * the scatter is stable across renders rather than jittering on every paint.
 *
 * Purely decorative: it is not derived from the user's photo, which never
 * leaves the analysis request.
 */

// The box is wider than the face so the right-hand annotation has room to sit
// beside it; overflowing the viewBox lets a neighbouring grid column clip it.
const W = 360;
const H = 384;
const CX = 140;
const CY = 190;

/** Deterministic [0,1) noise — same diagram every render, no layout jitter. */
function noise(i) {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

function buildRings() {
  const rings = [];
  // Six nested face outlines, each sampled into dots.
  for (let r = 0; r < 6; r++) {
    const scale = 0.34 + r * 0.132;
    const rx = 108 * scale;
    const ry = 148 * scale;
    const count = 12 + r * 7;
    const dots = [];

    for (let i = 0; i < count; i++) {
      const t = (i / count) * Math.PI * 2 - Math.PI / 2;
      const wobble = 0.94 + noise(r * 97 + i) * 0.12;
      // Faces taper: pull the lower half of each ring inwards toward the chin.
      const taper = Math.sin(t) > 0 ? 1 - Math.sin(t) * 0.16 : 1;

      dots.push({
        x: CX + Math.cos(t) * rx * wobble * taper,
        y: CY + Math.sin(t) * ry * wobble,
        r: 1.05 + noise(i * 13 + r) * 0.9,
        delay: (noise(r * 31 + i * 7) * 3.6).toFixed(2),
      });
    }
    rings.push({ dots, rx, ry, taper: true });
  }
  return rings;
}

/** The regions the classifier measures, labelled as in a calibration chart. */
const ZONES = [
  { label: 'FOREHEAD', cx: CX, cy: CY - 92, rx: 46, ry: 20 },
  { label: 'CHEEK', cx: CX - 44, cy: CY - 20, rx: 30, ry: 16 },
  { label: 'CHEEK', cx: CX + 44, cy: CY - 20, rx: 30, ry: 16 },
  { label: 'JAW', cx: CX, cy: CY + 74, rx: 40, ry: 18 },
];

export default function FaceMesh({ caption = 'biometric mesh', thirds = '1 : 1 : 1.06' }) {
  const rings = useMemo(buildRings, []);

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      style={{ maxWidth: '380px', display: 'block' }}
      role="img"
      aria-label="Stylised face landmark mesh with the facial thirds marked"
    >
      <defs>
        <linearGradient id="mesh-scan-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ff2d6e" stopOpacity="0" />
          <stop offset="50%" stopColor="#ff2d6e" stopOpacity="0.16" />
          <stop offset="100%" stopColor="#ff2d6e" stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Vertical thirds — the ratio the shape classifier reads. */}
      <g stroke="rgba(255,120,160,0.16)" strokeWidth="1" strokeDasharray="3 5">
        <line x1={CX - 132} y1={CY - 74} x2={CX + 132} y2={CY - 74} />
        <line x1={CX - 132} y1={CY + 22} x2={CX + 132} y2={CY + 22} />
      </g>

      {/* Left measuring rail. */}
      <g stroke="rgba(255,120,160,0.28)" strokeWidth="1">
        <line x1={CX - 132} y1={CY - 156} x2={CX - 132} y2={CY + 156} />
        {[-156, -74, 22, 156].map((y) => (
          <line key={y} x1={CX - 137} y1={CY + y} x2={CX - 127} y2={CY + y} />
        ))}
      </g>

      {/* Landmark rings. */}
      {rings.map((ring, r) => (
        <g key={r}>
          <ellipse
            cx={CX}
            cy={CY}
            rx={ring.rx}
            ry={ring.ry}
            fill="none"
            stroke="rgba(255,45,110,0.1)"
            strokeWidth="1"
          />
          {ring.dots.map((d, i) => (
            <circle
              key={i}
              className="mesh-dot"
              cx={d.x}
              cy={d.y}
              r={d.r}
              fill="#ff2d6e"
              style={{ animationDelay: `${d.delay}s` }}
            />
          ))}
        </g>
      ))}

      {/* Measured zones. */}
      {ZONES.map((zone, i) => (
        <g key={i}>
          <ellipse
            cx={zone.cx}
            cy={zone.cy}
            rx={zone.rx}
            ry={zone.ry}
            fill="rgba(255,45,110,0.07)"
            stroke="rgba(255,123,166,0.45)"
            strokeWidth="1"
          />
          <text
            x={zone.cx}
            y={zone.cy + 3}
            textAnchor="middle"
            fill="#ff7ba6"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: '7px',
              letterSpacing: '0.18em',
            }}
          >
            {zone.label}
          </text>
        </g>
      ))}

      {/* Sweep — a soft band with a bright leading edge, kept faint enough
          that it reads as a pass over the mesh rather than a highlight on it. */}
      <g className="mesh-scan">
        <rect
          x={CX - 132}
          y={CY - 22}
          width="264"
          height="44"
          fill="url(#mesh-scan-grad)"
        />
        <line
          x1={CX - 132}
          y1={CY}
          x2={CX + 132}
          y2={CY}
          stroke="#ff7ba6"
          strokeWidth="1"
          opacity="0.32"
        />
      </g>

      {/* Captions, set like chart annotations. */}
      <text
        x={CX + 122}
        y={CY - 88}
        fill="#7d5966"
        style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '8px', letterSpacing: '0.14em' }}
      >
        {caption}
      </text>
      <line
        x1={CX + 96}
        y1={CY - 92}
        x2={CX + 118}
        y2={CY - 92}
        stroke="rgba(255,120,160,0.3)"
        strokeWidth="1"
      />
      <text
        x={CX - 132}
        y={CY + 182}
        fill="#7d5966"
        style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '8px', letterSpacing: '0.14em' }}
      >
        vertical thirds {thirds}
      </text>
    </svg>
  );
}
