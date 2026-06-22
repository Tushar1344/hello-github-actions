import { Math } from "../../components/math/Math";
import { Callout } from "../../components/book/Callout";
import { CoreBudgetSim } from "../../simulations/CoreBudgetSim";

export function Chapter07() {
  return (
    <>
      <p>
        CPU, GPU, TPU. They are made of the same transistors, fabricated on the same kind of silicon,
        built from the same gates. What makes them so different is a single decision repeated across
        the whole die: how much of your transistor budget do you spend on <em>control</em>, and how
        much on raw <em>arithmetic</em>?
      </p>

      <h2 id="budget">One die, one dial</h2>
      <p>
        Every chip has a fixed area budget. Spend it on control logic — branch predictors, out-of-
        order schedulers, deep caches — and a single thread of instructions runs blazingly fast. Spend
        it instead on arithmetic units, and you can do many operations at once but each is dumb and
        needs to be told exactly what to do. Slide the dial below from one extreme to the other.
      </p>

      <CoreBudgetSim />

      <h2 id="three">The three answers</h2>
      <p>
        A <strong>CPU</strong> sets the dial toward control: a handful of large, clever cores that
        chew through irregular, branchy code one fast thread at a time. A <strong>GPU</strong> pushes
        it toward arithmetic: thousands of small ALUs running in lockstep, magnificent at the same
        operation applied to mountains of data. A <strong>TPU</strong> pushes it nearly all the way:
        almost the entire die is one giant systolic array doing matrix multiply, with the bare minimum
        of control wrapped around it.
      </p>

      <Callout label="Reiner&rsquo;s framing">
        <p>
          A GPU is, to first order, a bunch of tiny TPUs. Each of its streaming multiprocessors is a
          small matrix-multiply engine; the GPU glues many of them together with enough general-
          purpose plumbing to stay flexible. Once you see the systolic array (Chapter 3) as the unit,
          GPUs and TPUs stop being different species and become points on one continuum.
        </p>
      </Callout>

      <h2 id="why-grew">Why the cores got smaller</h2>
      <p>
        For decades the dial sat near the CPU end, because most software is one sequential thread and
        latency was king. Deep learning changed the workload to something overwhelmingly parallel and
        regular — <Math>{String.raw`C = AB`}</Math> repeated trillions of times — which rewards
        throughput over latency. The optimal dial position slid hard toward arithmetic, and the
        industry followed it from CPUs to GPUs to TPUs.
      </p>

      <h2 id="takeaway">Why this matters</h2>
      <p>
        We have reduced an entire product taxonomy to one number. But <em>why</em> does throughput
        win, in hard quantities? To answer that we need to make the &ldquo;compute is cheap, movement
        is dear&rdquo; slogan numerical — which is the roofline, and the subject of the next chapter.
      </p>
    </>
  );
}
