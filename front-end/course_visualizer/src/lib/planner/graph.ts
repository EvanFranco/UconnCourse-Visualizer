import { Position, type Edge, type Node } from "reactflow";
import type { MajorCatalog } from "../../models/course";

export function buildGraph(
  catalog: MajorCatalog,
  semesters: string[][]
): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  // ---- vertical layout (semesters as ROWS) ----
  const laneHeight = 120;      // row height
  const laneGapY = 24;
  const cardW = 320;
  const cardH = 72;
  const hGap = 16;
  const lanePadding = 24;

  semesters.forEach((sem, sIdx) => {
    const laneWidth =
      Math.max(800, sem.length * (cardW + hGap) + lanePadding * 2 + 16);
    const laneId = `lane-${sIdx + 1}`;

    nodes.push({
      id: laneId,
      type: "group",
      data: { label: `Semester ${sIdx + 1}` },
      position: { x: 0, y: sIdx * (laneHeight + laneGapY) },
      style: {
        width: laneWidth,
        height: laneHeight,
        borderRadius: 16,
        border: "1px solid #e5e7eb",
        padding: lanePadding,
        background: "#fafafa",
      },
    } as Node);

    // Place courses left→right inside the row
    sem.forEach((cid, j) => {
      const isFree = cid.startsWith("FREE_");
      const label = isFree
        ? freeChoiceLabel(cid)
        : `${catalog[cid].id}: ${catalog[cid].name} (${catalog[cid].credits} cr)`;

      nodes.push({
        id: `${cid}@${sIdx}`,
        parentNode: laneId,
        extent: "parent",
        position: { x: 8 + j * (cardW + hGap), y: 40 },
        data: { label },
        style: {
          borderRadius: 12,
          // AFTER (Tailwind greens: green-300 border, green-100 fill)
          border: `1px solid ${isFree ? "#86efac" : "#d1d5db"}`,  // green-300
          background: isFree ? "#dcfce7" : "white",               // green-100
          padding: 8,
          width: cardW,
          height: cardH,
          display: "flex",
          alignItems: "center",
          fontSize: 12,
          boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
        },
        // vertical flow anchors
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
      } as Node);
    });
  });

  // Prereq edges (vertical: from prior semester(s) to later rows)
  semesters.forEach((sem, sIdx) => {
    sem.forEach((cid) => {
      if (cid.startsWith("FREE_")) return; // no deps for placeholders
      const c = catalog[cid];
      c.prereqs.forEach((p) => {
        // find last semester index that contains prereq p
        for (let k = 0; k <= sIdx; k++) {
          const found = semesters[k].findIndex((x) => x === p);
          if (found >= 0) {
            edges.push({
              id: `${p}@${k}->${cid}@${sIdx}`,
              source: `${p}@${k}`,
              target: `${cid}@${sIdx}`,
              type: "smoothstep",
              style: { stroke: "#000", strokeWidth: 3 }  
            });
            break;
          }
        }
      });
    });
  });

  return { nodes, edges };
}

function freeChoiceLabel(freeId: string): string {
  // FREE_term_index_chunkCredits (e.g., FREE_1_2_3 → 3 credits)
  const parts = freeId.split("_");
  const cr = parts[3] ? parseInt(parts[3], 10) : 1;
  return `Free Choice (≈${cr} cr)`;
}
