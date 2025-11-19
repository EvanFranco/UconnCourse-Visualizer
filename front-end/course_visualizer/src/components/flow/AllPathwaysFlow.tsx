import React, { useMemo, useState } from "react";
import ReactFlow, { Background, Controls, MiniMap } from "reactflow";
import "reactflow/dist/style.css";
import type { DegreePlanTemplate } from "../../models/degreePlanTemplate";
import { expandRequirements } from "../../lib/planner/expandRequirements";
import { planSemesters } from "../../lib/planner/scheduler";
import { buildGraph } from "../../lib/planner/graph";
import csTemplate from "../../data/examples/cs-template.json";


const templates: DegreePlanTemplate[] = [csTemplate as DegreePlanTemplate];


export default function AllPathwaysFlow() {
const [templateIdx, setTemplateIdx] = useState(0);
const [maxCredits, setMaxCredits] = useState(16);
const [maxSemesters, setMaxSemesters] = useState(8);
const [pathIndex, setPathIndex] = useState(0);


const tpl = templates[templateIdx];


const courseSets = useMemo(() => expandRequirements(tpl.requirements), [tpl]);


const pathways = useMemo(() => {
return courseSets.map((set) => planSemesters(tpl.catalog, new Set(set), maxCredits, maxSemesters));
}, [courseSets, tpl, maxCredits, maxSemesters]);


const safeIndex = Math.min(pathIndex, Math.max(0, pathways.length - 1));
const semesters = pathways[safeIndex] ?? [];


const { nodes, edges } = useMemo(() => buildGraph(tpl.catalog, semesters), [tpl, semesters]);


return (
<div className="w-full h-[80vh] flex flex-col gap-3">
<div className="flex flex-wrap items-end gap-3 p-3 bg-white/60 rounded-xl shadow-sm border">
<div className="flex flex-col">
<label className="text-xs text-gray-600">Template</label>
<select className="border rounded-lg px-3 py-2" value={templateIdx} onChange={(e) => { setTemplateIdx(parseInt(e.target.value, 10)); setPathIndex(0); }}>
{templates.map((t, i) => (
<option key={t.majorName} value={i}>{t.majorName}</option>
))}
</select>
</div>
<div className="flex flex-col">
<label className="text-xs text-gray-600">Max credits / semester</label>
<input type="number" className="border rounded-lg px-3 py-2 w-28" value={maxCredits} min={6} max={21} onChange={(e) => setMaxCredits(parseInt(e.target.value || "0", 10))} />
</div>
<div className="flex flex-col">
<label className="text-xs text-gray-600">Max semesters</label>
<input type="number" className="border rounded-lg px-3 py-2 w-28" value={maxSemesters} min={1} max={12} onChange={(e) => setMaxSemesters(parseInt(e.target.value || "0", 10))} />
</div>
<div className="flex flex-col">
<label className="text-xs text-gray-600">Pathway</label>
<select className="border rounded-lg px-3 py-2 w-40" value={safeIndex} onChange={(e) => setPathIndex(parseInt(e.target.value, 10))}>
{pathways.map((p, i) => (
<option key={i} value={i}>{`Path ${i + 1} of ${pathways.length}`}</option>
))}
</select>
<span className="text-xs text-gray-600 mt-1">Total branches: {pathways.length}</span>
</div>
</div>


<div className="flex-1 border rounded-xl overflow-hidden">
<ReactFlow nodes={nodes} edges={edges} fitView>
<MiniMap pannable zoomable />
<Controls position="bottom-left" />
<Background variant="dots" gap={16} size={1} />
</ReactFlow>
</div>


<div className="text-xs text-gray-600">Legend: Blue cards are <b>Free Choice</b> placeholders.</div>
</div>
);
}