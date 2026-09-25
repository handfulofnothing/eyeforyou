import cv2, numpy as np, json
cap = cv2.VideoCapture('source.mp4')
prev=None; diffs=[]; hists=[]; means=[]
i=0
while True:
    ok, f = cap.read()
    if not ok: break
    small = cv2.resize(f,(160,90))
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv],[0,1,2],None,[8,4,4],[0,180,0,256,0,256]); h=cv2.normalize(h,h).flatten()
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)
    means.append(float(g.mean()))
    if prev is not None:
        pd = float(np.abs(g-prev[0]).mean())
        hd = float(cv2.compareHist(h,prev[1],cv2.HISTCMP_BHATTACHARYYA))
        diffs.append((i,pd,hd))
    prev=(g,h); i+=1
print('frames',i)
d=np.array(diffs)
json.dump({'diffs':diffs,'means':means},open('scene_raw.json','w'))
# candidate cuts
pd=d[:,1]; hd=d[:,2]
med = np.median(pd)
for (fi,p,h) in diffs:
    if (p>max(18,4*med) and h>0.25) or h>0.45 or p>35:
        print(f"{fi:5d}  t={fi/30:6.3f}  pix={p:6.1f}  hist={h:.3f}")
print('median pix diff', med)
