import { useState } from "react";


export default function ImportExportPage() {
const [json, setJson] = useState("{}");
return (
<div className="space-y-3">
<h1 className="text-xl font-semibold">Import / Export</h1>
<textarea className="w-full h-64 border rounded-xl p-3 font-mono text-sm" value={json} onChange={(e)=>setJson(e.target.value)} />
<div className="text-sm text-gray-600">Paste a template JSON here (schema matches <code>DegreePlanTemplate</code>).</div>
</div>
);
}