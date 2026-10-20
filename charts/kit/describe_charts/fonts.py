"""
fonts.py — find the brand faces and hand them to matplotlib.

The faces are SIL OFL, loaded from Google Fonts; this repository does not
redistribute them (NOTICE.md). So the kit looks for them, in order:

    1. $DESCRIBE_FONTS_DIR
    2. ~/.cache/describe-fonts     (what `python -m describe_charts fonts` fills)
    3. decisions/fonts/ in this repo, when the kit runs from a checkout
    4. whatever is installed system-wide

and falls back to DejaVu quietly when none is found, which is the normal case
on a fresh server. Run `python -m describe_charts fonts` once per machine to
download them from the google/fonts repository. Plotly's static export
(kaleido) renders in Chrome, which only sees fonts installed for the user:
`python -m describe_charts fonts --install` also copies them there.
"""

from __future__ import annotations

import glob
import os
import shutil
import sys
import urllib.parse
import urllib.request

from .tokens import HERE, TOKENS

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "describe-fonts")
REPO_FONTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "decisions", "fonts"))
GOOGLE = "https://raw.githubusercontent.com/google/fonts/main/"


def search_dirs() -> list[str]:
    dirs = [os.environ.get("DESCRIBE_FONTS_DIR", ""), CACHE, REPO_FONTS]
    return [d for d in dirs if d and os.path.isdir(d)]


def font_files() -> list[str]:
    out = []
    for d in search_dirs():
        out += sorted(glob.glob(os.path.join(d, "*.ttf")) + glob.glob(os.path.join(d, "*.otf")))
    return out


def _family(path):
    from fontTools.ttLib import TTFont
    try:
        return TTFont(path, lazy=True)["name"].getBestFamilyName()
    except Exception:
        return None


def make_instances(dest: str = CACHE) -> list[str]:
    """Cut the static weights in tokens.json → font_instances from the
    variable faces, under their own family names ("Fraunces Light"), because
    matplotlib can only use a variable font at its default (Fraunces: 900)."""
    from fontTools.varLib.instancer import instantiateVariableFont
    from fontTools.ttLib import TTFont
    sources = {}
    for f in font_files():
        fam = _family(f)
        if fam and fam not in sources:
            sources[fam] = f
    made = []
    for name, spec in TOKENS.get("font_instances", {}).items():
        if name.startswith("_"):
            continue
        target = os.path.join(dest, name.replace(" ", "") + ".ttf")
        if name in sources or os.path.exists(target):
            made.append(target)
            continue
        src = sources.get(spec["from"])
        if not src:
            continue
        os.makedirs(dest, exist_ok=True)
        font = instantiateVariableFont(TTFont(src), spec["axes"])
        tbl = font["name"]
        for rec in list(tbl.names):
            if rec.nameID in (1, 3, 4, 16, 17, 21, 22, 25):
                tbl.removeNames(nameID=rec.nameID)
        tbl.setName(name, 1, 3, 1, 0x409)
        tbl.setName("Regular", 2, 3, 1, 0x409)
        tbl.setName(name, 4, 3, 1, 0x409)
        tbl.setName(name.replace(" ", "") + "-Regular", 3, 3, 1, 0x409)
        tbl.setName(name.replace(" ", "") + "-Regular", 6, 3, 1, 0x409)
        font["OS/2"].usWeightClass = spec["weight"]
        font.save(target)
        made.append(target)
    return made


def register_matplotlib() -> list[str]:
    """Add every brand face found to matplotlib's font manager. Returns the
    family names now available, so callers can tell brand from fallback."""
    from matplotlib import font_manager as fm
    try:
        make_instances()
    except Exception:      # no fontTools, read-only home: fall back to the variable defaults
        pass
    for path in font_files():
        try:
            fm.fontManager.addfont(path)
        except Exception:      # a broken file should never stop a chart
            pass
    have = {f.name for f in fm.fontManager.ttflist}
    wanted = {n for fam in TOKENS["fonts"].values() for n in fam}
    return sorted(n for n in wanted & have if not n.startswith("DejaVu"))


def download(dest: str = CACHE) -> list[str]:
    """Fetch the brand faces (OFL) from github.com/google/fonts into dest."""
    os.makedirs(dest, exist_ok=True)
    got = []
    for rel in TOKENS["font_files"].values():
        target = os.path.join(dest, os.path.basename(rel))
        if not os.path.exists(target):
            url = GOOGLE + urllib.parse.quote(rel, safe="/")
            urllib.request.urlretrieve(url, target)
        got.append(target)
    return got + make_instances(dest)


def install_user(files=None) -> str:
    """Copy the faces into the per-user font folder (macOS, Linux), where
    Chrome — and so Plotly's image export — can find them."""
    files = files or download()
    if sys.platform == "darwin":
        dest = os.path.expanduser("~/Library/Fonts")
    elif sys.platform.startswith("linux"):
        dest = os.path.expanduser("~/.local/share/fonts")
    else:
        raise OSError("On Windows, select the downloaded .ttf files and choose Install.")
    os.makedirs(dest, exist_ok=True)
    for f in files:
        shutil.copy2(f, dest)
    return dest
