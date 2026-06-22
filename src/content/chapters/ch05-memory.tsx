import { Math } from "../../components/math/Math";
import { Callout } from "../../components/book/Callout";
import { MemorySim } from "../../simulations/MemorySim";

export function Chapter05() {
  return (
    <>
      <p>
        Chapter 3 told us the expensive thing is moving data, not computing on it. So a chip&rsquo;s
        most important real estate is its on-chip memory — the staging area that keeps operands close
        to the arithmetic. There are two philosophies for managing it, and the choice between them
        quietly separates a CPU from a TPU.
      </p>

      <h2 id="hierarchy">The memory hierarchy</h2>
      <p>
        Memory comes in a steep pyramid: a little bit of very fast, very expensive storage right next
        to the ALUs, backed by progressively larger and slower tiers. Reading from the top tier might
        cost a single cycle; reaching all the way to main memory can cost hundreds. The whole art is
        keeping the data you are about to use in the top tier — maximising <em>reuse</em> per
        expensive fetch.
      </p>

      <h2 id="cache-vs-scratch">Cache versus scratchpad</h2>
      <p>
        A <strong>cache</strong> manages the top tier automatically. Hardware guesses what you will
        need next — usually &ldquo;what you just used&rdquo; — and silently keeps it around. It is
        wonderful for unpredictable, branchy code, which is why CPUs are mostly cache. But the
        guessing costs transistors, and when your working set is larger than the cache, it evicts data
        you will need again and pays to re-fetch it.
      </p>
      <p>
        A <strong>scratchpad</strong> is the same fast memory with the autopilot removed: the program
        loads and evicts it by hand. That sounds like more work, and it is — but when the access
        pattern is known in advance, you can move each datum in exactly once and never re-fetch. Toggle
        between the two below and watch the fetch count.
      </p>

      <MemorySim />

      <Callout label="The big idea">
        <p>
          Matrix multiply has a perfectly predictable access pattern — you know every operand you will
          touch before you start. So the cache&rsquo;s guessing buys nothing, while its hardware costs
          area and energy. That is why AI accelerators replace caches with large, program-managed
          scratchpads: with <Math>{String.raw`C = AB`}</Math>, certainty beats cleverness.
        </p>
      </Callout>

      <h2 id="takeaway">Why this matters</h2>
      <p>
        We have now seen the same theme decide three things — the systolic array, the clock, and the
        memory system — all bending to &ldquo;reuse each byte as much as possible.&rdquo; Next we ask a
        higher-level question: should the circuit be fixed in silicon at all, or stay soft and
        reprogrammable? That is the FPGA-versus-ASIC choice.
      </p>
    </>
  );
}
