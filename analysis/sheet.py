import sys, glob
from PIL import Image, ImageDraw
files = sorted(glob.glob('thumbs/t_*.jpg'))
cols, rows = 5, 4
W,H = Image.open(files[0]).size
per = cols*rows
for s in range(0, len(files), per):
    sheet = Image.new('RGB',(cols*W, rows*(H+18)),'black')
    d = ImageDraw.Draw(sheet)
    for k,f in enumerate(files[s:s+per]):
        idx = s+k
        t = idx*0.5 + 0.25  # fps=2 filter samples at mid
        im = Image.open(f)
        x,y = (k%cols)*W, (k//cols)*(H+18)
        sheet.paste(im,(x,y+18))
        d.text((x+4,y+2), f"{t:5.2f}s", fill='yellow')
    sheet.save(f'sheet_{s//per:02d}.jpg', quality=85)
print('done')
