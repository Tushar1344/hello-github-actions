import { useState } from "react";
import { SimSlider } from "../components/sim/controls";

// Toy hardware numbers (unitless) to build intuition, not real specs.
const PEAK = 100; // peak compute
const BW = 8; // memory bandwidth
const RIDGE = PEAK / BW; // arithmetic intensity at the corner

export function RooflineSim() {
  const [intensity, setIntensity] = useState(3); // FLOPs per byte moved

  const attainable = Math.min(PEAK, BW * intensity);
  const memoryBound = intensity < RIDGE;

  // plot geometry
  const W = 360,
    H = 240,
    PAD = 36;
  const X_MAX = 30;
  const Y_MAX = PEAK * 1.15;
  const px = (i: number) => PAD + (i / X_MAX) * (W - PAD - 10);
  const py = (p: number) => H - PAD - (p / Y_MAX) * (H - PAD - 14);

  return (
    <div className="figure-card">
      <div className="sim-controls">
        <SimSlider
          label="arithmetic intensity (FLOP/byte)"
          min={1}
          max={30}
          step={0.5}
          value={intensity}
          onChange={setIntensity}
          format={(v) => v.toFixed(1)}
        />
      </div>

      <div className="sim-row">
        <svg width={W} height={H} style={{ display: "block" }}>
          {/* axes */}
          <line x1={PAD} y1={H - PAD} x2={W - 6} y2={H - PAD} stroke="var(--line-strong)" strokeWidth={1} />
          <line x1={PAD} y1={H - PAD} x2={PAD} y2={10} stroke="var(--line-strong)" strokeWidth={1} />
          {/* memory-bound slope */}
          <line x1={px(0)} y1={py(0)} x2={px(RIDGE)} y2={py(PEAK)} stroke="var(--plum)" strokeWidth={2} />
          {/* compute ceiling */}
          <line x1={px(RIDGE)} y1={py(PEAK)} x2={px(X_MAX)} y2={py(PEAK)} stroke="var(--teal-deep)" strokeWidth={2} />
          {/* ridge marker */}
          <line x1={px(RIDGE)} y1={H - PAD} x2={px(RIDGE)} y2={py(PEAK)} stroke="var(--line)" strokeDasharray="3 3" />
          <text x={px(RIDGE)} y={H - PAD + 14} textAnchor="middle" fontFamily="var(--mono)" fontSize={9} fill="var(--muted)">
            ridge
          </text>
          {/* current point */}
          <line x1={px(intensity)} y1={H - PAD} x2={px(intensity)} y2={py(attainable)} stroke="var(--line)" strokeDasharray="2 3" />
          <circle cx={px(intensity)} cy={py(attainable)} r={5} fill={memoryBound ? "var(--plum)" : "var(--teal-deep)"} stroke="var(--panel)" strokeWidth={2} />
          {/* labels */}
          <text x={W - 6} y={H - PAD + 14} textAnchor="end" fontFamily="var(--mono)" fontSize={9} fill="var(--muted)">
            FLOP / byte →
          </text>
          <text x={PAD - 6} y={py(PEAK)} textAnchor="end" fontFamily="var(--mono)" fontSize={9} fill="var(--teal-deep)">
            peak
          </text>
        </svg>

        <div className="sim-col">
          <div className="sim-stat-label">Attainable performance</div>
          <div className="sim-stat-big" style={{ color: memoryBound ? "var(--plum)" : "var(--teal-deep)" }}>
            {attainable.toFixed(0)}
            <span className="unit"> / {PEAK}</span>
          </div>
          <div
            style={{
              display: "inline-block",
              marginTop: 8,
              fontFamily: "var(--mono)",
              fontSize: 10,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: memoryBound ? "var(--plum)" : "var(--teal-deep)",
            }}
          >
            {memoryBound ? "memory-bound" : "compute-bound"}
          </div>
          <p className="sim-note">
            <span className="lead">This is the whole game in one chart. </span>
            Arithmetic intensity is how many operations you do per byte you move. To the left of the
            ridge you are <strong>starved by data movement</strong> — your expensive ALUs sit idle
            waiting for memory. A lone MAC fetching its own operands lives way out here. A systolic
            array reuses each byte across a whole row, pushing intensity right, past the ridge, where
            you finally run at peak. Every architecture in this book is a scheme to move right.
          </p>
        </div>
      </div>
    </div>
  );
}
