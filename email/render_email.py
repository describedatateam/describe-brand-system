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
    role = "مؤسِّسة، <span dir=\"ltr\" style=\"font-weight:bold;color:%s;\">.describe(</span> لتحليل البيانات" % INK if rtl else \
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


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rtl = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "ar"
    args = [a for a in args if a not in ("ar", "en")]
    kind, path = args[0], args[1]
    text = open(path, encoding="utf-8").read()
    sys.stdout.write((outreach if kind == "outreach" else newsletter)(text, rtl))
