import csTemplate from "../data/examples/cs-template.json";


export default function TemplatesPage() {
return (
<div className="space-y-4">
<h1 className="text-xl font-semibold">Templates</h1>
<pre className="p-4 border rounded-xl overflow-auto bg-white/70 text-xs">{JSON.stringify(csTemplate, null, 2)}</pre>
</div>
);
}