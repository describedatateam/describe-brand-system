"""
tokens.py — the kit's single source of colour and type.

Colour comes from the brand's design tokens, tokens/dist/tokens.json (built
by tokens/build.py from tokens/tokens.json). When the kit runs from a
checkout it reads that file directly. When it is pip-installed, only this
folder ships, so it reads tokens.json beside it: a snapshot of the same
values, which charts/kit/check.py keeps identical to the shared file.

    from describe_charts.tokens import palette
    palette("dark")["story"]   # '#5B8DF0'
    palette()["cat"]           # the six categorical colours, in order
"""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.normpath(os.path.join(HERE, "..", "..", "..", "tokens", "dist", "tokens.json"))
SNAPSHOT = os.path.join(HERE, "tokens.json")

# chart role -> shared token
ROLES = {
    "ink": "color.text.ink", "body": "color.text.body", "dim": "color.text.dim",
    "rule": "color.line.rule", "faint": "color.line.faint",
    "ground": "color.surface.ground", "panel": "color.surface.panel",
    "story": "color.viz.story", "context": "color.viz.context",
    "mark": "color.role.mark", "pos": "color.role.pos", "neg": "color.role.neg",
}
DIV = ["n5", "n4", "n3", "n2", "n1", "0", "p1", "p2", "p3", "p4", "p5"]


def from_shared(path: str = SHARED) -> dict:
    """The chart subset of the shared design tokens, in the snapshot's shape."""
    with open(path, encoding="utf-8") as fh:
        t = json.load(fh)["tokens"]
    out = {}
    for mode in ("light", "dark"):
        p = {k: t[v][mode] for k, v in ROLES.items()}
        p["cat"] = [t[f"color.viz.cat.{i}"][mode] for i in range(1, 7)]
        seq = [t[f"color.viz.seq.{s}"][mode] for s in range(100, 800, 100)]
        # dark reverses the blue scale so small values recede into the surface (TOKENS.md)
        p["seq"] = seq if mode == "light" else seq[::-1]
        p["div"] = [t[f"color.viz.div.{s}"][mode] for s in DIV]
        out[mode] = p
    return out


with open(SNAPSHOT, encoding="utf-8") as fh:
    TOKENS = json.load(fh)
if os.environ.get("DESCRIBE_TOKENS") or os.path.exists(SHARED):
    TOKENS.update(from_shared(os.environ.get("DESCRIBE_TOKENS", SHARED)))

MODES = ("light", "dark")
FONTS = TOKENS["fonts"]
SIZE = TOKENS["size"]
STROKE = TOKENS["stroke"]


def palette(mode: str = "light") -> dict:
    if mode not in MODES:
        raise ValueError(f"mode is 'light' or 'dark', not {mode!r}")
    return dict(TOKENS[mode])
