import { useState } from "react";
import AllPathwaysFlow from "../components/flow/AllPathwaysFlow";
import MergedPathwaysFlow from "../components/flow/MergedPathwaysFlow";

export default function FlowBuilderPage() {
  const [mode, setMode] = useState<"single" | "merged">("single");
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <label className="text-sm text-gray-700">Visualization</label>
        <select
          className="border rounded-lg px-3 py-2"
          value={mode}
          onChange={(e) => setMode(e.target.value as "single" | "merged")}
        >
          <option value="single">Single Pathway</option>
          <option value="merged">All Pathways (Merged)</option>
        </select>
      </div>
      {mode === "single" ? <AllPathwaysFlow /> : <MergedPathwaysFlow />}
    </div>
  );
}
