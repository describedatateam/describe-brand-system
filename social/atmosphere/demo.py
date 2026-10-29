# Two Replicate photos, four treatments, to check the atmosphere rules hold on new subjects.
from atmos import *
W, H = 1080, 880

# parcel: digits on navy, framed at the tape (the order that came back)
t = tone('demo/parcel.png', W, H, lo=0.12, hi=0.9, scale=0.95, offset=(140, 0))
t = focus(t, 560, 470, 230)
im = ascii(t, PALETTES['navy'], accent=ellipse(t.shape, 560, 470, 40, 260))
frame(im, (480, 170, 640, 790), 'RETURNED · 14% OF ORDERS', ground=PALETTES['navy']['ground']).save('demo/a_parcel_ascii.png')

# parcel: pixel grid on light ground
pixels(t, PALETTES['light'], cell=14, accent=ellipse(t.shape, 560, 470, 40, 260)).save('demo/b_parcel_pixels.png')

# field researcher: digits on paper, the tablet's own digits in blue
t2 = tone('demo/fieldworker.png', W, H, lo=0.12, hi=0.45, offset=(-60, 60))
t2 = focus(t2, 640, 420, 300)
TX, TY = 790, 680
ascii(t2, PALETTES['paper'], accent=ellipse(t2.shape, TX, TY, 80, 60)).save('demo/c_field_ascii.png')

# field researcher: halftone dots on navy, tablet framed
im = dots(t2, PALETTES['navy'], cell=10, accent=ellipse(t2.shape, TX, TY, 80, 60))
frame(im, (TX - 110, TY - 90, TX + 110, TY + 90), '312 SURVEYS · DAY 4', ground=PALETTES['navy']['ground']).save('demo/d_field_dots.png')
