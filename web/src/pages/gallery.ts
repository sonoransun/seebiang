import { loadCharacter, loadIndex } from "../lib/loader";
import { buildSvgElement } from "../lib/animator";

export async function renderGallery(root: HTMLElement): Promise<void> {
  root.textContent = "";
  const heading = document.createElement("h2");
  heading.textContent = "Gallery";
  root.appendChild(heading);

  const list = document.createElement("ul");
  list.className = "gallery";
  root.appendChild(list);

  let index;
  try {
    index = await loadIndex();
  } catch (err) {
    const p = document.createElement("p");
    p.textContent = `Failed to load character index: ${(err as Error).message}`;
    root.appendChild(p);
    return;
  }

  for (const entry of index.characters) {
    const li = document.createElement("li");
    const link = document.createElement("a");
    link.href = `#/variant/${entry.id}`;
    link.setAttribute("aria-label", `${entry.variantName}, ${entry.strokeCount} strokes`);

    try {
      const character = await loadCharacter(entry.id);
      const svg = buildSvgElement(character, { background: true });
      link.appendChild(svg);
    } catch (err) {
      const note = document.createElement("p");
      note.textContent = `Preview failed: ${(err as Error).message}`;
      link.appendChild(note);
    }

    const meta = document.createElement("p");
    meta.className = "meta";
    const name = document.createElement("strong");
    name.textContent = entry.variantName;
    const count = document.createElement("span");
    count.textContent = `${entry.strokeCount} strokes`;
    meta.append(name, count);
    link.appendChild(meta);

    li.appendChild(link);
    list.appendChild(li);
  }
}
