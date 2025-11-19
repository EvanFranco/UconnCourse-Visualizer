import type { MajorCatalog } from "../../models/course";


export type Pathway = string[][]; // semesters → course IDs (or FREE_* placeholders)


export function planSemesters(
catalog: MajorCatalog,
required: Set<string>,
maxCredits: number,
maxSemesters: number
): Pathway {
const planned: Pathway = [];
const remaining = new Set(required);
const completed = new Set<string>();


const canTake = (cid: string) => catalog[cid].prereqs.every((p) => completed.has(p));


for (let term = 0; term < maxSemesters && remaining.size > 0; term++) {
let credits = 0;
const termCourses: string[] = [];


const available = [...remaining].filter(canTake).sort((a, b) => catalog[a].credits - catalog[b].credits);


for (const cid of available) {
const c = catalog[cid];
if (credits + c.credits <= maxCredits) { termCourses.push(cid); credits += c.credits; }
}


termCourses.forEach((cid) => remaining.delete(cid));


const remainingCredits = maxCredits - credits;
if (remainingCredits > 0) {
let leftover = remainingCredits, idx = 1;
while (leftover > 0) {
const chunk = Math.min(3, leftover);
termCourses.push(`FREE_${term + 1}_${idx}_${chunk}`);
leftover -= chunk; idx++;
}
}


planned.push(termCourses);
termCourses.forEach((cid) => { if (!cid.startsWith("FREE_")) completed.add(cid); });


if (remaining.size === 0 && termCourses.every((cid) => !cid.startsWith("FREE_"))) break;
}


return planned;
}