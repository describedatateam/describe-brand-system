"""round_sheet.py <tag> — shareable round images: desktop light (700w) and a mobile contact sheet (columns)."""
import sys
from PIL import Image
tag = sys.argv[1]
src = '/home/claude/website/shots/'
out = '/mnt/user-data/outputs/rounds/'
for theme in ('light', 'dark'):
    im = Image.open(f'{src}{tag}-desktop-{theme}.png').convert('RGB')
    w, h = im.size
    s = min(1, 700 / w, 4000 / h)
    im.resize((int(w * s), int(h * s)), Image.LANCZOS).save(f'{out}{tag}-desktop-{theme}.jpg', quality=85)
m = Image.open(f'{src}{tag}-mobile-light.png').convert('RGB')
w, h = m.size
cols = 5
seg = -(-h // cols)
sheet = Image.new('RGB', (cols * w + (cols - 1) * 16, seg), (203, 213, 225))
for i in range(cols):
    sheet.paste(m.crop((0, i * seg, w, min(h, (i + 1) * seg))), (i * (w + 16), 0))
s = min(1, 2000 / sheet.size[0], 4000 / sheet.size[1])
sheet.resize((int(sheet.size[0] * s), int(sheet.size[1] * s)), Image.LANCZOS).save(f'{out}{tag}-mobile-sheet.jpg', quality=85)
print('ok', tag)
