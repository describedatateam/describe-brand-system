"""How the ramp hexes in tokens.json were derived. Run it to see the
derivation; tokens.json holds the literal values, so nothing downstream
depends on this script and a ramp never shifts by accident.

  python3 tokens/derive_ramps.py

Sequential ramps hold one OKLCH hue and step lightness. Blue step 500 is
the brand blue itself. Diverging arms share one lightness per step, so the
two sides of zero weigh the same, and meet at a neutral grey.
"""
from colour import from_oklch, oklch

BLUE_H = oklch("#0F58E5")[2]      # 262.1, the brand blue's own hue
BRASS_H = 78                      # the categorical brass slot's hue

SEQ_L = {100: .95, 200: .88, 300: .79, 400: .68, 500: .516, 600: .42, 700: .33}
SEQ_C_BLUE = {100: .025, 200: .055, 300: .10, 400: .16, 500: .224, 600: .18, 700: .13}
SEQ_C_BRASS = {100: .03, 200: .06, 300: .09, 400: .115, 500: .12, 600: .11, 700: .09}

DIV_L_LIGHT = [.86, .76, .66, .56, .46]   # step 1 (near zero) -> 5 (far)
DIV_L_DARK = [.42, .52, .62, .72, .82]    # dark: magnitude gets lighter
DIV_C = [.05, .08, .11, .13, .15]


def ramp(h, cs):
    return {k: ("#0F58E5" if (h == BLUE_H and k == 500) else from_oklch(SEQ_L[k], cs[k], h))
            for k in SEQ_L}


def diverging(ls):
    return ([from_oklch(l, c, BRASS_H) for l, c in zip(ls, DIV_C)],
            [from_oklch(l, min(c, .17), BLUE_H) for l, c in zip(ls, DIV_C)])


if __name__ == "__main__":
    print("blue ", ramp(BLUE_H, SEQ_C_BLUE))
    print("brass", ramp(BRASS_H, SEQ_C_BRASS))
    for mode, ls, mid in (("light", DIV_L_LIGHT, (.95, 0, 0)), ("dark", DIV_L_DARK, (.33, 0, 0))):
        neg, pos = diverging(ls)
        print(mode, "brass arm", neg, "mid", from_oklch(*mid), "blue arm", pos)
