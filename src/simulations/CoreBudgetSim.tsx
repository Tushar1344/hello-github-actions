import { useState } from "react";
import { SimButton, SimSlider } from "../components/sim/controls";

const GRID = 8;
const TOTAL = GRID * GRID; // transistor "budget" units

const PRESETS: Record<string, number> = {
  CPU: 0.72, // mostly control + cache, a few powerful cores
  GPU: 0.18, // little control, many small ALUs
  TPU: 0.05, // nearly all ALUs, one big systolic array
};

export function CoreBudgetSim() {
  const [controlFrac, setControlFrac] = useState(PRESETS.GPU);
  const [preset, setPreset] = useState("GPU");

  const controlUnits = Math.round(controlFrac * TOTAL);
  const aluUnits = TOTAL - controlUnits;

  const setP = (name: string) => {
    setPreset(name);
    setControlFrac(PRESETS[name]);
  };

  // proxies (unitless, for intuition only)
  const throughput = aluUnits; // parallel arithmetic
  const serial = Math.round(Math.sqrt(controlUnits) * 12); // single-thread latency hiding

  const CELL = 30;
  return (
    <div className="figure-card">
      <div className="sim-controls">
        {Object.keys(PRESETS).map((p) => (
          <SimButton key={p} active={preset === p} onClick={() => setP(p)}>
            {p}
          </SimButton>
        ))}
        <div className="sim-spacer" />
        <SimSlider
          label="control"
          min={0}
          max={100}
          value={Math.round(controlFrac * 100)}
          onChange={(v) => {
            setControlFrac(v / 100);
            setPreset("custom");
          }}
          format={(v) => `${v}%`}
        />
      </div>

      <div className="sim-row">
        <svg width={GRID * CELL} height={GRID * CELL} style={{ display: "block" }}>
          {Array.from({ length: TOTAL }).map((_, idx) => {
            const r = Math.floor(idx / GRID);
            const c = idx % GRID;
            const isControl = idx < controlUnits;
            return (
              <g key={idx}>
                <rect
                  x={c * CELL + 1}
                  y={r * CELL + 1}
                  width={CELL - 2}
                  height={CELL - 2}
                  rx={isControl ? 3 : 5}
                  fill={isControl ? "var(--plum)" : "var(--teal-bg)"}
                  stroke={isControl ? "var(--plum)" : "var(--teal-deep)"}
                  strokeWidth={1}
                />
                {!isControl && (
                  <circle cx={c * CELL + CELL / 2} cy={r * CELL + CELL / 2} r={3} fill="var(--teal-deep)" />
                )}
              </g>
            );
          })}
        </svg>

        <div className="sim-col">
          <div style={{ display: "flex", gap: 24 }}>
            <div>
              <div className="sim-stat-label">ALUs (throughput)</div>
              <div className="sim-stat-big">{throughput}</div>
            </div>
            <div>
              <div className="sim-stat-label">Serial speed</div>
              <div className="sim-stat-big" style={{ color: "var(--plum)" }}>
                {serial}
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 14, marginTop: 12, fontFamily: "var(--mono)", fontSize: 11 }}>
            <span>
              <span style={{ color: "var(--plum)" }}>■</span> control / cache
            </span>
            <span>
              <span style={{ color: "var(--teal-deep)" }}>■</span> arithmetic
            </span>
          </div>
          <p className="sim-note">
            <span className="lead">Same silicon, opposite bets. </span>
            A <strong>CPU</strong> spends most of its transistors on control — branch prediction,
            out-of-order logic, big caches — to make one thread fast. A <strong>GPU</strong> strips
            that away and fills the die with small ALUs for throughput. A <strong>TPU</strong> goes
            furthest: almost the whole die is one systolic array. In this light a GPU is just a bunch
            of tiny TPUs wrapped in a little more general-purpose plumbing.
          </p>
        </div>
      </div>
    </div>
  );
}
