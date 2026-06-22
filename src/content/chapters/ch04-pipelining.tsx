import { Math, BlockMath } from "../../components/math/Math";
import { Callout } from "../../components/book/Callout";
import { VideoDemo } from "../../components/video/VideoDemo";
import { PipelineSim } from "../../simulations/PipelineSim";

export function Chapter04() {
  return (
    <>
      <p>
        The systolic array gave us a way to keep thousands of multipliers fed. But we glossed over
        the clock that drives the whole dance. In this chapter we slow down and look at time itself —
        how a chip turns a deep chain of slow logic into a firehose of results, using nothing but a
        well-placed register.
      </p>

      <h2 id="clock">The clock and the register</h2>
      <p>
        Logic takes time to settle. A signal entering a chain of gates ripples through them, and only
        after the slowest path has settled is the output trustworthy. That worst-case settling time
        is the <strong>critical path</strong>, and it sets the fastest the clock can tick:
      </p>
      <BlockMath>{String.raw`f_{\max} = \frac{1}{t_{\text{critical path}}}`}</BlockMath>
      <p>
        A <strong>register</strong> is a gate-built memory cell that captures its input on each clock
        edge and holds it steady until the next. Drop registers into the middle of a long logic chain
        and you cut the critical path into shorter pieces — each piece now fits in a faster tick.
      </p>

      <h2 id="pipeline">Pipelining</h2>
      <p>
        Cutting the path into <Math>k</Math> stages does something better than just raising the clock:
        it lets <Math>k</Math> different operations occupy the <Math>k</Math> stages at once. Like an
        assembly line, while stage 3 works on item&nbsp;1, stage 2 works on item&nbsp;2 and stage 1 on
        item&nbsp;3. The <em>latency</em> of any single item is unchanged, but the <em>throughput</em>{" "}
        — items finished per cycle — approaches one, a <Math>k</Math>-fold win.
      </p>

      <PipelineSim />

      <Callout>
        <p>
          Latency and throughput are different currencies. Pipelining buys throughput without
          lowering latency — exactly the trade a chip wants, because it has billions of independent
          multiply-accumulates to run and only cares how many finish per second.
        </p>
      </Callout>

      <VideoDemo
        id="pipeline-fill"
        n="4.1"
        caption={
          <>
            An empty pipeline filling stage by stage. Once full, one result leaves every clock tick —
            the steady-state throughput that makes deep pipelines worthwhile.
          </>
        }
      />

      <h2 id="cost">The cost: bubbles and dependencies</h2>
      <p>
        Pipelining is not free. If one operation needs the result of the operation just ahead of it,
        the pipeline must stall — insert a <strong>bubble</strong> — until the answer is ready. In
        training, the forward and backward passes create exactly this hazard at the boundary between
        stages, and a great deal of systems engineering goes into keeping those bubbles small. The
        switch to <em>Sequential</em> in the simulator shows the extreme: every operation waits for
        the last to finish completely, wasting <Math>k-1</Math> of every <Math>k</Math> slots.
      </p>

      <h2 id="takeaway">Why this matters</h2>
      <p>
        Time on a chip is a resource to be pipelined, just as area is a resource to be tiled. With the
        clock understood, the next question is where the operands live between cycles — because the
        fastest pipeline in the world is useless if it is starved for data. That is the memory
        system, and it is next.
      </p>
    </>
  );
}
