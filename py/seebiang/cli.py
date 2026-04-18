"""Command-line interface: `seebiang <command> ...`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .io import data_root, iter_characters, load_character
from .validate import validate_all, validate_file, format_issues


def _cmd_validate(args) -> int:
    if args.id:
        path = data_root() / "characters" / f"{args.id}.json"
        issues = validate_file(path)
    else:
        issues = validate_all()
    if issues:
        print(format_issues(issues))
        errors = [i for i in issues if i.severity == "error"]
        return 1 if errors else 0
    print("ok: all character files valid")
    return 0


def _cmd_render(args) -> int:
    from . import render as r
    from . import animate as a

    characters = (
        [load_character(args.id)] if args.id else list(iter_characters())
    )
    outdir = Path(args.out_dir) if args.out_dir else data_root().parent / "outputs"
    outdir.mkdir(parents=True, exist_ok=True)

    for character in characters:
        if args.format in ("png", "all"):
            out_path = outdir / "png" / f"{character.id}.png"
            r.render_png(character, size=args.size, out_path=out_path)
            print(f"wrote {out_path}")
        if args.format in ("gif", "all"):
            out_path = outdir / "gif" / f"{character.id}.gif"
            _render_gif(character, out_path, fps=args.fps, size=args.size)
            print(f"wrote {out_path}")
        if args.format in ("apng", "all"):
            out_path = outdir / "apng" / f"{character.id}.png"
            _render_apng(character, out_path, fps=args.fps, size=args.size)
            print(f"wrote {out_path}")
    if args.format == "all":
        from .review import write_index

        index_path = write_index(outdir, characters)
        print(f"wrote {index_path}")
    return 0


def _render_gif(character, out_path: Path, fps: int, size: int) -> None:
    from . import render as r
    import imageio.v3 as iio
    import numpy as np

    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = [np.array(im.convert("RGB")) for im in r.render_frames(character, fps=fps, size=size)]
    iio.imwrite(str(out_path), frames, duration=int(1000 / fps), loop=0, extension=".gif")
    r._write_attribution_sidecar(character, out_path)


def _render_apng(character, out_path: Path, fps: int, size: int) -> None:
    from . import render as r

    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = list(r.render_frames(character, fps=fps, size=size))
    if not frames:
        return
    frames[0].save(
        out_path,
        format="PNG",
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
    )
    r._write_attribution_sidecar(character, out_path)


def _cmd_ls(args) -> int:
    for c in iter_characters():
        cp = c.codepoint or "-"
        print(f"{c.id}\t{cp}\tstrokes={len(c.strokes)}\t{c.variant_name}")
    return 0


def _cmd_review(args) -> int:
    from .review import write_index

    outdir = Path(args.out_dir) if args.out_dir else data_root().parent / "outputs"
    path = write_index(outdir)
    print(f"wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="seebiang", description="See Biáng! CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate character JSON files against the schema.")
    p_validate.add_argument("--id", help="Validate a single character by id")
    p_validate.set_defaults(func=_cmd_validate)

    p_ls = sub.add_parser("ls", help="List known characters.")
    p_ls.set_defaults(func=_cmd_ls)

    p_review = sub.add_parser("review", help="Write outputs/index.html contact sheet.")
    p_review.add_argument("--out-dir", help="Override output directory (default: outputs/)")
    p_review.set_defaults(func=_cmd_review)

    p_render = sub.add_parser("render", help="Render glyphs to static PNG and animated GIF/APNG.")
    p_render.add_argument("format", choices=["png", "gif", "apng", "all"])
    p_render.add_argument("--id", help="Render a single character by id (default: all)")
    p_render.add_argument("--size", type=int, default=1024, help="Output pixel size")
    p_render.add_argument("--fps", type=int, default=30)
    p_render.add_argument("--out-dir", help="Override output directory (default: outputs/)")
    p_render.set_defaults(func=_cmd_render)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
