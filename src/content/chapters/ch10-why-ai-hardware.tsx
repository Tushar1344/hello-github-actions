import { Callout } from "../../components/book/Callout";
import { Figure } from "../../components/book/Figure";

const STACK = [
  { n: "1", t: "Logic gates", s: "switches → any boolean function, all from NAND" },
  { n: "2", t: "Multiply-accumulate", s: "gates → the one op all of AI runs on" },
  { n: "3", t: "Systolic array", s: "tile MACs; share operands to beat data movement" },
  { n: "4", t: "Pipelining", s: "cut the clock path; throughput without latency" },
  { n: "5", t: "Cache vs scratchpad", s: "predictable patterns → program-managed memory" },
  { n: "6", t: "FPGA vs ASIC", s: "how sure are you about the workload?" },
  { n: "7", t: "CPU · GPU · TPU", s: "one dial: control vs arithmetic" },
  { n: "8", t: "The roofline", s: "arithmetic per byte moved, quantified" },
  { n: "9", t: "Brains vs chips", s: "compute-in-memory at the biological limit" },
];

export function Chapter10() {
  return (
    <>
      <p>
        We opened with a claim: an AI accelerator is not magic, just one trick repeated at scale. We
        can now make that precise. Every layer we built was an answer to a single question —{" "}
        <strong>how do I do the most arithmetic per byte of data moved?</strong> — and the answers
        stack into the entire machine.
      </p>

      <h2 id="stack">The whole stack, in one view</h2>
      <Figure n="10.1" caption="Each layer rests on the ones below it; the same constraint shapes them all.">
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {STACK.map((row) => (
            <div
              key={row.n}
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 14,
                padding: "10px 14px",
                background: "var(--panel-2)",
                borderLeft: "2px solid var(--teal)",
                borderRadius: 4,
              }}
            >
              <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--teal-deep)", width: 18 }}>
                {row.n}
              </span>
              <span style={{ fontFamily: "var(--serif)", fontSize: 16, color: "var(--ink)", minWidth: 170 }}>
                {row.t}
              </span>
              <span style={{ fontSize: 13, color: "var(--muted)" }}>{row.s}</span>
            </div>
          ))}
        </div>
      </Figure>

      <h2 id="thesis">Why the hardware looks the way it does</h2>
      <p>
        Read the stack from the bottom and the &ldquo;zoo&rdquo; of chips dissolves into a single
        family. Matrix multiply dominates AI. Matrix multiply is multiply-accumulates with a perfectly
        predictable data-movement pattern. Predictable movement rewards systolic arrays, scratchpads,
        deep pipelines, and fixed-function ASICs. So the economics of moving data — not any arbitrary
        engineering taste — <em>forces</em> the shape of every AI accelerator on Earth. GPUs, TPUs,
        FPGAs, and even brains are just different resolutions of the same trade-off.
      </p>

      <Callout label="The thesis">
        <p>
          If you internalise one sentence from this book, make it this: an AI chip is a machine for
          maximising arithmetic per byte moved, and every design decision — from the choice of gate to
          the size of the scale-up domain — is a consequence of that one objective.
        </p>
      </Callout>

      <h2 id="forward">Where it goes next</h2>
      <p>
        The frontier is set by the same constraint. Compute per chip keeps climbing faster than memory
        bandwidth, so the data-movement wall presses harder every generation. The most interesting
        ideas ahead — bigger scale-up domains, sparser attention, and ultimately compute-in-memory
        designs that take the brain&rsquo;s hint seriously — are all attempts to move further right on
        the roofline. From a single transistor, we have arrived at the live edge of the field.
      </p>

      <h2 id="takeaway">The end of the beginning</h2>
      <p>
        You started with a switch. You can now explain why a TPU is mostly one enormous grid, why a GPU
        is a bunch of tiny ones, why scratchpads beat caches for this workload, and why a three-pound
        brain still embarrasses a kilowatt of silicon on efficiency. The machine is no longer magic —
        it is gates, all the way up.
      </p>
    </>
  );
}
