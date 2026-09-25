import sys
from PIL import Image, ImageDraw
# usage: quad.py out.jpg t1 t2 t3 t4 [scale]
out=sys.argv[1]; ts=[float(x) for x in sys.argv[2:6]]; sc=float(sys.argv[6]) if len(sys.argv)>6 else 0.75
w,h=int(854*sc),int(480*sc)
S=Image.new('RGB',(2*w,2*(h+16)),(30,30,30)); d=ImageDraw.Draw(S)
for k,t in enumerate(ts):
    f=int(round(t*30)); im=Image.open(f'frames/f_{f+1:05d}.jpg').resize((w,h),Image.LANCZOS)
    x,y=(k%2)*w,(k//2)*(h+16); S.paste(im,(x,y+16)); d.text((x+4,y+2),f"src {t:.3f}s f{f}",fill='yellow')
S.save(out,quality=90)
