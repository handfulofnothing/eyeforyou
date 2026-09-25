import numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
flux=np.load("kflux.npy"); ob=np.load("bflux.npy"); n=min(len(flux),len(ob)); flux=flux[:n]; ob=ob[:n]; fr=44100/64
g=json.load(open('grid_fit.json')); per=60/g['bpm']; ph=g['phase']
tt=np.arange(len(flux))/fr
wins=[(12,18),(18,24),(24,30),(30,36),(36,42),(42,48),(48,54),(54,60),(60,66),(66,72),(72,78),(78,84.8)]
fig,axes=plt.subplots(len(wins),1,figsize=(24,30))
for ax,(a,b) in zip(axes,wins):
    m=(tt>=a)&(tt<b)
    ax.plot(tt[m],flux[m],lw=0.8,label='kick band')
    ax.plot(tt[m],ob[m]*0.6-0.65,lw=0.6,color='g',label='broadband')
    for k,t in enumerate(np.arange(ph,85,per)):
        if a<=t<b:
            ax.axvline(t,color='r' if round((t-ph)/per)%4==0 else 'orange',alpha=0.5,lw=0.8)
    ax.set_xlim(a,b); ax.set_xticks(np.arange(a,b,0.25),minor=True); ax.set_xticks(np.arange(int(a),b,1)); ax.grid(which='minor',alpha=0.2)
plt.tight_layout(); plt.savefig('gridplot.png',dpi=55)
