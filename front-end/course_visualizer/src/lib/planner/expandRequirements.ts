import type { Requirement } from "../../models/requirement";
import { combinations } from "../utils/combinations";


/** Expand requirement model into ALL concrete sets of required courses */
export function expandRequirements(reqs: Requirement[]): string[][] {
let courseSets: string[][] = [[]];


for (const r of reqs) {
if (r.type === "allOf") {
courseSets = courseSets.map((set) => Array.from(new Set([...set, ...r.courses])));
} else if (r.type === "choose") {
const picks = combinations(r.from, r.count);
const next: string[][] = [];
for (const set of courseSets) {
for (const pick of picks) next.push(Array.from(new Set([...set, ...pick])));
}
courseSets = next;
}
}
// dedup
const m = new Map<string, string[]>();
for (const s of courseSets) m.set([...s].sort().join("|"), [...s]);
return [...m.values()];
}