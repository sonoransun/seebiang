"""Animation math shared between Python and (mirrored by) the TypeScript animator.

The two implementations must stay in step — see tests/py/test_animate.py and
the cross-pipeline parity test for enforcement.
"""

from __future__ import annotations

from typing import Sequence

from .io import Stroke


def total_duration_ms(strokes: Sequence[Stroke]) -> int:
    return sum(s.duration_ms for s in strokes)


def progresses_at_time(t_ms: float, strokes: Sequence[Stroke]) -> list[float]:
    """Per-stroke progress in [0, 1] at absolute time t_ms from animation start."""
    elapsed = 0.0
    out: list[float] = []
    for s in strokes:
        d = s.duration_ms
        if t_ms <= elapsed:
            out.append(0.0)
        elif t_ms >= elapsed + d:
            out.append(1.0)
        else:
            out.append((t_ms - elapsed) / d)
        elapsed += d
    return out


def frame_count(fps: int, strokes: Sequence[Stroke], tail_ms: int = 600) -> int:
    """Number of frames to emit for a full animation at the given fps.

    tail_ms keeps the completed glyph on screen for a moment before loop.
    """
    total = total_duration_ms(strokes) + tail_ms
    return max(1, int(round(total * fps / 1000.0)))
