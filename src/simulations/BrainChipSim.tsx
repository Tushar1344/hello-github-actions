import { useState } from "react";
import { SimButton } from "../components/sim/controls";

interface Metric {
  key: string;
  label: string;
  brain: { v: string; frac: number };
  chip: { v: string; frac: number };
  note: string;
}

// Order-of-magnitude figures for intuition, not precise benchmarks.
const METRICS: Metric[] = [
  {
    key: "power",
    label: "Power",
    brain: { v: "~20 W", frac: 0.03 },
    chip: { v: "~700 W", frac: 1 },
    note: "The brain runs the whole mind on the power of a dim light bulb; a single AI GPU draws ~35× more.",
  },
  {
    key: "parallel",
    label: "Parallelism",
    brain: { v: "~10¹¹ neurons", frac: 1 },
    chip: { v: "~10⁴ ALUs", frac: 0.12 },
    note: "Brains are massively parallel and slow; chips are far less parallel but each unit is millions of times faster.",
  },
  {
    key: "clock",
    label: "Clock speed",
    brain: { v: "~100 Hz", frac: 0.02 },
    chip: { v: "~10⁹ Hz", frac: 1 },
    note: "A neuron fires a few hundred times a second; a chip switches a billion times a second. Speed is the chip's edge.",
  },
  {
    key: "energy",
    label: "Energy per op",
    brain: { v: "~10 fJ", frac: 0.05 },
    chip: { v: "~200 fJ+", frac: 1 },
    note: "The brain co-locates memory and compute at the synapse, so it barely moves data — the ultimate answer to the data-movement wall.",
  },
];

export function BrainChipSim() {
  const [mi, setMi] = useState(3); // default: energy/op
  const m = METRICS[mi];

  const Bar = ({ label, color, v, frac }: { label: string; color: string; v: string; frac: number }) => (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--muted)" }}>{label}</span>
        <span style={{ fontFamily: "var(--serif)", fontSize: 18, color }}>{v}</span>
      </div>
      <div style={{ height: 12, background: "var(--panel-2)", borderRadius: 6, overflow: "hidden" }}>
        <div style={{ width: `${frac * 100}%`, height: "100%", background: color, transition: "width 0.3s" }} />
      </div>
    </div>
  );

  return (
    <div className="figure-card">
      <div className="sim-controls">
        {METRICS.map((mm, i) => (
          <SimButton key={mm.key} active={i === mi} onClick={() => setMi(i)}>
            {mm.label}
          </SimButton>
        ))}
      </div>

      <Bar label="Brain" color="var(--teal-deep)" v={m.brain.v} frac={m.brain.frac} />
      <Bar label="AI chip" color="var(--plum)" v={m.chip.v} frac={m.chip.frac} />

      <p className="sim-note">
        <span className="lead">{m.label}. </span>
        {m.note}
      </p>
    </div>
  );
}
