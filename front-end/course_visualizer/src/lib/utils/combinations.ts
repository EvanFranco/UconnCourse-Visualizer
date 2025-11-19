export function combinations<T>(arr: T[], k: number): T[][] {
const res: T[][] = [];
function backtrack(start: number, path: T[]) {
if (path.length === k) { res.push([...path]); return; }
for (let i = start; i < arr.length; i++) {
path.push(arr[i]);
backtrack(i + 1, path);
path.pop();
}
}
if (k === 0) return [[]];
backtrack(0, []);
return res;
}