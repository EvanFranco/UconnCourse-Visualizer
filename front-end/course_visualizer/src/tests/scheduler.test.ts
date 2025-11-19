import { describe, it, expect } from "vitest";
import { planSemesters } from "../src/lib/planner/scheduler";


const catalog = {
A: { id: "A", name: "A", credits: 3, prereqs: [] },
B: { id: "B", name: "B", credits: 3, prereqs: ["A"] },
} as const;


describe("planSemesters", () => {
it("respects prereqs", () => {
const path = planSemesters(catalog as any, new Set(["A", "B"]), 6, 2);
expect(path.length).toBeGreaterThan(0);
// A appears in an earlier or same term as B
let termA = -1, termB = -1;
path.forEach((sem, i) => {
if (sem.includes("A")) termA = i;
if (sem.includes("B")) termB = i;
});
expect(termA).toBeLessThanOrEqual(termB);
});
});