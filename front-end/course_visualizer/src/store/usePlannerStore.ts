import { create } from "zustand";


interface PlannerState {
maxCredits: number;
maxSemesters: number;
setMaxCredits: (n: number) => void;
setMaxSemesters: (n: number) => void;
}


export const usePlannerStore = create<PlannerState>((set) => ({
maxCredits: 16,
maxSemesters: 8,
setMaxCredits: (n) => set({ maxCredits: n }),
setMaxSemesters: (n) => set({ maxSemesters: n }),
}));