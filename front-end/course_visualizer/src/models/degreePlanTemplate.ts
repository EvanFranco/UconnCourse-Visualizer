import type { MajorCatalog } from "./course";
import type { Requirement } from "./requirement";


export interface DegreePlanTemplate {
majorName: string;
catalog: MajorCatalog;
requirements: Requirement[];
}