import { useEffect, useMemo, useState } from "react";
import { SimButton, SimSlider } from "../components/sim/controls";

// A reuse-heavy access stream (like a tiled matmul touching the same operands).
const STREAM = [0, 1, 2, 0, 1, 2, 3, 4, 3, 4, 5, 6, 5, 6, 7, 0];
const DISTINCT = new Set(STREAM).size;

export function MemorySim() {
  const [mode, setMode] = useState<"cache" | "scratchpad">("cache");
  const [cap, setCap] = useState(3);
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    setT(0);
    setPlaying(false);
  }, [mode, cap]);

  useEffect(() => {
    if (!playing) return;
    if (t >= STREAM.length) {
      setPlaying(false);
      return;
    }
    const id = setTimeout(() => setT((x) => x + 1), 420);
    return () => clearTimeout(id);
  }, [playing, t]);

  // Replay the LRU cache up to step t; record hit/miss per access + fetch count.
  const sim = useMemo(() => {
    const results: ("hit" | "miss")[] = [];
    let fetches = 0;
    const lru: number[] = [];
    for (let i = 0; i < STREAM.length; i++) {
      const a = STREAM[i];
      const idx = lru.indexOf(a);
      if (idx >= 0) {
        results.push("hit");
        lru.splice(idx, 1);
        lru.push(a);
      } else {
        results.push("miss");
        fetches++;
        lru.push(a);
        if (lru.length > cap) lru.shift();
      }
    }
    return { results, fetches };
  }, [cap]);

  // Cache contents after t steps.
  const cacheNow = useMemo(() => {
    const lru: number[] = [];
    for (let i = 0; i < t; i++) {
      const a = STREAM[i];
      const idx = lru.indexOf(a);
      if (idx >= 0) {
        lru.splice(idx, 1);
        lru.push(a);
      } else {
        lru.push(a);
        if (lru.length > cap) lru.shift();
      }
    }
    return lru;
  }, [t, cap]);

  const fetchesSoFar =
    mode === "cache"
      ? sim.results.slice(0, t).filter((r) => r === "miss").length
      : Math.min(t > 0 ? DISTINCT : 0, DISTINCT); // scratchpad: one bulk preload of the tile

  const totalFetches = mode === "cache" ? sim.fetches : DISTINCT;

  return (
    <div className="figure-card">
      <div className="sim-controls">
        <SimButton active={mode === "cache"} onClick={() => setMode("cache")}>
          Cache (auto)
        </SimButton>
        <SimButton active={mode === "scratchpad"} onClick={() => setMode("scratchpad")}>
          Scratchpad (explicit)
        </SimButton>
        {mode === "cache" && <SimSlider label="size" min={2} max={6} value={cap} onChange={setCap} />}
        <div className="sim-spacer" />
        <SimButton onClick={() => setT((x) => Math.min(STREAM.length, x + 1))} disabled={t >= STREAM.length}>
          Step +
        </SimButton>
        <SimButton
          accent
          onClick={() => {
            if (t >= STREAM.length) setT(0);
            setPlaying((p) => !p);
          }}
        >
          {playing ? "Pause" : "Run"}
        </SimButton>
      </div>

      {/* access tape */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 16 }}>
        {STREAM.map((a, i) => {
          const visited = i < t;
          const res = mode === "cache" ? sim.results[i] : i < DISTINCT ? "miss" : "hit";
          const isCurrent = i === t - 1;
          const bg = !visited
            ? "var(--panel-2)"
            : res === "hit"
              ? "var(--teal-bg)"
              : "#f7e6e6";
          return (
            <div
              key={i}
              style={{
                width: 30,
                height: 34,
                borderRadius: 4,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                background: bg,
                border: `1px solid ${isCurrent ? "var(--teal-deep)" : "var(--line)"}`,
                fontFamily: "var(--mono)",
                fontSize: 12,
                color: "var(--ink)",
              }}
            >
              <span>{a}</span>
              <span style={{ fontSize: 7, color: "var(--muted)" }}>
                {visited ? (res === "hit" ? "hit" : "load") : ""}
              </span>
            </div>
          );
        })}
      </div>

      <div className="sim-row">
        <div className="sim-col" style={{ minWidth: 220 }}>
          <div className="sim-stat-label">
            {mode === "cache" ? `Cache (LRU, size ${cap})` : "Scratchpad (preloaded tile)"}
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" }}>
            {(mode === "cache" ? cacheNow : t > 0 ? [...Array(DISTINCT).keys()] : []).map((a) => (
              <div
                key={a}
                style={{
                  width: 30,
                  height: 30,
                  borderRadius: 4,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: "var(--teal-deep)",
                  color: "var(--panel)",
                  fontFamily: "var(--mono)",
                  fontSize: 12,
                }}
              >
                {a}
              </div>
            ))}
          </div>
        </div>
        <div className="sim-col">
          <div className="sim-stat-label">Memory fetches (data movement)</div>
          <div className="sim-stat-big">
            {fetchesSoFar}
            <span className="unit"> / {totalFetches} total</span>
          </div>
          <p className="sim-note">
            <span className="lead">
              {mode === "cache" ? "Guesses, sometimes re-fetches." : "Each datum moved exactly once."}
            </span>{" "}
            {mode === "cache" ? (
              <>
                A cache manages itself with hardware (LRU here). Brilliant for unpredictable code —
                but when the working set exceeds its size, it evicts data it will need again and
                pays repeat fetches. Shrink the size and watch the misses climb.
              </>
            ) : (
              <>
                A scratchpad is memory the program fills by hand. When the access pattern is known
                ahead of time — exactly the case for matrix multiply — you preload the tile once and
                never re-fetch. No guessing hardware to pay for, and no capacity misses. This is why
                AI accelerators favour scratchpads.
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
