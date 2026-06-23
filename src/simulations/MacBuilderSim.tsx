import { useEffect, useState } from "react";
import { SimButton } from "../components/sim/controls";

const bits = (n: number, w: number) =>
  Array.from({ length: w }, (_, i) => (n >> (w - 1 - i)) & 1);

/** Toggleable little-endian-rendered bit register (MSB left). */
function BitRegister({
  value,
  width,
  onToggle,
  label,
  color = "var(--ink)",
}: {
  value: number;
  width: number;
  onToggle?: (bit: number) => void;
  label: string;
  color?: string;
}) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--muted)", width: 54 }}>
        {label}
      </span>
      <div style={{ display: "flex", gap: 4 }}>
        {bits(value, width).map((bit, i) => {
          const pos = width - 1 - i;
          return (
            <button
              key={i}
              onClick={onToggle ? () => onToggle(pos) : undefined}
              disabled={!onToggle}
              style={{
                width: 28,
                height: 30,
                fontFamily: "var(--mono)",
                fontSize: 14,
                fontWeight: 600,
                borderRadius: 4,
                cursor: onToggle ? "pointer" : "default",
                color: bit ? "var(--panel)" : "var(--muted-2)",
                background: bit ? color : "var(--panel-2)",
                border: `1px solid ${bit ? color : "var(--line)"}`,
              }}
            >
              {bit}
            </button>
          );
        })}
      </div>
      <span
        style={{
          fontFamily: "var(--serif)",
          fontSize: 22,
          color: "var(--ink)",
          minWidth: 40,
          textAlign: "right",
        }}
      >
        {value}
      </span>
    </div>
  );
}

// A fixed length-4 dot product to demonstrate accumulation.
const VEC_A = [3, 1, 2, 2];
const VEC_B = [2, 4, 1, 3];

export function MacBuilderSim() {
  const [a, setA] = useState(6); // 0110
  const [b, setB] = useState(5); // 0101
  const product = a * b;

  // accumulator demo
  const [step, setStep] = useState(0); // products folded in so far (0..4)
  const [playing, setPlaying] = useState(false);
  const acc = VEC_A.slice(0, step).reduce((s, av, i) => s + av * VEC_B[i], 0);

  useEffect(() => {
    if (!playing) return;
    if (step >= VEC_A.length) {
      setPlaying(false);
      return;
    }
    const id = setTimeout(() => setStep((s) => s + 1), 700);
    return () => clearTimeout(id);
  }, [playing, step]);

  const toggle = (set: (f: (v: number) => number) => void, pos: number) =>
    set((v) => v ^ (1 << pos));

  return (
    <div className="figure-card">
      <h4 style={{ margin: "0 0 14px" }}>1 · Multiply two numbers</h4>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <BitRegister label="a (4-bit)" value={a} width={4} color="var(--teal-deep)" onToggle={(p) => toggle(setA, p)} />
        <BitRegister label="b (4-bit)" value={b} width={4} color="var(--plum)" onToggle={(p) => toggle(setB, p)} />
      </div>

      <div style={{ marginTop: 18, paddingTop: 16, borderTop: "1px solid var(--line)" }}>
        <div className="sim-stat-label">Partial products (shift &amp; add)</div>
        <div style={{ fontFamily: "var(--mono)", fontSize: 13, lineHeight: 1.9, color: "var(--ink-soft)" }}>
          {bits(b, 4).map((bit, i) => {
            const pos = 3 - i;
            const pp = bit ? a << pos : 0;
            return (
              <div key={i} style={{ opacity: bit ? 1 : 0.4 }}>
                b<sub>{pos}</sub>={bit} → {bit ? `a · 2^${pos}` : "0"} = {pp}
              </div>
            );
          })}
          <div style={{ borderTop: "1px solid var(--line)", marginTop: 6, paddingTop: 6 }}>
            <span style={{ color: "var(--teal-deep)", fontWeight: 600 }}>
              product = {a} × {b} = {product}
            </span>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 22, paddingTop: 16, borderTop: "1px solid var(--line)" }}>
        <h4 style={{ margin: "0 0 14px" }}>2 · Accumulate a dot product — the MAC</h4>
        <div className="sim-row">
          <div className="sim-col" style={{ minWidth: 0 }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "var(--mono)", fontSize: 13 }}>
              <thead>
                <tr style={{ color: "var(--muted)" }}>
                  <th style={{ textAlign: "left", padding: "4px 8px" }}>i</th>
                  <th style={{ textAlign: "right", padding: "4px 8px" }}>aᵢ</th>
                  <th style={{ textAlign: "right", padding: "4px 8px" }}>bᵢ</th>
                  <th style={{ textAlign: "right", padding: "4px 8px" }}>aᵢ·bᵢ</th>
                  <th style={{ textAlign: "right", padding: "4px 8px" }}>acc</th>
                </tr>
              </thead>
              <tbody>
                {VEC_A.map((av, i) => {
                  const done = i < step;
                  const running = VEC_A.slice(0, i + 1).reduce((s, x, j) => s + x * VEC_B[j], 0);
                  return (
                    <tr
                      key={i}
                      style={{
                        color: done ? "var(--ink)" : "var(--muted-2)",
                        background: i === step - 1 ? "var(--teal-bg)" : "transparent",
                      }}
                    >
                      <td style={{ padding: "4px 8px" }}>{i}</td>
                      <td style={{ textAlign: "right", padding: "4px 8px" }}>{av}</td>
                      <td style={{ textAlign: "right", padding: "4px 8px" }}>{VEC_B[i]}</td>
                      <td style={{ textAlign: "right", padding: "4px 8px" }}>{av * VEC_B[i]}</td>
                      <td style={{ textAlign: "right", padding: "4px 8px", fontWeight: 600 }}>
                        {done ? running : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="sim-col">
            <div className="sim-stat-label">Accumulator</div>
            <div className="sim-stat-big">{acc}</div>
            <div className="sim-controls" style={{ marginTop: 16 }}>
              <SimButton
                onClick={() => setStep((s) => Math.min(VEC_A.length, s + 1))}
                disabled={step >= VEC_A.length}
              >
                Step +
              </SimButton>
              <SimButton
                accent
                onClick={() => {
                  if (step >= VEC_A.length) setStep(0);
                  setPlaying((p) => !p);
                }}
              >
                {playing ? "Pause" : "Run"}
              </SimButton>
              <SimButton
                onClick={() => {
                  setStep(0);
                  setPlaying(false);
                }}
              >
                Reset
              </SimButton>
            </div>
            <p className="sim-note">
              <span className="lead">One unit, one operation. </span>
              A MAC multiplies a pair and adds it to a running total — <code>acc ← acc + aᵢbᵢ</code>.
              Run it across two vectors and you have computed a dot product. Stack dot products and
              you have a matrix multiply, which is nearly all of what a neural network does.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
