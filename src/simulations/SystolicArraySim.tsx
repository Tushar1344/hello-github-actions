import { useEffect, useMemo, useState } from "react";
import { SimButton, SimSlider } from "../components/sim/controls";

// Deterministic small matrices so the numbers stay readable.
const mkA = (n: number) =>
  Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => ((i + j) % 3) + 1));
const mkB = (n: number) =>
  Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => ((i * 2 + j) % 3) + 1));

export function SystolicArraySim() {
  const [n, setN] = useState(3);
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);

  const A = useMemo(() => mkA(n), [n]);
  const B = useMemo(() => mkB(n), [n]);
  const tMax = 3 * (n - 1); // cycle at which every accumulator is complete

  useEffect(() => {
    setT(0);
    setPlaying(false);
  }, [n]);

  useEffect(() => {
    if (!playing) return;
    if (t >= tMax) {
      setPlaying(false);
      return;
    }
    const id = setTimeout(() => setT((x) => x + 1), 650);
    return () => clearTimeout(id);
  }, [playing, t, tMax]);

  // For cell (i,j): the operand index streaming in at cycle t is k = t - i - j.
  const kAt = (i: number, j: number) => t - i - j;
  // accumulated value after the current cycle: fold terms k' = 0..min(k, n-1)
  const accAt = (i: number, j: number) => {
    const k = kAt(i, j);
    const upto = Math.min(k, n - 1);
    let s = 0;
    for (let kk = 0; kk <= upto; kk++) s += A[i][kk] * B[kk][j];
    return { acc: s, terms: Math.max(0, upto + 1) };
  };
  const finalC = (i: number, j: number) => {
    let s = 0;
    for (let k = 0; k < n; k++) s += A[i][k] * B[k][j];
    return s;
  };

  const CELL = 66;
  const PAD = 30;
  const W = n * CELL + PAD * 2;
  const H = n * CELL + PAD * 2;
  const done = t >= tMax;

  return (
    <div className="figure-card">
      <div className="sim-controls">
        <SimSlider label="N" min={2} max={4} value={n} onChange={setN} format={(v) => `${v}×${v}`} />
        <div className="sim-spacer" />
        <SimButton onClick={() => setT((x) => Math.min(tMax, x + 1))} disabled={done}>
          Clock +
        </SimButton>
        <SimButton
          accent
          onClick={() => {
            if (done) setT(0);
            setPlaying((p) => !p);
          }}
        >
          {playing ? "Pause" : "Run"}
        </SimButton>
        <SimButton
          onClick={() => {
            setT(0);
            setPlaying(false);
          }}
        >
          Reset
        </SimButton>
      </div>

      <div className="sim-row">
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ display: "block", maxWidth: "100%" }}>
          {/* top B-feed labels */}
          {Array.from({ length: n }).map((_, j) => (
            <text
              key={`bt${j}`}
              x={PAD + j * CELL + CELL / 2}
              y={18}
              textAnchor="middle"
              fontFamily="var(--mono)"
              fontSize={10}
              fill="var(--plum)"
            >
              B↓{j}
            </text>
          ))}
          {/* left A-feed labels */}
          {Array.from({ length: n }).map((_, i) => (
            <text
              key={`al${i}`}
              x={10}
              y={PAD + i * CELL + CELL / 2 + 4}
              fontFamily="var(--mono)"
              fontSize={10}
              fill="var(--teal-deep)"
            >
              A→{i}
            </text>
          ))}

          {A.map((_, i) =>
            B[0].map((_, j) => {
              const x = PAD + j * CELL;
              const y = PAD + i * CELL;
              const k = kAt(i, j);
              const active = k >= 0 && k < n;
              const { acc, terms } = accAt(i, j);
              const cellDone = terms >= n;
              const border = active ? "var(--teal-deep)" : cellDone ? "var(--teal-soft)" : "var(--line)";
              const bg = active ? "var(--teal-bg)" : "var(--panel)";
              return (
                <g key={`${i}-${j}`}>
                  <rect
                    x={x + 4}
                    y={y + 4}
                    width={CELL - 8}
                    height={CELL - 8}
                    rx={8}
                    fill={bg}
                    stroke={border}
                    strokeWidth={active ? 2 : 1}
                  />
                  {/* incoming operands this cycle */}
                  {active && (
                    <>
                      <text x={x + 14} y={y + 22} fontFamily="var(--mono)" fontSize={10} fill="var(--teal-deep)">
                        {A[i][k]}
                      </text>
                      <text x={x + CELL - 16} y={y + 22} fontFamily="var(--mono)" fontSize={10} fill="var(--plum)" textAnchor="end">
                        {B[k][j]}
                      </text>
                    </>
                  )}
                  {/* accumulator */}
                  <text
                    x={x + CELL / 2}
                    y={y + CELL / 2 + 10}
                    textAnchor="middle"
                    fontFamily="var(--serif)"
                    fontSize={20}
                    fontWeight={500}
                    fill={terms > 0 ? "var(--ink)" : "var(--muted-2)"}
                  >
                    {terms > 0 ? acc : "·"}
                  </text>
                </g>
              );
            }),
          )}
        </svg>

        <div className="sim-col">
          <div className="sim-stat-label">Clock cycle</div>
          <div className="sim-stat-big">
            {t}
            <span className="unit"> / {tMax}</span>
          </div>
          <p className="sim-note">
            <span className="lead">Compute moves to the data, not the other way round. </span>
            Rows of <span style={{ color: "var(--teal-deep)" }}>A</span> stream in from the left,
            columns of <span style={{ color: "var(--plum)" }}>B</span> from the top, skewed by one
            cycle per step. Each cell multiplies the pair passing through it, adds it to its own
            accumulator, then hands the operands to its neighbours. One memory read feeds an entire
            diagonal of multipliers.
          </p>
          {done && (
            <p className="sim-note" style={{ borderTop: "none", marginTop: 8 }}>
              <span className="lead">Done. </span>Every cell now holds its dot product —
              the array has computed C = A·B in {tMax + 1} cycles using {n * n} MACs, with no cell
              ever touching main memory.
            </p>
          )}
          {/* verify against ground truth */}
          {done && (
            <table
              style={{
                marginTop: 12,
                borderCollapse: "collapse",
                fontFamily: "var(--mono)",
                fontSize: 12,
              }}
            >
              <tbody>
                {A.map((_, i) => (
                  <tr key={i}>
                    {B[0].map((_, j) => (
                      <td
                        key={j}
                        style={{
                          padding: "4px 10px",
                          textAlign: "center",
                          color: "var(--teal-deep)",
                          border: "1px solid var(--line)",
                        }}
                      >
                        {finalC(i, j)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
