"""
report.py — a short branded report, as HTML and PDF.

    from describe_charts.report import Report
    r = Report("Q3 sales review", dek="What moved, and what didn't.", client="Acme")
    r.section("Summary")
    r.text("Revenue rose in eight of ten regions ...")
    r.stats([("+12%", "Revenue vs Q2", "n = 10 regions")])
    r.figure(fig)                       # a matplotlib or Plotly figure
    r.table(df, n="n = 10 regions", source="Acme ERP export")
    r.save_html("report.html")          # Plotly figures stay interactive
    r.save_pdf("report.pdf")            # needs `pip install weasyprint`

Charts keep their own title, dek and provenance (set with finish()); the
report adds the page furniture around them: lockup, title, contents, the
running footer and the page numbers.
"""

from __future__ import annotations

import base64
import html
import io
import os
import re
from datetime import date
from string import Template

from .fonts import font_files
from .tokens import FONTS, HERE, palette

TEMPLATES = os.path.join(HERE, "templates")
GOOGLE_FONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400"
                "&family=Readex+Pro:wght@300;400;500&family=IBM+Plex+Mono:wght@400;500&display=swap")

esc = lambda s: html.escape(str(s), quote=True)


def _css_family(key):
    return ", ".join(f"'{f}'" for f in FONTS[key]) + (", serif" if key == "serif" else
                                                      ", monospace" if key == "mono" else ", sans-serif")


def _font_faces() -> str:
    """@font-face rules for any brand faces found on disk, so the PDF uses
    them offline. Matches by filename stem."""
    rules = []
    for path in font_files():
        stem = os.path.basename(path).lower()
        for fam, key, weight in (("Fraunces", "fraunces", "100 900"), ("Readex Pro", "readex", "160 700"),
                                 ("Vazirmatn", "vazirmatn", "100 900"),
                                 ("IBM Plex Mono", "ibmplexmono-regular", "400"),
                                 ("IBM Plex Mono", "ibmplexmono-medium", "500")):
            if stem.startswith(key):
                url = "file://" + path.replace("%", "%25").replace("[", "%5B").replace("]", "%5D")
                rules.append(f"@font-face{{font-family:'{fam}';src:url('{url}');font-weight:{weight};}}")
    return "\n".join(rules)


def _lockup(mode: str) -> str:
    p = palette(mode)
    with open(os.path.join(TEMPLATES, "lockup-compact.svg"), encoding="utf-8") as fh:
        svg = fh.read()
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
    return (svg.replace("var(--wm-ink,#092052)", p["ink"])
               .replace("var(--wm-accent,#0F58E5)", p["story"]))


def _is_plotly(fig) -> bool:
    return type(fig).__module__.startswith("plotly")


def _figure_svg(fig) -> str:
    if _is_plotly(fig):
        w = fig.layout.width or 900
        h = fig.layout.height or 520
        svg = fig.to_image(format="svg", width=w, height=h).decode("utf-8")
    else:
        buf = io.StringIO()
        fig.savefig(buf, format="svg")
        svg = buf.getvalue()
    svg = re.sub(r"<\?xml.*?\?>|<!DOCTYPE.*?>", "", svg, flags=re.S)
    # drop the root's fixed size so the chart scales to the column; viewBox stays
    root = re.search(r"<svg\b[^>]*>", svg)
    tag = re.sub(r'\s(width|height)="[^"]*"', "", root.group(0))
    return svg[:root.start()] + tag + svg[root.end():]


class Report:
    def __init__(self, title, dek=None, client=None, author=".describe(", issued=None, mode="light"):
        self.title, self.dek, self.client, self.author = title, dek, client, author
        self.issued = issued or date.today().strftime("%-d %B %Y")
        self.mode = mode
        self.blocks: list[tuple] = []

    # -- content -----------------------------------------------------------
    def section(self, heading):
        self.blocks.append(("section", heading))
        return self

    def text(self, paragraph):
        """A paragraph. **bold** is honoured; everything else is escaped."""
        self.blocks.append(("text", paragraph))
        return self

    def stats(self, items):
        """Stat tiles: [(value, label, note), ...]. Values set in Fraunces,
        proportional figures (CHARTS.md §6)."""
        self.blocks.append(("stats", list(items)))
        return self

    def figure(self, fig, caption=None):
        self.blocks.append(("figure", fig, caption))
        return self

    def table(self, df, caption=None, n=None, source=None, index=False, floatfmt="{:,.1f}"):
        self.blocks.append(("table", df, caption, n, source, index, floatfmt))
        return self

    # -- rendering ---------------------------------------------------------
    def _render_block(self, b, interactive):
        kind = b[0]
        if kind == "section":
            sid = re.sub(r"[^a-z0-9]+", "-", b[1].lower()).strip("-")
            return f'<h2 id="{sid}">{esc(b[1])}</h2>', (sid, b[1])
        if kind == "text":
            t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(b[1]))
            return f"<p>{t}</p>", None
        if kind == "stats":
            tiles = []
            for v, label, *note in b[1]:
                nt = f'<div class="stat__note">{esc(note[0])}</div>' if note and note[0] else ""
                tiles.append(f'<div class="stat"><div class="stat__value">{esc(v)}</div>'
                             f'<div class="stat__label">{esc(label)}</div>{nt}</div>')
            tiles = "".join(tiles)
            return f'<div class="stats">{tiles}</div>', None
        if kind == "figure":
            fig, cap = b[1], b[2]
            if interactive and _is_plotly(fig):
                body = fig.to_html(full_html=False, include_plotlyjs="cdn",
                                   config={"displaylogo": False, "responsive": True})
            else:
                body = _figure_svg(fig)
            capt = f"<figcaption>{esc(cap)}</figcaption>" if cap else ""
            return f'<figure class="chart">{body}{capt}</figure>', None
        if kind == "table":
            df, cap, n, src, index, ffmt = b[1:]
            d = df.reset_index() if index else df
            num = [str(d[c].dtype).startswith(("int", "float")) for c in d.columns]
            head = "".join(f'<th class="{"num" if k else ""}">{esc(c)}</th>' for c, k in zip(d.columns, num))
            rows = []
            for _, r in d.iterrows():
                cells = []
                for v, k in zip(r.values, num):
                    if v is None or (isinstance(v, float) and v != v):
                        cells.append('<td class="null">—</td>')       # null is never zero
                    elif k:
                        s = ffmt.format(v) if isinstance(v, float) else f"{v:,}"
                        cells.append(f'<td class="num">{esc(s)}</td>')
                    else:
                        cells.append(f"<td>{esc(v)}</td>")
                rows.append("<tr>" + "".join(cells) + "</tr>")
            prov = ""
            if n or src:
                prov = (f'<div class="prov"><span class="n">{esc(n or "")}</span>'
                        + (f" · Source: {esc(src)}" if src else "") + "</div>")
            capt = f"<caption>{esc(cap)}</caption>" if cap else ""
            return (f'<div class="table-wrap"><table>{capt}<thead><tr>{head}</tr></thead>'
                    f'<tbody>{"".join(rows)}</tbody></table>{prov}</div>'), None
        raise ValueError(kind)

    def html(self, interactive=True, for_pdf=False) -> str:
        parts, toc = [], []
        for b in self.blocks:
            h, entry = self._render_block(b, interactive and not for_pdf)
            parts.append(h)
            if entry:
                toc.append(entry)
        p = palette(self.mode)
        tokens = "".join(f"--{k}:{v};" for k, v in p.items() if isinstance(v, str))
        with open(os.path.join(TEMPLATES, "report.html"), encoding="utf-8") as fh:
            tpl = Template(fh.read())
        return tpl.substitute(
            title=esc(self.title),
            dek=f'<p class="dek">{esc(self.dek)}</p>' if self.dek else "",
            client=f'<span>Prepared for {esc(self.client)}</span>' if self.client else "",
            author=esc(self.author), issued=esc(self.issued),
            lockup=_lockup(self.mode), tokens=tokens, mode=self.mode,
            serif=_css_family("serif"), sans=_css_family("sans"), mono=_css_family("mono"),
            fontfaces=_font_faces() if for_pdf else "",
            fontlink="" if for_pdf else f'<link rel="stylesheet" href="{GOOGLE_FONTS}">',
            toc="".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc),
            body="\n".join(parts),
        )

    def save_html(self, path, interactive=True):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.html(interactive=interactive))
        return path

    def save_pdf(self, path):
        try:
            from weasyprint import HTML
        except ImportError as e:
            raise ImportError("PDF output needs WeasyPrint: pip install weasyprint") from e
        HTML(string=self.html(for_pdf=True), base_url=HERE).write_pdf(path)
        return path


def image_data_uri(path) -> str:
    """For dropping an exported PNG into a report or a slide."""
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()
