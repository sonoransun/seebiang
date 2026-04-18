"""See Biáng! — static and animated visualisations of the Biáng character."""

from .io import Character, Stroke, load_character, iter_characters, data_root
from .animate import progresses_at_time, total_duration_ms
from .render import build_svg, render_png, render_frames

__all__ = [
    "Character",
    "Stroke",
    "load_character",
    "iter_characters",
    "data_root",
    "progresses_at_time",
    "total_duration_ms",
    "build_svg",
    "render_png",
    "render_frames",
]
