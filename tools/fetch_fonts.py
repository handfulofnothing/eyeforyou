import re, urllib.request, base64, json
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
url=("https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,400;0,500;0,600;0,700;1,700;1,800"
     "&family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,700&family=Archivo:wdth,wght@125,800;125,900&display=block")
css=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA})).read().decode()
blocks=re.findall(r'/\*\s*([\w-]+)\s*\*/\s*@font-face\s*{([^}]*)}',css)
out=[]
for subset,b in blocks:
    if subset!='latin': continue
    fam=re.search(r"font-family:\s*'([^']+)'",b).group(1)
    sty=re.search(r"font-style:\s*(\w+)",b).group(1)
    wt=re.search(r"font-weight:\s*(\d+)",b).group(1)
    st=re.search(r"font-stretch:\s*([\d%]+)",b)
    src=re.search(r"url\((https://[^)]+)\)",b).group(1)
    data=urllib.request.urlopen(src).read()
    face=f"@font-face{{font-family:'{fam}';font-style:{sty};font-weight:{wt};{('font-stretch:'+st.group(1)+';') if st else ''}src:url(data:font/woff2;base64,{base64.b64encode(data).decode()}) format('woff2');}}"
    out.append(face); print(fam,sty,wt,st.group(1) if st else '',len(data))
open('src/fonts.css','w').write('\n'.join(out))
