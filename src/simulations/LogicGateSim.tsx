import { useState } from "react";
import { SimButton } from "../components/sim/controls";

type Bit = 0 | 1;
const nand = (a: Bit, b: Bit): Bit => (a && b ? 0 : 1);

const GATES: { name: string; fn: (a: Bit, b: Bit) => Bit; expr: string }[] = [
  { name: "AND", fn: (a, b) => (a && b ? 1 : 0), expr: "A · B" },
  { name: "OR", fn: (a, b) => (a || b ? 1 : 0), expr: "A + B" },
  { name: "XOR", fn: (a, b) => ((a ^ b) as Bit), expr: "A ⊕ B" },
  { name: "NAND", fn: nand, expr: "¬(A · B)" },
  { name: "NOR", fn: (a, b) => (a || b ? 0 : 1), expr: "¬(A + B)" },
  { name: "XNOR", fn: (a, b) => ((a ^ b ? 0 : 1) as Bit), expr: "¬(A ⊕ B)" },
];

/** Bit pill: filled teal when high. */
function BitPill({ v, label }: { v: Bit; label?: string }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      {label && (
        <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--muted)" }}>
          {label}
        </span>
      )}
      <span
        style={{
          fontFamily: "var(--mono)",
          fontSize: 13,
          fontWeight: 600,
          width: 22,
          height: 22,
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: 4,
          color: v ? "var(--panel)" : "var(--muted)",
          background: v ? "var(--teal-deep)" : "var(--panel-2)",
          border: `1px solid ${v ? "var(--teal-deep)" : "var(--line)"}`,
        }}
      >
        {v}
      </span>
    </span>
  );
}

const wireColor = (v: Bit) => (v ? "var(--teal-deep)" : "var(--line-strong)");

/** A NAND gate body + bubble at (x,y), output lit by `out`. */
function NandGate({ x, y, out, label }: { x: number; y: number; out: Bit; label: string }) {
  return (
    <g>
      <path
        d={`M${x},${y} h26 a22,22 0 0 1 0,44 h-26 z`}
        fill="var(--panel)"
        stroke={wireColor(out)}
        strokeWidth={1.5}
      />
      <circle cx={x + 52} cy={y + 22} r={4} fill="var(--panel)" stroke={wireColor(out)} strokeWidth={1.5} />
      <text
        x={x + 18}
        y={y + 26}
        fontFamily="var(--mono)"
        fontSize={9}
        fill="var(--muted)"
        textAnchor="middle"
      >
        {label}
      </text>
    </g>
  );
}

export function LogicGateSim() {
  const [a, setA] = useState<Bit>(1);
  const [b, setB] = useState<Bit>(0);
  const [view, setView] = useState<"gates" | "xor">("gates");

  // XOR-from-NAND construction.
  const g1 = nand(a, b);
  const g2 = nand(a, g1);
  const g3 = nand(b, g1);
  const xor = nand(g2, g3);

  return (
    <div className="figure-card">
      <div className="sim-controls">
        <SimButton active={view === "gates"} onClick={() => setView("gates")}>
          Gates
        </SimButton>
        <SimButton active={view === "xor"} onClick={() => setView("xor")}>
          XOR from NAND
        </SimButton>
        <div className="sim-spacer" />
        <span className="sim-field">
          <SimButton accent onClick={() => setA((v) => (v ? 0 : 1))}>
            A = {a}
          </SimButton>
          <SimButton accent onClick={() => setB((v) => (v ? 0 : 1))}>
            B = {b}
          </SimButton>
        </span>
      </div>

      {view === "gates" ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
            gap: 12,
          }}
        >
          {GATES.map((g) => {
            const out = g.fn(a, b);
            return (
              <div
                key={g.name}
                style={{
                  border: `1px solid ${out ? "var(--teal-soft)" : "var(--line)"}`,
                  borderRadius: 8,
                  padding: "14px 16px",
                  background: out ? "var(--teal-bg)" : "var(--panel)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span style={{ fontFamily: "var(--mono)", fontSize: 13, fontWeight: 600, color: "var(--ink)" }}>
                    {g.name}
                  </span>
                  <BitPill v={out} />
                </div>
                <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--muted)", marginTop: 8 }}>
                  {g.expr}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="sim-row">
          <svg width={360} height={170} viewBox="0 0 360 170" style={{ display: "block", maxWidth: "100%" }}>
            {/* input rails */}
            <text x={6} y={48} fontFamily="var(--mono)" fontSize={12} fill="var(--ink)">
              A
            </text>
            <text x={6} y={128} fontFamily="var(--mono)" fontSize={12} fill="var(--ink)">
              B
            </text>
            {/* wires: A and B to g1, then fan-out */}
            <polyline points="16,44 70,44 70,30" fill="none" stroke={wireColor(a)} strokeWidth={1.5} />
            <polyline points="16,124 70,124 70,62" fill="none" stroke={wireColor(b)} strokeWidth={1.5} />
            <NandGate x={70} y={24} out={g1} label="N1" />
            {/* g1 fans to N2 (with A) and N3 (with B) */}
            <polyline points="126,46 150,46 150,96" fill="none" stroke={wireColor(g1)} strokeWidth={1.5} />
            <polyline points="16,44 40,44 40,86 178,86" fill="none" stroke={wireColor(a)} strokeWidth={1.2} strokeOpacity={0.7} />
            <polyline points="16,124 40,124 40,150 178,150" fill="none" stroke={wireColor(b)} strokeWidth={1.2} strokeOpacity={0.7} />
            <NandGate x={178} y={78} out={g2} label="N2" />
            <NandGate x={178} y={132} out={g3} label="N3" />
            <polyline points="150,96 178,96" fill="none" stroke={wireColor(g1)} strokeWidth={1.5} />
            <polyline points="150,96 150,146 178,146" fill="none" stroke={wireColor(g1)} strokeWidth={1.5} />
            {/* N2,N3 → N4 */}
            <polyline points="234,100 260,100 260,60" fill="none" stroke={wireColor(g2)} strokeWidth={1.5} />
            <polyline points="234,154 268,154 268,82 286,82" fill="none" stroke={wireColor(g3)} strokeWidth={1.5} />
            <polyline points="260,60 286,60" fill="none" stroke={wireColor(g2)} strokeWidth={1.5} />
            <NandGate x={286} y={52} out={xor} label="N4" />
            <polyline points="342,74 356,74" fill="none" stroke={wireColor(xor)} strokeWidth={2} />
          </svg>

          <div className="sim-col">
            <div className="sim-stat-label">Output (= A ⊕ B)</div>
            <div className="sim-stat-big">{xor}</div>
            <p className="sim-note">
              <span className="lead">Four NANDs make an XOR. </span>
              NAND alone is <em>functionally complete</em> — every other gate, and therefore every
              circuit in this book, can be built from copies of this one part. Toggle A and B and
              watch the high (teal) signal propagate.
            </p>
            <div style={{ display: "flex", gap: 14, marginTop: 14 }}>
              <BitPill v={a} label="A" />
              <BitPill v={b} label="B" />
              <BitPill v={xor} label="OUT" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
