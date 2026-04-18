import { loadCharacter } from "../lib/loader";
import { animate, buildSvgElement, prefersReducedMotion } from "../lib/animator";

export async function renderDetail(root: HTMLElement, id: string): Promise<void> {
  root.textContent = "";

  const back = document.createElement("a");
  back.className = "breadcrumb";
  back.href = "#/";
  back.textContent = "← Back to gallery";
  root.appendChild(back);

  let character;
  try {
    character = await loadCharacter(id);
  } catch (err) {
    const p = document.createElement("p");
    p.textContent = `Failed to load character '${id}': ${(err as Error).message}`;
    root.appendChild(p);
    return;
  }

  const wrap = document.createElement("div");
  wrap.className = "detail";
  root.appendChild(wrap);

  const stage = document.createElement("section");
  stage.className = "stage";
  wrap.appendChild(stage);

  const svg = buildSvgElement(character, {
    progresses: character.strokes.map(() => 0),
    background: true,
  });
  stage.appendChild(svg);

  const controls = document.createElement("div");
  controls.className = "controls";
  const playBtn = document.createElement("button");
  playBtn.textContent = "Play";
  const pauseBtn = document.createElement("button");
  pauseBtn.textContent = "Pause";
  const resetBtn = document.createElement("button");
  resetBtn.textContent = "Reset";
  controls.append(playBtn, pauseBtn, resetBtn);
  stage.appendChild(controls);

  const strokeOrder = document.createElement("p");
  strokeOrder.className = "stroke-order";
  strokeOrder.textContent = `Stroke 0 / ${character.strokeCount}`;
  stage.appendChild(strokeOrder);

  const controller = animate(svg, character);
  controller.onTick((tMs) => {
    let elapsed = 0;
    let current = 0;
    for (const s of character.strokes) {
      const d = s.durationMs ?? 500;
      if (tMs >= elapsed + d) current = s.index + 1;
      elapsed += d;
    }
    strokeOrder.textContent = `Stroke ${Math.min(current, character.strokeCount)} / ${character.strokeCount}`;
  });

  playBtn.addEventListener("click", () => controller.play());
  pauseBtn.addEventListener("click", () => controller.pause());
  resetBtn.addEventListener("click", () => controller.reset());

  document.addEventListener("keydown", function keyHandler(e) {
    if (!document.contains(root)) {
      document.removeEventListener("keydown", keyHandler);
      return;
    }
    if (e.key === " ") { e.preventDefault(); controller.toggle(); }
    if (e.key === "r" || e.key === "R") controller.reset();
  });

  if (!prefersReducedMotion()) {
    controller.play();
  }

  const info = document.createElement("aside");
  info.className = "info";
  wrap.appendChild(info);

  const name = document.createElement("h2");
  name.textContent = character.variantName;
  info.appendChild(name);

  const dl = document.createElement("dl");
  const rows: Array<[string, string | undefined]> = [
    ["Codepoint", character.codepoint ?? "(no Unicode codepoint)"],
    ["Stroke count", String(character.strokeCount)],
    ["Source", character.source.kind],
    ["Licence", character.source.license],
    ["Attribution", character.source.attribution ?? character.source.author],
  ];
  for (const [label, value] of rows) {
    if (!value) continue;
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    dl.append(dt, dd);
  }
  info.appendChild(dl);

  if (character.source.url) {
    const p = document.createElement("p");
    const a = document.createElement("a");
    a.href = character.source.url;
    a.textContent = "Upstream source";
    a.rel = "noopener noreferrer";
    a.target = "_blank";
    p.appendChild(a);
    info.appendChild(p);
  }

  if (character.description) {
    const p = document.createElement("p");
    p.textContent = character.description;
    info.appendChild(p);
  }
}
