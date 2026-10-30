# Parcel, second take: the highlight is the shipping label, i.e. the order the post is about.
from atmos import *
W, H = 1080, 880
LX, LY = 526, 350  # shipping label centre after placement
t = tone('demo/parcel2.png', W, H, lo=0.15, hi=1.0, offset=(0, 100))
t = focus(t, LX, LY + 120, 320)
im = ascii(t, PALETTES['navy'], accent=ellipse(t.shape, LX, LY, 48, 30))
frame(im, (LX - 75, LY - 52, LX + 75, LY + 52), '1 IN 7 ORDERS COMES BACK',
      ground=PALETTES['navy']['ground'], side='right').save('demo/e_parcel_label.png')
