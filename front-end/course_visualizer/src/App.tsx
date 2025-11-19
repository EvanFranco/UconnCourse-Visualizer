import { Routes, Route, NavLink } from "react-router-dom";
import FlowBuilderPage from "./routes/FlowBuilderPage";
import TemplatesPage from "./routes/TemplatesPage";
import ImportExportPage from "./routes/ImportExportPage";


export default function App() {
return (
<div className="min-h-screen flex flex-col bg-sky-50">
<header className="border-b bg-white/70 backdrop-blur supports-[backdrop-filter]:bg-white/60">
<nav className="max-w-6xl mx-auto p-4 flex gap-6 text-sm">
<NavLink
to="/"
className={({ isActive }) =>
`px-2 py-1 rounded ${isActive ? "font-semibold text-blue-600" : "text-gray-700 hover:text-blue-600"}`
}
end
>
Flow
</NavLink>
<NavLink
to="/templates"
className={({ isActive }) =>
`px-2 py-1 rounded ${isActive ? "font-semibold text-blue-600" : "text-gray-700 hover:text-blue-600"}`
}
>
Templates
</NavLink>
<NavLink
to="/import"
className={({ isActive }) =>
`px-2 py-1 rounded ${isActive ? "font-semibold text-blue-600" : "text-gray-700 hover:text-blue-600"}`
}
>
Import/Export
</NavLink>
</nav>
</header>


<main className="max-w-6xl mx-auto p-4 flex-1 w-full">
<Routes>
<Route path="/" element={<FlowBuilderPage />} />
<Route path="/templates" element={<TemplatesPage />} />
<Route path="/import" element={<ImportExportPage />} />
</Routes>
</main>


<footer className="text-xs text-gray-500 border-t bg-white/50 p-3 text-center">
Course Visualizer
</footer>
</div>
);
}