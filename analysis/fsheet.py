import sys
from PIL import Image, ImageDraw
t0,t1,step,cols,out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
w = int(sys.argv[6]) if len(sys.argv)>6 else 320
f0,f1=int(round(t0*30)),int(round(t1*30))
idx=list(range(f0,f1+1,step))
h=int(w*480/854)
rows=(len(idx)+cols-1)//cols
sheet=Image.new('RGB',(cols*w,rows*(h+14)),(40,40,40)); d=ImageDraw.Draw(sheet)
for k,f in enumerate(idx):
    im=Image.open(f'frames/f_{f+1:05d}.jpg').resize((w,h))
    x,y=(k%cols)*w,(k//cols)*(h+14)
    sheet.paste(im,(x,y+14)); d.text((x+3,y+1),f"f{f} {f/30:.3f}s",fill='yellow')
sheet.save(out,quality=88)
print(out,len(idx))
