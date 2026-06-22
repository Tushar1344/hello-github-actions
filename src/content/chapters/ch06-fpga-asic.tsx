import { Math } from "../../components/math/Math";
import { Callout } from "../../components/book/Callout";
import { FabricSim } from "../../simulations/FabricSim";

export function Chapter06() {
  return (
    <>
      <p>
        Everything so far has been built from gates, but we never asked a basic manufacturing
        question: once you etch a circuit into silicon, it is permanent. So how do you build hardware
        for a workload that might change? This is the tension between flexibility and efficiency, and
        it defines two whole categories of chip.
      </p>

      <h2 id="fpga">The FPGA: soft silicon</h2>
      <p>
        A <strong>field-programmable gate array</strong> is a sea of small configurable logic blocks
        connected by a mesh of programmable wires. You download a configuration and the fabric{" "}
        <em>becomes</em> your circuit; download a different one and it becomes something else. The cost
        is overhead: a large share of the die is routing and configuration machinery rather than the
        logic you actually wanted. Press <em>Reprogram</em> below to watch the same fabric take on a
        new function.
      </p>

      <FabricSim />

      <h2 id="asic">The ASIC: hard silicon</h2>
      <p>
        An <strong>application-specific integrated circuit</strong> throws flexibility away. The
        design is fixed at manufacture — every transistor does useful work, nothing is spent on
        routing you might reconfigure. The result is the fastest, most power-efficient, cheapest-per-
        unit chip you can build, at the price of an enormous up-front engineering cost and zero
        ability to change after the fact.
      </p>

      <h2 id="tradeoff">The economics</h2>
      <p>
        The choice is a bet on volume and stability. ASICs carry a large fixed cost (the{" "}
        <em>non-recurring engineering</em>, or NRE) but a tiny per-unit cost; FPGAs invert that. So
        total cost looks like
      </p>
      <p style={{ textAlign: "center" }}>
        <Math>{String.raw`\text{cost}_{\text{ASIC}} = \text{NRE} + n \cdot c_{\text{low}} \quad\text{vs}\quad \text{cost}_{\text{FPGA}} = n \cdot c_{\text{high}}`}</Math>
      </p>
      <p>
        Below some crossover volume the FPGA wins; above it, the ASIC does. For a workload that is both
        enormous in volume and stable in shape, the ASIC is the obvious call.
      </p>

      <Callout>
        <p>
          Matrix multiply is exactly that workload: astronomically high-volume and unchanging in
          structure. That is the bet a TPU makes — it is essentially an ASIC that does one thing,
          <Math>{String.raw`\;C = AB`}</Math>, as efficiently as physics allows.
        </p>
      </Callout>

      <h2 id="takeaway">Why this matters</h2>
      <p>
        &ldquo;How fixed should the circuit be?&rdquo; is the same question as &ldquo;how sure are you
        about the workload?&rdquo; With that settled, we can finally compare the three chips everyone
        actually argues about — CPU, GPU, and TPU — and see that they differ by exactly one dial.
      </p>
    </>
  );
}
