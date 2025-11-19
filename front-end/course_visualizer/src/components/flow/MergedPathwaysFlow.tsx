import React, { useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  Position,
} from "reactflow";
import "reactflow/dist/style.css";

import type { DegreePlanTemplate } from "../../models/degreePlanTemplate";
import type { MajorCatalog } from "../../models/course";
import type { Requirement, RequirementChoose } from "../../models/requirement";
import csTemplate from "../../data/examples/cs-template.json";
import { expandRequirements } from "../../lib/planner/expandRequirements";
import { planSemesters, type Pathway } from "../../lib/planner/scheduler";

const templates: DegreePlanTemplate[] = [csTemplate as DegreePlanTemplate];

type CountMap = Map<string, number>; // key -> count
// Node key format: `${courseId}@${semesterIndex}`
// Edge key format: `${srcCourseId}@${srcSem}->${dstCourseId}@${dstSem}`

function buildMergedGraph(
  catalog: MajorCatalog,
  requirements: Requirement[],
  pathways: Pathway[]
): { nodes: Node[]; edges: Edge[] } {
  // ---- vertical layout (semesters as ROWS) ----
  const laneHeight = 140;
  const laneGapY = 24;
  const cardW = 320;
  const cardH = 80;
  const hGap = 16;
  const lanePadding = 24;

  const nodeCounts: CountMap = new Map(); // includes FREE_
  const edgeCounts: CountMap = new Map();
  const inc = (m: CountMap, k: string, v = 1) => m.set(k, (m.get(k) ?? 0) + v);

  let maxSemesters = 0;
  pathways.forEach((p) => (maxSemesters = Math.max(maxSemesters, p.length)));

  // Count nodes (including FREE_) and edges (only prereq edges) across all paths
  pathways.forEach((p) => {
    // nodes
    p.forEach((sem, sIdx) => sem.forEach((cid) => inc(nodeCounts, `${cid}@${sIdx}`)));
    // prereq edges
    p.forEach((sem, sIdx) => {
      sem.forEach((cid) => {
        if (cid.startsWith("FREE_")) return;
        const prereqs = catalog[cid]?.prereqs ?? [];
        prereqs.forEach((pid) => {
          for (let k = 0; k <= sIdx; k++) {
            if (p[k].includes(pid)) {
              inc(edgeCounts, `${pid}@${k}->${cid}@${sIdx}`);
              break;
            }
          }
        });
      });
    });
  });

  const totalPaths = Math.max(1, pathways.length);

  // Compute a primary semester for each course (most frequent placement)
  const primarySemForCourse = new Map<string, number>();
  Object.keys(catalog).forEach((cid) => {
    let bestSem = 0;
    let bestCount = -1;
    for (let s = 0; s < maxSemesters; s++) {
      const count = nodeCounts.get(`${cid}@${s}`) ?? 0;
      if (count > bestCount) {
        bestSem = s;
        bestCount = count;
      }
    }
    primarySemForCourse.set(cid, bestSem);
  });

  // Build lanes and standard nodes
  const nodes: Node[] = [];
  for (let s = 0; s < maxSemesters; s++) {
    const laneId = `lane-${s + 1}`;
    const inLane = [...nodeCounts.keys()].filter((k) => k.endsWith(`@${s}`));
    const laneWidth =
      Math.max(1000, inLane.length * (cardW + hGap) + lanePadding * 2 + 16);

    nodes.push({
      id: laneId,
      type: "group",
      data: { label: `Semester ${s + 1}` },
      position: { x: 0, y: s * (laneHeight + laneGapY) },
      style: {
        width: laneWidth,
        height: laneHeight,
        borderRadius: 16,
        border: "1px solid #e5e7eb",
        padding: lanePadding,
        background: "#fafafa",
      },
    } as Node);

    inLane
      .sort((a, b) => a.localeCompare(b))
      .forEach((key, j) => {
        const [cid] = key.split("@");
        const freq = nodeCounts.get(key) ?? 0;
        const pct = Math.round((freq / totalPaths) * 100);

        const isFree = cid.startsWith("FREE_");
        const label = isFree
          ? freeChoiceLabel(cid)
          : `${catalog[cid].id}: ${catalog[cid].name} (${catalog[cid].credits} cr) — in ${freq}/${totalPaths} paths (${pct}%)`;

        nodes.push({
          id: key,
          parentNode: laneId,
          extent: "parent",
          position: { x: 8 + j * (cardW + hGap), y: 40 },
          data: { label },
          style: {
            borderRadius: 12,
            border: `1px solid ${isFree ? "#f59e0b" : "#d1d5db"}`,
            background: isFree
              ? "rgba(245,158,11,0.18)" // amber for Free Choice
              : `rgba(59,130,246,${0.15 + 0.6 * (freq / totalPaths)})`,
            padding: 8,
            width: cardW,
            height: cardH,
            display: "flex",
            alignItems: "center",
            fontSize: 12,
            boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
          },
          sourcePosition: Position.Bottom,
          targetPosition: Position.Top,
        } as Node);
      });
  }

  // Build solid prereq edges (distinct from choice edges)
  const edges: Edge[] = [];
  for (const [key, count] of edgeCounts.entries()) {
    const [src, dst] = key.split("->");
    edges.push({
      id: key,
      source: src,
      target: dst,
      type: "smoothstep",
      // solid line (default color) — thickness by frequency
      style: { stroke: "#000", strokeWidth: 3 }  ,
      label: undefined,
    });
  }

  // Add explicit CHOICE nodes (diamonds) + dashed amber edges to options
  let choiceCounter = 0;
  const choiceNodesByLane = new Map<number, number>(); // lane -> how many choice nodes placed (for horizontal offset)

  const chooseGroups = requirements.filter(
    (r): r is RequirementChoose => r.type === "choose",
  );

  for (const grp of chooseGroups) {
    // determine lane to place this choice: earliest primary semester among its options
    const primarySems = grp.from.map((cid) => primarySemForCourse.get(cid) ?? 0);
    const lane = Math.min(...primarySems);
    const laneId = `lane-${lane + 1}`;

    // horizontal offset for multiple choices in same lane
    const idxInLane = choiceNodesByLane.get(lane) ?? 0;
    choiceNodesByLane.set(lane, idxInLane + 1);

    const choiceId = `choice-${choiceCounter++}@${lane}`;
    const xPos = 8 + idxInLane * (cardW + hGap);
    const yPos = 40;

    // diamond style via CSS transform (square container rotated 45deg)
    nodes.push({
      id: choiceId,
      parentNode: laneId,
      extent: "parent",
      position: { x: xPos, y: yPos },
      data: { label: `Choose ${grp.count}` },
      style: {
        width: 44,
        height: 44,
        border: "2px solid #f59e0b",
        background: "rgba(245,158,11,0.15)",
        transform: "rotate(45deg)",
        borderRadius: 6,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
    } as Node);

    // dashed amber edges from choice -> each option’s primary node
    grp.from.forEach((cid) => {
      const sem = primarySemForCourse.get(cid) ?? lane;
      const targetId = `${cid}@${sem}`;
      edges.push({
        id: `${choiceId}->${targetId}`,
        source: choiceId,
        target: targetId,
        type: "smoothstep",
        animated: false,
        style: {
          stroke: "#f59e0b",
          strokeDasharray: "6 3",
          strokeWidth: 2,
        },
        label: "option",
        labelBgPadding: [4, 2],
        labelBgBorderRadius: 4,
        labelBgStyle: { fill: "rgba(245,158,11,0.12)" },
      });
    });
  }

  return { nodes, edges };
}

function freeChoiceLabel(freeId: string): string {
  const parts = freeId.split("_");
  const cr = parts[3] ? parseInt(parts[3], 10) : 1;
  return `Free Choice (≈${cr} cr)`;
}

export default function MergedPathwaysFlow() {
  const [templateIdx, setTemplateIdx] = useState(0);
  const [maxCredits, setMaxCredits] = useState(16);
  const [maxSemesters, setMaxSemesters] = useState(8);

  const tpl = templates[templateIdx];

  const courseSets = useMemo(() => expandRequirements(tpl.requirements), [tpl]);

  const pathways = useMemo(
    () =>
      courseSets.map((set) =>
        planSemesters(tpl.catalog, new Set(set), maxCredits, maxSemesters),
      ),
    [courseSets, tpl, maxCredits, maxSemesters],
  );

  const { nodes, edges } = useMemo(
    () => buildMergedGraph(tpl.catalog, tpl.requirements, pathways),
    [tpl, pathways],
  );

  return (
    <div className="w-full h-[80vh] flex flex-col gap-3">
      <div className="flex flex-wrap items-end gap-3 p-3 bg-white/60 rounded-xl shadow-sm border">
        <div className="flex flex-col">
          <label className="text-xs text-gray-600">Template</label>
          <select
            className="border rounded-lg px-3 py-2"
            value={templateIdx}
            onChange={(e) => setTemplateIdx(parseInt(e.target.value, 10))}
          >
            {templates.map((t, i) => (
              <option key={t.majorName} value={i}>
                {t.majorName}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col">
          <label className="text-xs text-gray-600">Max credits / semester</label>
          <input
            type="number"
            className="border rounded-lg px-3 py-2 w-28"
            value={maxCredits}
            min={6}
            max={21}
            onChange={(e) => setMaxCredits(parseInt(e.target.value || "0", 10))}
          />
        </div>
        <div className="flex flex-col">
          <label className="text-xs text-gray-600">Max semesters</label>
          <input
            type="number"
            className="border rounded-lg px-3 py-2 w-28"
            value={maxSemesters}
            min={1}
            max={12}
            onChange={(e) => setMaxSemesters(parseInt(e.target.value || "0", 10))}
          />
        </div>
        <div className="text-sm text-gray-700">
          Total pathways: <b>{pathways.length}</b>
        </div>
      </div>

      <div className="flex-1 border rounded-xl overflow-hidden">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <MiniMap pannable zoomable />
          <Controls position="bottom-left" />
          <Background variant="dots" gap={16} size={1} />
        </ReactFlow>
      </div>

      <div className="text-xs text-gray-600">
        <b>Legend:</b> solid lines = prerequisites; dashed amber lines = “choose K” options;
        amber cards = Free Choice credits.
      </div>
    </div>
  );
}
