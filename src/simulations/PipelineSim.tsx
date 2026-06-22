import { useEffect, useState } from "react";
import { SimButton, SimSlider } from "../components/sim/controls";

const N = 6; // instructions in flight
const STAGE_NAMES = ["fetch", "decode", "exec", "mem", "write"];

export function PipelineSim() {
  const [k, setK] = useState(4); // pipeline stages
  const [pipelined, setPipelined] = useState(true);
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);

  const totalSeq = N * k;
  const totalPipe = N + k - 1;
  const maxC = pipelined ? totalPipe : totalSeq;

  useEffect(() => {
    setT(0);
    setPlaying(false);
  }, [k, pipelined]);

  useEffect(() => {
    if (!playing) return;
    if (t >= maxC - 1) {
      setPlaying(false);
      return;
    }
    const id = setTimeout(() => setT((x) => x + 1), 360);
    return () => clearTimeout(id);
  }, [playing, t, maxC]);

  // stage of instruction i at cycle c, or -1 if idle
  const stageOf = (i: number, c: number) => {
    if (pipelined) {
      const s = c - i;
      return s >= 0 && s < k ? s : -1;
    }
    const start = i * k;
    return c >= start && c < start + k ? c - start : -1;
  };

  const CELL = 30;
  const LABELW = 70;
  const W = LABELW + maxC * CELL + 10;
  const H = 40 + N * CELL + 24;

  const stageColor = (s: number) => {
    const shades = ["#BCE4E1", "#7FD0CA", "#3FB7AF", "#15A39C", "#0D7C77"];
    return shades[s % shades.length];
  };

  return (
    <div className="figure-card">
      <div className="sim-controls">
        <SimSlider label="stages" min={2} max={5} value={k} onChange={setK} />
        <SimButton active={pipelined} onClick={() => setPipelined(true)}>
          Pipelined
        </SimButton>
        <SimButton active={!pipelined} onClick={() => setPipelined(false)}>
          Sequential
        </SimButton>
        <div className="sim-spacer" />
        <SimButton onClick={() => setT((x) => Math.min(maxC - 1, x + 1))} disabled={t >= maxC - 1}>
          Clock +
        </SimButton>
        <SimButton
          accent
          onClick={() => {
            if (t >= maxC - 1) setT(0);
            setPlaying((p) => !p);
          }}
        >
          {playing ? "Pause" : "Run"}
        </SimButton>
      </div>

      <div className="sim-row">
        <div style={{ overflowX: "auto" }}>
          <svg width={W} height={H} style={{ display: "block" }}>
            {/* cycle header */}
            {Array.from({ length: maxC }).map((_, c) => (
              <text
                key={`c${c}`}
                x={LABELW + c * CELL + CELL / 2}
                y={20}
                textAnchor="middle"
                fontFamily="var(--mono)"
                fontSize={9}
                fill={c === t ? "var(--teal-deep)" : "var(--muted-2)"}
              >
                {c + 1}
              </text>
            ))}
            {/* current-clock column highlight */}
            <rect x={LABELW + t * CELL} y={28} width={CELL} height={N * CELL} fill="var(--teal-bg)" opacity={0.6} />
            {Array.from({ length: N }).map((_, i) => (
              <g key={`r${i}`}>
                <text x={8} y={40 + i * CELL + 19} fontFamily="var(--mono)" fontSize={11} fill="var(--muted)">
                  instr {i + 1}
                </text>
                {Array.from({ length: maxC }).map((_, c) => {
                  const s = stageOf(i, c);
                  if (s < 0) return null;
                  const shown = c <= t;
                  return (
                    <g key={`${i}-${c}`}>
                      <rect
                        x={LABELW + c * CELL + 1}
                        y={40 + i * CELL + 1}
                        width={CELL - 2}
                        height={CELL - 2}
                        rx={4}
                        fill={shown ? stageColor(s) : "var(--panel-2)"}
                        stroke="var(--line)"
                        strokeWidth={0.5}
                      />
                      <text
                        x={LABELW + c * CELL + CELL / 2}
                        y={40 + i * CELL + CELL / 2 + 3}
                        textAnchor="middle"
                        fontFamily="var(--mono)"
                        fontSize={8}
                        fill={shown && s >= 3 ? "#fff" : "var(--ink)"}
                      >
                        {STAGE_NAMES[s][0].toUpperCase()}
                      </text>
                    </g>
                  );
                })}
              </g>
            ))}
          </svg>
        </div>

        <div className="sim-col">
          <div className="sim-stat-label">{pipelined ? "Pipelined" : "Sequential"} — total cycles</div>
          <div className="sim-stat-big">{maxC}</div>
          <p className="sim-note">
            <span className="lead">
              {pipelined ? `${(totalSeq / totalPipe).toFixed(1)}× faster.` : "One at a time."}
            </span>{" "}
            A register between each stage lets {k} instructions occupy the {k} stages at once, like an
            assembly line. The latency of one instruction is unchanged ({k} cycles), but after the
            pipeline fills, a result pops out <em>every single cycle</em>. Sequential execution wastes{" "}
            {k - 1} of every {k} units; pipelining keeps them all busy.
          </p>
        </div>
      </div>
    </div>
  );
}
