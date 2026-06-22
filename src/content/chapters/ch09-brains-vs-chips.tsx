import { Math } from "../../components/math/Math";
import { Callout } from "../../components/book/Callout";
import { BrainChipSim } from "../../simulations/BrainChipSim";

export function Chapter09() {
  return (
    <>
      <p>
        Hold an AI accelerator and a human brain side by side. One runs on hundreds of watts and a
        nine-figure budget; the other runs on the energy of a dim light bulb and fits in your skull.
        They sit at opposite corners of the same design space — and the axis between them is the one we
        have circled all book: data movement.
      </p>

      <h2 id="compare">Two corners of one space</h2>
      <p>
        Switch between the metrics below. The pattern is consistent: the chip wins overwhelmingly on
        speed, the brain wins overwhelmingly on power and energy efficiency, and the reason for both
        is the same architectural choice.
      </p>

      <BrainChipSim />

      <h2 id="why">Why the brain is so efficient</h2>
      <p>
        A chip separates memory from compute and spends most of its energy shuttling data between them
        across the data-movement wall of Chapter 8. The brain does the opposite: a synapse is{" "}
        <em>both</em> the memory and the computation. Weights live exactly where they are used, so
        there is almost nothing to move. It is, in effect, the most extreme scratchpad imaginable —
        compute-in-memory taken to its biological limit.
      </p>
      <p>
        The price the brain pays is speed. Neurons fire at <Math>{String.raw`\sim 10^2`}</Math> Hz,
        seven orders of magnitude slower than a chip&rsquo;s <Math>{String.raw`\sim 10^9`}</Math> Hz
        clock. It makes up the deficit with breathtaking parallelism —{" "}
        <Math>{String.raw`\sim 10^{11}`}</Math> neurons all working at once.
      </p>

      <Callout>
        <p>
          Brains and chips are not better or worse than each other; they are the same trade-off
          resolved in opposite directions. Slow-and-local versus fast-and-shuttling. Both are answers
          to &ldquo;how much arithmetic can I do per unit of data moved?&rdquo;
        </p>
      </Callout>

      <h2 id="takeaway">Why this matters</h2>
      <p>
        The brain is an existence proof that compute-in-memory can be wildly more efficient than what
        we build today — and a hint about where chips might go next. With that, we have all the pieces.
        The final chapter steps back and assembles them into a single answer to the question this book
        opened with.
      </p>
    </>
  );
}
