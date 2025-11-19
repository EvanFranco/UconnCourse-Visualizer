export type RequirementAllOf = { type: "allOf"; courses: string[] };
export type RequirementChoose = { type: "choose"; count: number; from: string[] };
export type Requirement = RequirementAllOf | RequirementChoose;