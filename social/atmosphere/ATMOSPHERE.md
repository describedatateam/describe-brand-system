# Image atmosphere

How .describe( images look, taken from the founder's moodboard (105 references, Oct 2026)
and the studies she approved. `atmos.py` applies these rules to any photo; `source.py`
makes the photo on Replicate.

## The idea

A real subject, rebuilt from data. From far it reads as a picture; up close it is digits,
cells or dots. The look comes from how the units are used, not from the subject.

## Rules

1. **One subject from a real photo.** An object, hands or a place on a plain dark background,
   chosen so one part of it carries the post's point. Avoid faces: digits and dots turn
   half-lit faces eerie. If a person is needed, use soft, even light and a relaxed expression. Make it with `source.py` (FLUX 1.1 Pro on Replicate, about
   $0.04 an image) or use a real photo. Never stock-photo clutter.
2. **One unit, on a strict grid.** Rebuild the photo from a single unit: digits (`ascii`),
   square cells (`pixels`), round dots (`dots`) or lines (`lines`). The grid stays visible.
3. **Tone lives in the unit, not in effects.** Brightness picks the glyph weight, cell fill
   step or dot size. Depth comes from that ramp: bright faces get medium-weight digits, mid
   tones regular digits, the shadow side drops to `:` and `.`. No blur, glow, grain,
   gradients or drop shadows.
4. **Light ink on navy.** Photo-based images use the `navy` palette. The inverted versions
   (navy ink on cream or off-white) were tried and don't work for photos; `paper` and `light`
   are kept only for drawn data, like the first S2 and S3.
5. **Guide attention the natural way.** Contrast fades away from the focus (`focus()`), so
   the eye settles on it without an arrow. The globe settles on the Arabian Peninsula this way.
6. **The highlight is the image's own units, recoloured, and it must mean something.** Recolour
   the digits of the one part of the photo that the post's number is about: the shipping
   label for a returns post, the region on a globe. If no part of the photo carries the
   meaning, pick another photo. Accent is brass. Nothing pasted on top.
7. **Optional: frame the focus.** Thin corner brackets with a short mono label (`frame()`),
   for a number that matters ("RETURNED · 14% OF ORDERS"). One frame per image.
8. **Type stays the brand's.** Fraunces headline, Readex body, Plex Mono labels, the lockup.
   Image models never draw text or the logo.

## Not this

- The star mark in images (tried as pointer and as separator; neither worked).
- Tiled shape patterns.
- Soft, glowing or grainy halftone (reads old in the wrong way).
- Images that dissolve upward into loose cells (study 01a).
- Half-lit or dramatic portraits (the field researcher test looked scary).
- Highlights on a part that carries no meaning (the parcel tape).
- Training a model on the moodboard: it is other designers' work. If a style model is
  trained later, train it on our own approved posts.

## Approved references

- `../studies-2026-10-29/p1.png`: Earth in digits from a Replicate photo.
- `../studies-2026-10-29/gb.png`: the same with a brass frame and label.
- `demo/post_returns.png`: parcel in digits, the shipping label highlighted.
- First-version S2 (digit line field) and S3 (dither cells) from 28 Oct.

## Use

```bash
python3 source.py demo/parcel.png "a cardboard delivery parcel handed between two hands, seen from above" 4:5
python3 demo.py   # shows tone(), focus(), a treatment, accent and frame together
```
