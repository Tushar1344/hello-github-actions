import { useState } from "react";
import { SimButton } from "../components/sim/controls";

const GRID = 8;

export function FabricSim() {
  const [mode, setMode] = useState<"fpga" | "asic">("fpga");
  const [config, setConfig] = useState(0); // which "program" the FPGA holds

  // FPGA: a fraction of cells are routing/overhead (wasted vs a dedicated design).
  // The active-logic pattern changes when you reprogram.
  const isActive = (idx: number) => {
    if (mode === "asic") return true; // dense, every cell does useful work
    // pseudo-random but deterministic per config: ~55% active logic, rest routing
    const h = (idx * 2654435761 + config * 40503) % 100;
    return h < 55;
  };

  const usefulPct = mode === "asic" ? 100 : 55;
  const CELL = 30;

  return (
    <div className="figure-card">
      <div className="sim-controls">
        <SimButton active={mode === "fpga"} onClick={() => setMode("fpga")}>
          FPGA
        </SimButton>
        <SimButton active={mode === "asic"} onClick={() => setMode("asic")}>
          ASIC
        </SimButton>
        <div className="sim-spacer" />
        <SimButton
          accent
          disabled={mode === "asic"}
          onClick={() => setConfig((c) => c + 1)}
        >
          {mode === "asic" ? "Locked in silicon" : "Reprogram"}
        </SimButton>
      </div>

      <div className="sim-row">
        <svg width={GRID * CELL} height={GRID * CELL} style={{ display: "block" }}>
          {Array.from({ length: GRID * GRID }).map((_, idx) => {
            const r = Math.floor(idx / GRID);
            const c = idx % GRID;
            const active = isActive(idx);
            return (
              <rect
                key={idx}
                x={c * CELL + 1}
                y={r * CELL + 1}
                width={CELL - 2}
                height={CELL - 2}
                rx={4}
                fill={active ? "var(--teal-bg)" : "var(--panel-2)"}
                stroke={active ? "var(--teal-deep)" : "var(--line)"}
                strokeWidth={1}
              />
            );
          })}
        </svg>

        <div className="sim-col">
          <div className="sim-stat-label">Useful silicon</div>
          <div className="sim-stat-big">
            {usefulPct}
            <span className="unit"> %</span>
          </div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--muted)", marginTop: 10 }}>
            {mode === "fpga" ? "reconfigurable · higher unit cost" : "fixed function · cheap at volume"}
          </div>
          <p className="sim-note">
            <span className="lead">
              {mode === "fpga" ? "Flexibility you pay for." : "Efficiency you commit to."}
            </span>{" "}
            An <strong>FPGA</strong> is a sea of logic blocks and programmable wiring you reconfigure
            after manufacture — press <em>Reprogram</em> and the circuit changes. But much of the die
            is routing overhead, so it is slower and less efficient. An <strong>ASIC</strong> bakes
            one design permanently into silicon: no overhead, maximum speed and efficiency, but it
            can never change. A TPU is an ASIC betting the workload will always be matrix multiply —
            a bet worth making once you have seen the previous chapters.
          </p>
        </div>
      </div>
    </div>
  );
}
