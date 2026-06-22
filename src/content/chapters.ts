import type { ComponentType } from "react";
import { Chapter01 } from "./chapters/ch01-logic-gates";
import { Chapter02 } from "./chapters/ch02-multiply-accumulate";
import { Chapter03 } from "./chapters/ch03-systolic-array";
import { Chapter04 } from "./chapters/ch04-pipelining";
import { Chapter05 } from "./chapters/ch05-memory";
import { Chapter06 } from "./chapters/ch06-fpga-asic";
import { Chapter07 } from "./chapters/ch07-cpu-gpu-tpu";
import { Chapter08 } from "./chapters/ch08-data-movement-wall";
import { Chapter09 } from "./chapters/ch09-brains-vs-chips";
import { Chapter10 } from "./chapters/ch10-why-ai-hardware";

export interface Section {
  id: string;
  label: string;
}

export interface ChapterMeta {
  /** route slug */
  slug: string;
  /** display number, e.g. "1" */
  num: string;
  part: string;
  title: string;
  /** one-line blurb for the home list */
  blurb: string;
  /** small tag shown on the home row */
  tag: string;
  /** in-page sections for the right-rail TOC (ids must match heading ids) */
  sections: Section[];
  Component: ComponentType;
}

const PART_I = "Part I · The Atoms";
const PART_II = "Part II · Making It Fast";
const PART_III = "Part III · Architectures as Choices";
const PART_IV = "Part IV · Stepping Back";

export const chapters: ChapterMeta[] = [
  {
    slug: "logic-gates",
    num: "1",
    part: PART_I,
    title: "Logic Gates",
    blurb: "Transistors as switches, and the gates that turn voltage into truth.",
    tag: "foundations",
    sections: [
      { id: "switch", label: "The switch" },
      { id: "gates", label: "From switches to gates" },
      { id: "universal", label: "One gate to rule them all" },
      { id: "playground", label: "Gate playground" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter01,
  },
  {
    slug: "multiply-accumulate",
    num: "2",
    part: PART_I,
    title: "The Multiply-Accumulate",
    blurb: "Adders, multipliers, and the one operation that all of AI runs on.",
    tag: "foundations",
    sections: [
      { id: "adder", label: "Adding with gates" },
      { id: "multiply", label: "Multiplying" },
      { id: "mac", label: "The MAC" },
      { id: "builder", label: "MAC builder" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter02,
  },
  {
    slug: "systolic-array",
    num: "3",
    part: PART_II,
    title: "The Systolic Array",
    blurb: "Tile thousands of MACs into a grid and pump data through like a heartbeat.",
    tag: "the payoff",
    sections: [
      { id: "problem", label: "The data-movement wall" },
      { id: "idea", label: "The systolic idea" },
      { id: "matmul", label: "Mapping matrix multiply" },
      { id: "array", label: "Array simulator" },
      { id: "takeaway", label: "Why chips look this way" },
    ],
    Component: Chapter03,
  },
  {
    slug: "pipelining",
    num: "4",
    part: PART_II,
    title: "Clocks & Pipelining",
    blurb: "Turn a deep chain of slow logic into a firehose of results, one register at a time.",
    tag: "throughput",
    sections: [
      { id: "clock", label: "The clock & register" },
      { id: "pipeline", label: "Pipelining" },
      { id: "cost", label: "Bubbles & hazards" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter04,
  },
  {
    slug: "memory",
    num: "5",
    part: PART_II,
    title: "Cache vs Scratchpad",
    blurb: "Two philosophies for on-chip memory — and why AI chips pick the explicit one.",
    tag: "memory",
    sections: [
      { id: "hierarchy", label: "The memory hierarchy" },
      { id: "cache-vs-scratch", label: "Cache vs scratchpad" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter05,
  },
  {
    slug: "fpga-asic",
    num: "6",
    part: PART_III,
    title: "FPGA vs ASIC",
    blurb: "Soft, reprogrammable silicon versus fixed silicon baked for one job.",
    tag: "flexibility",
    sections: [
      { id: "fpga", label: "The FPGA" },
      { id: "asic", label: "The ASIC" },
      { id: "tradeoff", label: "The economics" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter06,
  },
  {
    slug: "cpu-gpu-tpu",
    num: "7",
    part: PART_III,
    title: "CPU · GPU · TPU",
    blurb: "Same silicon, one dial: how much goes to control versus arithmetic.",
    tag: "architectures",
    sections: [
      { id: "budget", label: "One die, one dial" },
      { id: "three", label: "The three answers" },
      { id: "why-grew", label: "Why cores shrank" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter07,
  },
  {
    slug: "data-movement-wall",
    num: "8",
    part: PART_III,
    title: "The Data-Movement Wall",
    blurb: "The roofline: compute-cheap, movement-dear, made into a number.",
    tag: "synthesis",
    sections: [
      { id: "intensity", label: "Arithmetic intensity" },
      { id: "roofline", label: "The roofline" },
      { id: "payoff", label: "The book on one chart" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter08,
  },
  {
    slug: "brains-vs-chips",
    num: "9",
    part: PART_IV,
    title: "Brains vs Chips",
    blurb: "Compute-in-memory at the biological limit — the opposite corner of the same space.",
    tag: "perspective",
    sections: [
      { id: "compare", label: "Two corners" },
      { id: "why", label: "Why brains are efficient" },
      { id: "takeaway", label: "Why this matters" },
    ],
    Component: Chapter09,
  },
  {
    slug: "why-ai-hardware",
    num: "10",
    part: PART_IV,
    title: "Why AI Hardware Looks the Way It Does",
    blurb: "Assemble the whole stack into one answer — and look at where it goes next.",
    tag: "the thesis",
    sections: [
      { id: "stack", label: "The whole stack" },
      { id: "thesis", label: "Why it looks this way" },
      { id: "forward", label: "Where it goes next" },
      { id: "takeaway", label: "The end of the beginning" },
    ],
    Component: Chapter10,
  },
];

export function chapterIndex(slug: string): number {
  return chapters.findIndex((c) => c.slug === slug);
}
