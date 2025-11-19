export type Course = {
id: string;
name: string;
credits: number;
prereqs: string[];
};


export type MajorCatalog = Record<string, Course>;