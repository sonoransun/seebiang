/**
 * Load a reference SVG and copy its children into the tracer's reference layer.
 * Accepts /@fs/... paths (Vite) or relative URLs.
 */
export async function loadReference(target: SVGSVGElement, url: string): Promise<void> {
  if (!url) throw new Error("empty reference path");
  const res = await fetch(url);
  if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
  const text = await res.text();
  const doc = new DOMParser().parseFromString(text, "image/svg+xml");
  const root = doc.documentElement as unknown as SVGSVGElement;
  target.textContent = "";
  const vb = root.getAttribute("viewBox");
  if (vb) target.setAttribute("viewBox", vb);
  for (const node of Array.from(root.childNodes)) {
    target.appendChild(document.importNode(node, true));
  }
}
