import { describe, it, expect } from "vitest";
import { expandRequirements } from "../src/lib/planner/expandRequirements";


describe("expandRequirements", () => {
it("expands choose groups", () => {
const reqs = [
{ type: "allOf", courses: ["A"] },
{ type: "choose", count: 2, from: ["B", "C", "D"] },
] as const;
const sets = expandRequirements(reqs as any);
expect(sets.length).toBe(3); // 3C2
});
});