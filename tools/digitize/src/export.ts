interface StrokeRecord {
  index: number;
  path: string;
  median: [number, number][];
}

export function exportCharacter(id: string, strokes: StrokeRecord[]) {
  return {
    id,
    codepoint: null,
    variantName: id,
    description:
      "Digitised in the See Biáng! stroke tracer. Fill in variantName, source, and description before committing.",
    source: {
      kind: "hand-crafted",
      license: "CC0-1.0",
      attribution: "See Biáng! project",
    },
    canvas: { width: 1024, height: 1024 },
    strokeCount: strokes.length,
    strokes: strokes.map((s, i) => ({
      index: i,
      path: s.path,
      median: s.median.map(([x, y]) => [Number(x.toFixed(2)), Number(y.toFixed(2))]),
      durationMs: 500,
    })),
    schemaVersion: 1,
  };
}
