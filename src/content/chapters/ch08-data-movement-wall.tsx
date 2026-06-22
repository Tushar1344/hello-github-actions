import { Math, BlockMath } from "../../components/math/Math";
import { Callout } from "../../components/book/Callout";
import { RooflineSim } from "../../simulations/RooflineSim";

export function Chapter08() {
  return (
    <>
      <p>
        We have leaned on one slogan again and again: compute is cheap, moving data is dear. It is
        time to make it a number. The tool is the <strong>roofline</strong>, and it is the single most
        useful picture in all of hardware performance.
      </p>

      <h2 id="intensity">Arithmetic intensity</h2>
      <p>
        Define the key ratio — <strong>arithmetic intensity</strong> — as the number of operations you
        perform for every byte you move from memory:
      </p>
      <BlockMath>{String.raw`I = \frac{\text{FLOPs}}{\text{bytes moved}}`}</BlockMath>
      <p>
        A chip has two hard ceilings: a peak compute rate <Math>P</Math> (FLOP/s) and a memory
        bandwidth <Math>B</Math> (bytes/s). The performance you can actually attain on a workload of
        intensity <Math>I</Math> is whichever ceiling you hit first:
      </p>
      <BlockMath>{String.raw`\text{attainable} = \min\bigl(P,\; B \cdot I\bigr)`}</BlockMath>

      <h2 id="roofline">The roofline</h2>
      <p>
        Plot that and you get a roof: a slanted memory-bound region rising with <Math>I</Math>, then a
        flat compute-bound ceiling at <Math>P</Math>. They meet at the <strong>ridge point</strong>,{" "}
        <Math>{String.raw`I^\star = P/B`}</Math>. Drag the intensity below and watch which regime you
        fall into.
      </p>

      <RooflineSim />

      <h2 id="payoff">The whole book on one chart</h2>
      <p>
        Now the entire story snaps into focus. A lone multiply-accumulate that fetches both operands
        from memory has tiny intensity — it sits far to the left, deep in the memory-bound region,
        leaving the expensive ALUs idle. The systolic array exists precisely to raise <Math>I</Math>:
        by streaming one operand across a whole row of cells, it does dozens of multiplies per byte
        fetched, sliding the workload right, toward and past the ridge, where the chip finally runs at
        peak.
      </p>

      <Callout label="The big idea">
        <p>
          Pipelining, scratchpads, systolic arrays, the shift from CPUs to TPUs — every technique in
          this book is, at bottom, a scheme to push arithmetic intensity to the right of the ridge.
          That is what &ldquo;compute is cheap, movement is dear&rdquo; means, quantified.
        </p>
      </Callout>

      <h2 id="takeaway">Why this matters</h2>
      <p>
        If the goal is maximum arithmetic per byte moved, there is one system that has optimised it for
        millions of years by putting memory and compute in the same place: the brain. That comparison
        is where we turn next.
      </p>
    </>
  );
}
