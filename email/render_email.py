#!/usr/bin/env python3
"""Turn a short Markdown-ish text into a branded .describe( email (HTML).

Two kinds:
  outreach    personal 1:1 email (cold email, follow-up, offer). Looks like a
              normal letter: no banner, no images in the body, one compact
              signature. Heavy design hurts deliverability for cold email.
  newsletter  The .describe( Brief: logo header, sections, "Our take" notes,
              one button, footer.

Usage:
  python3 render_email.py outreach  body.md  > out.html  [--lang ar]
  python3 render_email.py newsletter issue.md > out.html [--lang ar]
  python3 render_email.py brief      issue.md > out.html [--lang ar] [--img-base URL]   rich Brief layout

Markup understood (keep it simple):
  # Title                 newsletter title (first line)
  _meta line_             newsletter date / edition line, right under the title
  ## Section              section heading
  - item / 1. item        lists
  **bold**  *italic*  [text](url)
  > Our take: ...         a tinted note block
  [[Button text](url)]    the one call-to-action button
  ---                     thin divider
  Plain paragraphs separated by a blank line.
Everything else is escaped. Inline CSS only, table layout, 600px max: safe in
Gmail, Outlook and Apple Mail.
"""
import html, re, sys

INK, BLUE, MUTED, LINE, TINT, PAPER = "#092052", "#0F58E5", "#64748B", "#CBD5E1", "#E6EFFF", "#F6F8FC"
LOGO = "https://raw.githubusercontent.com/describedatateam/describe-brand-system/claude/project-thread-xqhvx3/email/lockup-ink-40.png"
ICON = "https://raw.githubusercontent.com/describedatateam/describe-brand-system/claude/project-thread-xqhvx3/email/mark-44.png"
FONT_EN = "Arial,Helvetica,sans-serif"
FONT_AR = "Tahoma,Arial,sans-serif"


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|mailto:[^)\s]+)\)",
               lambda m: f'<a href="{m.group(2)}" style="color:{BLUE};text-decoration:underline;">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r'<strong style="color:%s;">\1</strong>' % INK, s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", s)
    return s


def blocks(text):
    out, para, lst = [], [], None

    def flush():
        nonlocal para, lst
        if para:
            out.append(("p", " ".join(para)))
            para = []
        if lst:
            out.append(lst)
            lst = None

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush(); continue
        m = re.match(r"^\s*(?:[-*]|(\d+)[.)])\s+(.*)", line)
        if m:
            if para:
                out.append(("p", " ".join(para))); para = []
            kind = "ol" if m.group(1) else "ul"
            if not lst or lst[0] != kind:
                if lst: out.append(lst)
                lst = (kind, [])
            lst[1].append(m.group(2)); continue
        flush() if lst else None
        if line.startswith("# "): flush(); out.append(("h1", line[2:])); continue
        if line.startswith("## ") or line.startswith("### "): flush(); out.append(("h2", line.split(" ", 1)[1])); continue
        if line.startswith("> "): flush(); out.append(("note", line[2:])); continue
        if line.strip() == "---": flush(); out.append(("hr", "")); continue
        b = re.match(r"^\[\[(.+?)\]\((https?://\S+?)\)\]$", line.strip())
        if b: flush(); out.append(("button", b.group(1), b.group(2))); continue
        para.append(line.strip())
    flush()
    return out


def render_blocks(bl, font, rtl):
    align = "right" if rtl else "left"
    p = f'margin:0 0 16px;font-family:{font};font-size:15px;line-height:24px;color:{INK};text-align:{align};'
    h = []
    for b in bl:
        k = b[0]
        if k == "p":
            h.append(f'<p style="{p}">{inline(b[1])}</p>')
        elif k == "h1":
            h.append(f'<h1 style="margin:0 0 6px;font-family:{font};font-size:26px;line-height:32px;font-weight:bold;color:{INK};text-align:{align};">{inline(b[1])}</h1>')
        elif k == "h2":
            h.append(f'<h2 style="margin:28px 0 10px;font-family:{font};font-size:18px;line-height:24px;font-weight:bold;color:{INK};text-align:{align};'
                     f'border-{ "right" if rtl else "left"}:3px solid {BLUE};padding-{ "right" if rtl else "left"}:10px;">{inline(b[1])}</h2>')
        elif k in ("ul", "ol"):
            items = "".join(f'<li style="margin:0 0 8px;">{inline(i)}</li>' for i in b[1])
            pad = "padding-right:22px;" if rtl else "padding-left:22px;"
            h.append(f'<{k} style="margin:0 0 16px;{pad}font-family:{font};font-size:15px;line-height:24px;color:{INK};">{items}</{k}>')
        elif k == "note":
            side = "right" if rtl else "left"
            h.append(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 16px;"><tr>'
                     f'<td style="background:{TINT};border-{side}:3px solid {BLUE};padding:12px 14px;font-family:{font};font-size:14px;line-height:22px;color:{INK};text-align:{align};">{inline(b[1])}</td></tr></table>')
        elif k == "hr":
            h.append(f'<div style="border-top:1px solid {LINE};margin:24px 0;line-height:1px;font-size:1px;">&nbsp;</div>')
        elif k == "button":
            h.append(f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 20px;" align="{ "right" if rtl else "left"}"><tr>'
                     f'<td style="background:{BLUE};border-radius:6px;"><a href="{b[2]}" style="display:inline-block;padding:12px 22px;font-family:{font};font-size:15px;font-weight:bold;color:#FFFFFF;text-decoration:none;">{inline(b[1])}</a></td></tr></table>'
                     f'<div style="clear:both;line-height:1px;font-size:1px;">&nbsp;</div>')
    return "\n".join(h)


def signature(rtl):
    font = FONT_AR if rtl else FONT_EN
    name = "وفاء الحايك" if rtl else "Wafa'a Al-Hayek"
    role = "مؤسِّسة <span style=\"font-weight:bold;color:%s;\">Describe</span> لتحليل البيانات" % INK if rtl else \
           "Founder, <span style=\"font-weight:bold;color:%s;\">.describe(</span> data analytics" % INK
    line = "اعرف ربحك الحقيقي، لا مبيعاتك فقط." if rtl else "See your real profit, not just your sales."
    call = "احجز مكالمة مجانية لمدة 20 دقيقة" if rtl else "Book a free 20-minute call"
    side, pad = ("right", "padding:0 12px 0 0;") if rtl else ("left", "padding:0 0 0 12px;")
    icon_pad = "padding:2px 0 0 12px;" if rtl else "padding:2px 12px 0 0;"
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" dir="{"rtl" if rtl else "ltr"}" style="margin-top:8px;border-collapse:collapse;font-family:{font};">'
            f'<tr><td valign="top" style="{icon_pad}"><a href="https://describe.team/"><img src="{ICON}" width="44" height="44" alt=".describe(" style="display:block;border:0;"></a></td>'
            f'<td valign="top" style="border-{side}:2px solid {BLUE};{pad}">'
            f'<div style="font-size:14px;line-height:19px;font-weight:bold;color:{INK};">{name}</div>'
            f'<div style="font-size:12px;line-height:17px;color:{MUTED};">{role}</div>'
            f'<div style="font-size:12px;line-height:17px;color:{INK};padding-top:4px;">{line}</div>'
            f'<div style="font-size:12px;line-height:17px;padding-top:4px;"><a href="https://describe.team/#contact" style="color:{BLUE};font-weight:bold;text-decoration:none;">{call}</a>'
            f' <span style="color:{MUTED};">&nbsp;·&nbsp; <a href="https://describe.team/" style="color:{MUTED};text-decoration:none;">describe.team</a></span></div>'
            f'</td></tr></table>')


def outreach(text, rtl=False):
    font = FONT_AR if rtl else FONT_EN
    body = render_blocks(blocks(text), font, rtl)
    return (f'<div dir="{"rtl" if rtl else "ltr"}" style="max-width:600px;font-family:{font};font-size:15px;line-height:24px;color:{INK};">'
            f'{body}{signature(rtl)}</div>')


def newsletter(text, rtl=False):
    font = FONT_AR if rtl else FONT_EN
    bl = blocks(text)
    title, meta = "The .describe( Brief", ""
    if bl and bl[0][0] == "h1":
        title = bl.pop(0)[1]
    if bl and bl[0][0] == "p" and re.fullmatch(r"_.+_", bl[0][1].strip()):
        meta = bl.pop(0)[1].strip("_")
    align = "right" if rtl else "left"
    unsub = "إلغاء الاشتراك: ردّ بكلمة «إيقاف»." if rtl else "Don't want these? Reply “stop” and you're off the list."
    why = "تصلك هذه النشرة لأنك اشتركت في describe.team/brief أو تواصلت معنا." if rtl else \
          "You get The Brief because you signed up at describe.team/brief or we've worked together."
    return f'''<!doctype html><html lang="{"ar" if rtl else "en"}" dir="{"rtl" if rtl else "ltr"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title></head>
<body style="margin:0;padding:0;background:{PAPER};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{PAPER};"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;background:#FFFFFF;border:1px solid {LINE};border-radius:10px;">
<tr><td style="padding:22px 28px 18px;border-bottom:3px solid {BLUE};" align="{align}">
<a href="https://describe.team/brief/"><img src="{LOGO}" width="168" height="40" alt=".describe(" style="display:block;border:0;width:168px;height:40px;"></a>
<div style="font-family:{FONT_EN};font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:{MUTED};padding-top:10px;">The Brief &middot; data news for online stores</div>
</td></tr>
<tr><td style="padding:26px 28px 8px;" dir="{"rtl" if rtl else "ltr"}">
<h1 style="margin:0 0 6px;font-family:{font};font-size:26px;line-height:32px;color:{INK};text-align:{align};">{inline(title)}</h1>
{f'<div style="font-family:{font};font-size:13px;line-height:20px;color:{MUTED};margin:0 0 20px;text-align:{align};">{inline(meta)}</div>' if meta else ''}
{render_blocks(bl, font, rtl)}
</td></tr>
<tr><td style="padding:4px 28px 24px;">{signature(rtl)}</td></tr>
<tr><td style="background:{PAPER};padding:16px 28px;border-top:1px solid {LINE};border-radius:0 0 10px 10px;font-family:{font};font-size:12px;line-height:18px;color:{MUTED};text-align:{align};">
{why}<br>{unsub}<br><a href="https://describe.team/" style="color:{MUTED};">describe.team</a>
</td></tr>
</table></td></tr></table></body></html>'''


# ---------------------------------------------------------------------------
# The Brief, rich layout. Section tags in the issue file: ## Title {lead} {news} {band} {cta}
# ---------------------------------------------------------------------------
import json as _json, os as _os

_T = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "tokens", "tokens.json"), encoding="utf-8"))["color"]
BRASS_100 = _T["viz"]["seq-alt"]["100"]["$value"]
BRASS_200 = _T["viz"]["seq-alt"]["200"]["$value"]
BRASS_500 = _T["viz"]["seq-alt"]["500"]["$value"]
BODY = _T["text"]["body"]["$value"]
NAVY_BLOCK = _T["brand"]["navy"]["$value"]
SERIF = "Georgia,'Times New Roman',serif"
IMG_BASE = "https://raw.githubusercontent.com/describedatateam/describe-brand-system/claude/occasion-posts/email/"


def _sections(text):
    head, secs, cur = [], [], None
    for line in text.splitlines():
        if line.startswith("## "):
            m = re.search(r"\s*\{(\w+)\}\s*$", line)
            title = re.sub(r"\s*\{\w+\}\s*$", "", line[3:])
            cur = [title, m.group(1) if m else "plain", []]
            secs.append(cur)
        elif cur is None:
            head.append(line)
        else:
            cur[2].append(line)
    return "\n".join(head), [(t, tag, "\n".join(b)) for t, tag, b in secs]


def _label(text, color, align="left"):
    return (f'<div style="font-family:{FONT_EN};font-size:11px;line-height:14px;letter-spacing:1.6px;text-transform:uppercase;'
            f'font-weight:bold;color:{color};text-align:{align};">{text}</div>')


def _h(text, color, size=26, align="left", margin="0 0 14px"):
    return f'<h2 style="margin:{margin};font-family:{SERIF};font-weight:normal;font-size:{size}px;line-height:{size + 6}px;color:{color};text-align:{align};">{inline(text)}</h2>'


def _p(text, color=INK, size=16, align="left", margin="0 0 16px", extra=""):
    return f'<p style="margin:{margin};font-family:{FONT_EN};font-size:{size}px;line-height:25px;color:{color};text-align:{align};{extra}">{inline(text)}</p>'


def _row(inner, bg="#FFFFFF", pad="28px 32px", border=""):
    return f'<tr><td style="background:{bg};padding:{pad};{border}">{inner}</td></tr>'


def _lead(title, body, img, alt, align):
    bl = blocks(body)
    out = [_label("The big one", BLUE, align), _h(title, INK, 30, align, "8px 0 14px")]
    i = 0
    while i < len(bl):
        b = bl[i]
        if b[0] == "p" and i + 1 < len(bl) and bl[i + 1][0] == "ol" and b[1].rstrip().endswith(":"):
            items = bl[i + 1][1]
            rows = "".join(
                f'<tr><td width="44" valign="top" style="padding:13px 0;border-top:1px solid {LINE};font-family:{SERIF};font-size:30px;line-height:30px;color:{BLUE};">{n}</td>'
                f'<td valign="middle" style="padding:13px 0;border-top:1px solid {LINE};font-family:{FONT_EN};font-size:15px;line-height:23px;color:{INK};text-align:{align};">{inline(t)}</td></tr>'
                for n, t in enumerate(items, 1))
            out.append(
                f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px;background:{TINT};border-radius:8px;"><tr><td style="padding:20px 22px 8px;">'
                f'{_label(inline(b[1].rstrip(":")), BLUE, align)}'
                f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:12px;">{rows}</table></td></tr></table>')
            i += 2
            continue
        if b[0] == "p":
            out.append(_p(b[1], INK, 16, align))
        i += 1
    hero = (f'<tr><td style="padding:0;line-height:0;font-size:0;"><img src="{img}" width="600" alt="{html.escape(alt)}" '
            f'style="display:block;width:100%;height:auto;border:0;"></td></tr>')
    return hero, _row("".join(out), pad="30px 32px 10px")


def _news(title, body, align):
    bl = blocks(body)
    out = [_label("This week", BLUE, align), _h(title, INK, 24, align, "8px 0 6px")]
    first = True
    for b in bl:
        if b[0] == "p" and b[1].startswith("**"):
            m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", b[1])
            sep = "" if first else f'<div style="border-top:1px solid {LINE};margin:20px 0 0;line-height:1px;font-size:1px;">&nbsp;</div>'
            out.append(sep + f'<h3 style="margin:{"14px" if first else "18px"} 0 6px;font-family:{FONT_EN};font-size:17px;line-height:23px;color:{INK};text-align:{align};">{inline(m.group(1))}</h3>'
                       + _p(m.group(2), BODY, 15, align, "0 0 12px"))
            first = False
        elif b[0] == "p":
            out.append(_p(b[1], BODY, 15, align))
        elif b[0] == "note":
            t = re.sub(r"^\*\*Our take:?\*\*:?\s*", "", b[1])
            t = t[:1].upper() + t[1:]
            side = "right" if align == "right" else "left"
            out.append(
                f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 4px;"><tr>'
                f'<td style="border-{side}:3px solid {BLUE};padding:2px 0 2px 14px;">{_label("Our take", BLUE, align)}'
                f'<div style="padding-top:5px;font-family:{FONT_EN};font-size:15px;line-height:24px;color:{INK};text-align:{align};">{inline(t)}</div></td></tr></table>')
    return _row("".join(out), pad="26px 32px 30px", border=f"border-top:1px solid {LINE};")


def _band(title, body, align):
    out = [_h(title, INK, 26, align, "0 0 14px")]
    for b in blocks(body):
        if b[0] == "p":
            out.append(_p(b[1], INK, 16, align))
        elif b[0] == "note":
            out.append(f'<p style="margin:18px 0 4px;padding-top:16px;border-top:2px solid {BRASS_500};font-family:{SERIF};font-style:italic;font-size:22px;line-height:30px;color:{INK};text-align:{align};">{inline(b[1])}</p>')
    return _row("".join(out), bg=BRASS_100, pad="30px 32px 28px")


def _cta(title, body, align):
    out = [_h(title, "#F6F8FC", 26, align, "0 0 14px")]
    for b in blocks(body):
        if b[0] == "p" and "button" not in b[1]:
            small = b[1].startswith("Not subscribed")
            out.append(_p(b[1], "#9FB0CC" if small else "#DBE4F5", 13 if small else 16, align, "18px 0 0" if small else "0 0 16px"))
        elif b[0] == "button":
            out.append(f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 4px;"><tr><td style="background:#F6F8FC;border-radius:6px;">'
                       f'<a href="{b[2]}" style="display:inline-block;padding:14px 26px;font-family:{FONT_EN};font-size:15px;font-weight:bold;color:{INK};text-decoration:none;">{inline(b[1])}</a></td></tr></table>')
    return _row("".join(out), bg=NAVY_BLOCK, pad="34px 32px 32px")


def brief(text, rtl=False, img_base=IMG_BASE, hero_alt="Countdown to White Friday"):
    align = "right" if rtl else "left"
    head, secs = _sections(text)
    hb = blocks(head)
    title = next((b[1] for b in hb if b[0] == "h1"), "The .describe( Brief")
    meta = next((b[1].strip("_") for b in hb if b[0] == "p" and re.fullmatch(r"_.+_", b[1].strip())), "")
    edition, _, lede = meta.partition(". ")
    sources = ""
    rows = []
    for t, tag, body in secs:
        if "\n---" in body:
            body, _, tail = body.partition("\n---")
            sources = tail.strip()
        if tag == "lead":
            hero, r = _lead(t, body, img_base + "brief-hero.png", hero_alt, align)
            rows += [hero, r]
        elif tag == "news":
            rows.append(_news(t, body, align))
        elif tag == "band":
            rows.append(_band(t, body, align))
        elif tag == "cta":
            rows.append(_cta(t, body, align))
        else:
            rows.append(_row(_h(t, INK, 22, align) + render_blocks(blocks(body), FONT_EN, rtl)))
    unsub = "إلغاء الاشتراك: ردّ بكلمة «إيقاف»." if rtl else "Don't want these? Reply “stop” and you're off the list."
    why = "تصلك هذه النشرة لأنك اشتركت في describe.team/brief أو تواصلت معنا." if rtl else \
          "You get The Brief because you signed up at describe.team/brief or we've worked together."
    src = f'<p style="margin:0 0 18px;font-family:{FONT_EN};font-size:12px;line-height:18px;color:{MUTED};text-align:{align};">{inline(sources)}</p>' if sources else ""
    side = "right" if rtl else "left"
    return f"""<!doctype html><html lang="{"ar" if rtl else "en"}" dir="{"rtl" if rtl else "ltr"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{html.escape(title)}</title></head>
<body style="margin:0;padding:0;background:{PAPER};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{PAPER};"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;background:#FFFFFF;border:1px solid {LINE};border-radius:10px;overflow:hidden;">
<tr><td style="padding:24px 32px 14px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td align="{side}"><a href="https://describe.team/brief/"><img src="{LOGO}" width="168" height="40" alt=".describe(" style="display:block;border:0;width:168px;height:40px;"></a></td>
<td align="{"left" if rtl else "right"}" valign="bottom" style="font-family:{FONT_EN};font-size:11px;line-height:15px;letter-spacing:1.6px;text-transform:uppercase;font-weight:bold;color:{MUTED};">{inline(edition)}</td>
</tr></table></td></tr>
<tr><td style="padding:0;line-height:0;font-size:0;"><img src="{img_base}brief-rule.png" width="600" alt="" style="display:block;width:100%;height:auto;border:0;"></td></tr>
<tr><td style="padding:24px 32px 26px;"><p style="margin:0;font-family:{SERIF};font-style:italic;font-size:20px;line-height:29px;color:{INK};text-align:{align};">{inline(lede)}</p></td></tr>
{"".join(rows)}
<tr><td style="padding:26px 32px 22px;">{src}{signature(rtl)}</td></tr>
<tr><td style="background:{PAPER};padding:16px 32px;border-top:1px solid {LINE};font-family:{FONT_EN};font-size:12px;line-height:18px;color:{MUTED};text-align:{align};">
{why}<br>{unsub}<br><a href="https://describe.team/" style="color:{MUTED};">describe.team</a></td></tr>
</table></td></tr></table></body></html>"""


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rtl = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "ar"
    base = sys.argv[sys.argv.index("--img-base") + 1] if "--img-base" in sys.argv else IMG_BASE
    args = [a for a in args if a not in ("ar", "en", base)]
    kind, path = args[0], args[1]
    text = open(path, encoding="utf-8").read()
    if kind == "brief":
        sys.stdout.write(brief(text, rtl, base))
    else:
        sys.stdout.write((outreach if kind == "outreach" else newsletter)(text, rtl))
