import { loadReference } from "./reference";
import { installTracer } from "./tracer";
import { exportCharacter } from "./export";

interface StrokeRecord {
  index: number;
  path: string;
  median: [number, number][];
}

const refPathInput = document.getElementById("ref-path") as HTMLInputElement;
const charIdInput = document.getElementById("char-id") as HTMLInputElement;
const loadBtn = document.getElementById("load-ref") as HTMLButtonElement;
const undoBtn = document.getElementById("undo") as HTMLButtonElement;
const clearBtn = document.getElementById("clear") as HTMLButtonElement;
const exportBtn = document.getElementById("export") as HTMLButtonElement;
const strokeList = document.getElementById("stroke-list") as HTMLOListElement;
const output = document.getElementById("output") as HTMLTextAreaElement;
const canvas = document.getElementById("canvas") as HTMLDivElement;
const ink = document.getElementById("ink") as unknown as SVGSVGElement;
const reference = document.getElementById("reference") as unknown as SVGSVGElement;

const strokes: StrokeRecord[] = [];

function renderList(): void {
  strokeList.textContent = "";
  for (const s of strokes) {
    const li = document.createElement("li");
    li.textContent = `#${s.index}: ${s.path.slice(0, 60)}${s.path.length > 60 ? "…" : ""}`;
    strokeList.appendChild(li);
  }
}

function renderInk(): void {
  ink.textContent = "";
  for (const s of strokes) {
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", s.path);
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", "#b0302e");
    p.setAttribute("stroke-width", "24");
    p.setAttribute("stroke-linecap", "round");
    p.setAttribute("stroke-linejoin", "round");
    p.setAttribute("opacity", "0.85");
    ink.appendChild(p);
  }
}

loadBtn.addEventListener("click", async () => {
  try {
    await loadReference(reference, refPathInput.value.trim());
  } catch (err) {
    alert(`Reference load failed: ${(err as Error).message}`);
  }
});

installTracer(canvas, ink, (pathData, median) => {
  strokes.push({ index: strokes.length, path: pathData, median });
  renderList();
  renderInk();
});

undoBtn.addEventListener("click", () => {
  strokes.pop();
  renderList();
  renderInk();
});

clearBtn.addEventListener("click", () => {
  if (!confirm("Clear all strokes?")) return;
  strokes.length = 0;
  renderList();
  renderInk();
});

exportBtn.addEventListener("click", () => {
  const id = charIdInput.value.trim() || "untitled";
  output.value = JSON.stringify(exportCharacter(id, strokes), null, 2);
  output.select();
});
