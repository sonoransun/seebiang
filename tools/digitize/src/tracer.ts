type Point = [number, number];
type OnStroke = (pathData: string, median: Point[]) => void;

const MIN_POINT_SPACING = 4; // SVG-units; drop jittery sub-pixel samples

export function installTracer(
  container: HTMLElement,
  inkLayer: SVGSVGElement,
  onStroke: OnStroke,
): void {
  let active = false;
  let points: Point[] = [];
  let preview: SVGPathElement | null = null;

  const toSvg = (clientX: number, clientY: number): Point => {
    const rect = container.getBoundingClientRect();
    const vb = inkLayer.viewBox.baseVal;
    const w = vb.width || 1024;
    const h = vb.height || 1024;
    const x = ((clientX - rect.left) / rect.width) * w;
    const y = ((clientY - rect.top) / rect.height) * h;
    return [x, y];
  };

  const pointerdown = (e: PointerEvent) => {
    if (e.button !== 0) return;
    e.preventDefault();
    container.setPointerCapture(e.pointerId);
    active = true;
    points = [toSvg(e.clientX, e.clientY)];
    preview = document.createElementNS("http://www.w3.org/2000/svg", "path");
    preview.setAttribute("fill", "none");
    preview.setAttribute("stroke", "#b0302e");
    preview.setAttribute("stroke-width", "24");
    preview.setAttribute("stroke-linecap", "round");
    preview.setAttribute("stroke-linejoin", "round");
    preview.setAttribute("opacity", "0.6");
    inkLayer.appendChild(preview);
    updatePreview();
  };

  const pointermove = (e: PointerEvent) => {
    if (!active) return;
    const next = toSvg(e.clientX, e.clientY);
    const [lx, ly] = points[points.length - 1];
    if (Math.hypot(next[0] - lx, next[1] - ly) < MIN_POINT_SPACING) return;
    points.push(next);
    updatePreview();
  };

  const pointerup = (e: PointerEvent) => {
    if (!active) return;
    active = false;
    if (preview) preview.remove();
    preview = null;
    container.releasePointerCapture(e.pointerId);
    if (points.length < 2) return;
    const path = pointsToPath(points);
    onStroke(path, points.slice());
  };

  const updatePreview = () => {
    if (!preview) return;
    preview.setAttribute("d", pointsToPath(points));
  };

  container.addEventListener("pointerdown", pointerdown);
  container.addEventListener("pointermove", pointermove);
  container.addEventListener("pointerup", pointerup);
  container.addEventListener("pointercancel", pointerup);
}

function pointsToPath(pts: Point[]): string {
  if (pts.length === 0) return "";
  const parts = [`M ${pts[0][0].toFixed(2)} ${pts[0][1].toFixed(2)}`];
  for (let i = 1; i < pts.length; i++) {
    parts.push(`L ${pts[i][0].toFixed(2)} ${pts[i][1].toFixed(2)}`);
  }
  return parts.join(" ");
}
