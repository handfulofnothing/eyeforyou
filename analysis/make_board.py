import json, base64, io, html
from PIL import Image
ev=json.load(open('events_out.json'))
bars=json.load(open('bars.json'))['bars']
blocks=json.load(open('blocks.json'))
BLK={'I':('Intro pad','#9AA0AA'),'A':('Drop · into welcome','#B90002'),'H1':('Hub loop','#F15D08'),'S':('Special loop','#10EA37'),
     'R':('Showroom loop','#14DCFC'),'E':('Hub-return loop','#F5A679'),'F':('Info loop','#0D8495')}
BPM={'I':135.03,'A':135.03,'H1':134.96,'S':135.18,'R':135.63,'E':135.13,'F':135.10}
ANC={'I':None,'A':12.871,'H1':22.598,'S':28.942,'R':44.540,'E':56.271,'F':63.134}
RES={b['key']:b for b in blocks}
TXT={'A':'#ffffff','F':'#ffffff'}
def tx(k): return TXT.get(k,'#111111')
def thumb(t):
    f=int(round(t*30)); f=max(0,min(2543,f))
    im=Image.open(f'frames/f_{f+1:05d}.jpg').convert('RGB').resize((384,216),Image.LANCZOS)
    buf=io.BytesIO(); im.save(buf,'JPEG',quality=74,optimize=True)
    return 'data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()
esc=html.escape
def tc(t):
    m=int(t//60); s=t-60*m; return f"{m}:{s:06.3f}"
# ---------- timeline svg ----------
PX=26.0; L=70; W=int(84.867*PX)+L+30
yB=26; yN=50; yE0=64; hE=64; yO=150; yT=214; H=262
def X(t): return L+t*PX
s=[]
s.append(f'<svg class="tl" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Beat grid timeline with energy per bar and original versus snapped event times">')
# row labels
for y,lab in [(yB+11,'loop'),(yN+2,'bar'),(yE0+hE/2+4,'energy'),(yO+4,'source'),(yT+4,'rebuild')]:
    s.append(f'<text x="8" y="{y}" class="lab">{lab}</text>')
# blocks
for b in blocks:
    a=b['start'] if b['key']=='I' else b['anchor']; e=b['end']
    nxt=[x['anchor'] for x in blocks if x['key']!='I' and x['anchor']>a+0.1]
    e=min(nxt) if nxt else 84.867
    col=BLK[b['key']][1]
    s.append(f'<rect x="{X(a):.1f}" y="{yB}" width="{(e-a)*PX:.1f}" height="16" rx="2" fill="{col}" class="blk"><title>{esc(b["key"])} · {esc(BLK[b["key"]][0])} · {BPM[b["key"]]} BPM · starts {a:.3f}s</title></rect>')
    s.append(f'<text x="{X(a)+5:.1f}" y="{yB+12}" class="blkt" style="fill:{tx(b['key'])}">{b["key"]}</text>')
# beats + bars
for br in bars:
    t0=br['t']; ln=br['len']; beat=60/BPM[br['block']]
    k=1
    while k*beat<ln-1e-3:
        s.append(f'<line x1="{X(t0+k*beat):.1f}" x2="{X(t0+k*beat):.1f}" y1="{yE0}" y2="{yT+14}" class="bt"/>'); k+=1
    s.append(f'<line x1="{X(t0):.1f}" x2="{X(t0):.1f}" y1="{yN-10}" y2="{yT+14}" class="br{" drop" if br["bar"]==1 else ""}"/>')
    if br['bar']%2==1 or br['bar']<0: s.append(f'<text x="{X(t0)+2:.1f}" y="{yN}" class="bn">{br["bar"]}</text>')
    # energy
    db=br['db']; h=max(2,(db+26)/18*hE)
    s.append(f'<rect x="{X(t0)+1:.1f}" y="{yE0+hE-h:.1f}" width="{max(1,ln*PX-2):.1f}" height="{h:.1f}" class="en" fill="{BLK[br["block"]][1]}"><title>bar {br["bar"]}: {db} dBFS RMS · low band {br["low_db"]} dB</title></rect>')
# drop label
s.append(f'<text x="{X(12.871)+4:.1f}" y="{yE0-4}" class="droplab">THE DROP · bar 1 · 12.871 s</text>')
# events
for e in ev:
    xo=X(e['t']); xt=X(e['target']); big=abs(e['delta_ms'])>=250
    s.append(f'<line x1="{xo:.1f}" y1="{yO+6}" x2="{xt:.1f}" y2="{yT-8}" class="cn{" big" if big else ""}"/>')
    s.append(f'<circle cx="{xo:.1f}" cy="{yO}" r="3" class="ev0"/>')
    cls={'CUT':'mc','HIT':'mh','MOVE':'mm','STAG':'ms'}[e['type']]
    if e['type']=='CUT':
        s.append(f'<rect x="{xt-3:.1f}" y="{yT-10}" width="6" height="22" class="{cls}"><title>{e["id"]} CUT → {e["target"]:.3f}s (bar {e["bar"]}.{e["beat"]}{e["sub"]})</title></rect>')
    else:
        if e['type'] in ('MOVE','STAG') and e.get('dur'):
            s.append(f'<rect x="{xt:.1f}" y="{yT+4}" width="{e["dur"]*PX:.1f}" height="4" rx="2" class="span"/>')
        s.append(f'<circle cx="{xt:.1f}" cy="{yT}" r="4.2" class="{cls}"><title>{e["id"]} {e["type"]} → {e["target"]:.3f}s (bar {e["bar"]}.{e["beat"]}{e["sub"]})</title></circle>')
# time axis
for sec in range(0,85,5):
    s.append(f'<text x="{X(sec):.1f}" y="{H-6}" class="ax">{sec}s</text>')
s.append('</svg>')
svg='\n'.join(s)
# ---------- cards ----------
scenes=[]
for e in ev:
    if not scenes or scenes[-1]['name']!=e['scene']: scenes.append({'name':e['scene'],'ev':[]})
    scenes[-1]['ev'].append(e)
def chip(t): return f'<span class="chip c-{t.lower()}">{ {"CUT":"Cut","HIT":"Hit","MOVE":"Move","STAG":"Ripple"}[t] }</span>'
cards=[]
for sc in scenes:
    evs=sc['ev']; b0=evs[0]['bar']; b1=evs[-1]['bar']; blks=[]
    for e in evs:
        if e['block'] not in blks: blks.append(e['block'])
    tags=''.join(f'<span class="btag" style="--c:{BLK[k][1]};color:{tx(k)}">{k}</span>' for k in blks)
    cards.append(f'<section class="scene" data-scene><header class="sh"><h3>{esc(sc["name"])}</h3><div class="sm">{tags}<span class="mono">bars {b0}–{b1} · {evs[0]["target"]:.2f}–{evs[-1]["target"]:.2f}s</span></div></header><div class="cards">')
    for e in evs:
        big=abs(e['delta_ms'])>=250
        dur=f' · lasts {e["dur"]:.2f}s' if e.get('dur') else ''
        d=e['delta_ms']; dcls='d-big' if big else ('d-zero' if abs(d)<20 else '')
        cards.append(f'''<article class="card{' retimed' if big else ''}" data-type="{e['type']}" data-big="{int(big)}">
<img loading="lazy" src="{thumb(e['thumb'])}" alt="Source frame at {e['thumb']:.2f}s for {e['id']}" width="384" height="216">
<div class="cb"><div class="row1"><span class="id mono">{e['id']}</span>{chip(e['type'])}<span class="pos mono">{e['bar']}.{e['beat']}{e['sub'] if e['sub'] in ('','.&') else ''}</span></div>
<p class="what">{esc(e['what'])}</p>
<div class="times mono"><span class="src">{e['t']:.3f}</span><span class="arr" aria-hidden="true">→</span><span class="tgt">{e['target']:.3f}s</span><span class="delta {dcls}">{'+' if d>0 else ''}{d} ms</span></div>
<div class="meta mono">60fps frame {e['frame60']}{dur}</div></div></article>''')
    cards.append('</div></section>')
cards='\n'.join(cards)
# ---------- retime review ----------
rv=[e for e in ev if abs(e['delta_ms'])>=250]
rvrows=''.join(f'<tr><td class="mono">{e["id"]}</td><td>{esc(e["what"][:90])}</td><td class="mono num">{e["t"]:.3f}</td><td class="mono num">{e["target"]:.3f}</td><td class="mono num d-big">{"+" if e["delta_ms"]>0 else ""}{e["delta_ms"]}</td><td class="mono">{e["bar"]}.{e["beat"]}</td></tr>' for e in rv)
# ---------- grid table ----------
brows=''.join(f'<tr><td class="mono num">{b["bar"]}</td><td><span class="btag" style="--c:{BLK[b["block"]][1]};color:{tx(b["block"])}">{b["block"]}</span></td><td class="mono num">{b["t"]:.3f}</td><td class="mono num">{int(round(b["t"]*60))}</td><td class="mono num">{b["len"]:.3f}</td><td class="mono num">{b["db"]:.1f}</td><td class="mono num">{b["low_db"]:.1f}</td></tr>' for b in bars)
blk_rows=''.join(f'<tr><td><span class="btag" style="--c:{BLK[b["key"]][1]};color:{tx(b["key"])}">{b["key"]}</span></td><td>{esc(BLK[b["key"]][0])}</td><td class="mono num">{("0.000" if b["key"]=="I" else f"{b['anchor']:.3f}")}</td><td class="mono num">{BPM[b["key"]]:.2f}</td><td class="mono num">{b["on_grid"]}/{b["hits"]}</td><td class="mono num">{"—" if b["key"]=="I" else f"{b['med_res_ms']:.1f}"}</td></tr>' for b in blocks)
n_cut=sum(e['type']=='CUT' for e in ev); n_hit=sum(e['type']=='HIT' for e in ev)
tpl=open('board_tpl.html').read()
out=(tpl.replace('%%SVG%%',svg).replace('%%CARDS%%',cards).replace('%%RVROWS%%',rvrows).replace('%%BARROWS%%',brows)
       .replace('%%BLKROWS%%',blk_rows).replace('%%NEV%%',str(len(ev))).replace('%%NRV%%',str(len(rv))).replace('%%NCUT%%',str(n_cut)).replace('%%NHIT%%',str(n_hit)))
p='/private/tmp/claude-501/-Users-marcelojansson-eye4u/b16b63e2-e45c-4726-b156-123955828f64/scratchpad/storyboard.html'
open(p,'w').write(out)
import os; print(p, os.path.getsize(p)//1024,'KB', 'events',len(ev),'retimed',len(rv))
