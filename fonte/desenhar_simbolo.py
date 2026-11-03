import math
from pathlib import Path
N=64
g=[['.']*N for _ in range(N)]
def put(x,y,c):
    if 0<=x<N and 0<=y<N: g[y][x]=c
def tom(v):  # v 0..1 -> '1'..'6' em faixas
    return str(1+min(5,max(0,int(v*6))))
# ---- lua: centro e raio externos, recorte interno
cx,cy,r=27.0,17.0,13.2; ix,iy,ir=33.0,13.8,11.0
L=(-0.62,-0.78)
lua=set()
for y in range(N):
    for x in range(N):
        px,py=x+.5,y+.5
        if math.hypot(px-cx,py-cy)<=r and math.hypot(px-ix,py-iy)>ir: lua.add((x,y))
for (x,y) in lua:
    px,py=x+.5,y+.5
    nx,ny=(px-cx)/r,(py-cy)/r
    lam=nx*L[0]+ny*L[1]            # -1..1
    din=(math.hypot(px-ix,py-iy)-ir)  # distancia da borda interna
    v=0.5+0.45*lam - (0.18 if din<1.6 else 0)
    put(x,y,tom(v))
# selout da lua: borda externa escura no lado da sombra
for (x,y) in lua:
    viz=[(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    if any(p not in lua for p in viz):
        nx,ny=(x+.5-cx)/r,(y+.5-cy)/r
        lam=nx*L[0]+ny*L[1]
        borda_ext=math.hypot(x+.5-cx,y+.5-cy)>r-1.3
        if borda_ext and lam<0.1: put(x,y,'2' if lam>-0.5 else '1')
        elif not borda_ext: put(x,y,'2' if lam<0.3 else '3')
# ---- cristal: hexagono alongado com facetas
C=33; top,sh,lo,bot,hw=33,38,49,59,6.5
cri={}
for y in range(N):
    for x in range(N):
        px,py=x+.5,y+.5
        if py<top or py>bot: continue
        w=hw*(py-top)/(sh-top) if py<sh else hw if py<=lo else hw*(bot-py)/(bot-lo)
        if abs(px-C)<=w: cri[(x,y)]=None
for (x,y) in cri:
    px,py=x+.5,y+.5; dx=px-C
    if py<sh:   # faceta de cima
        t='6' if dx<0 else '4'
    elif py>lo: # faceta de baixo
        t='4' if dx<0 else '2'
    else:
        t='5' if dx<-3.5 else '6' if dx<0 else '4' if dx<3.5 else '3'
    cri[(x,y)]=t
for (x,y),t in cri.items():
    out=any(p not in cri for p in((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    if out: t='1' if x>=C+2 or y>=bot-3 else '3' if x>=C else '4'
    put(x,y,t)
# ---- orbita em arcos abertos, 2 px na frente
def orb(front_pass):
    for k in range(3000):
        a=2*math.pi*k/3000
        deg=math.degrees(a)%360
        if 70<deg<110: continue          # abertura embaixo do cristal? (frente meio)
        if 250<deg<290: continue         # atras do cristal
        ex,ey=27*math.cos(a),5.2*math.sin(a); rot=math.radians(-8)
        x=C+ex*math.cos(rot)-ey*math.sin(rot); y=46+ex*math.sin(rot)+ey*math.cos(rot)
        front=math.sin(a)>0
        if front!=front_pass: continue
        p=(int(x),int(y))
        if not front and p in cri: continue
        lado=math.cos(a)
        if front: t='5' if lado<-0.3 else '4' if lado<0.4 else '3'
        else: t='2' if lado<0 else '3'
        put(*p,t)
        if front: put(p[0],p[1]+1,'2' if lado>0.2 else '3')
orb(False); orb(True)
# ---- estrelas
def estrela(x,y,braco):
    put(x,y,'6')
    for k in range(1,braco+1):
        t='5' if k==1 else '4' if k<braco else '3'
        for dx,dy in((k,0),(-k,0),(0,k),(0,-k)): put(x+dx,y+dy,t)
    if braco>=3:
        for dx,dy in((1,1),(-1,1),(1,-1),(-1,-1)): put(x+dx,y+dy,'3')
estrela(50,8,4); estrela(8,30,3); estrela(54,30,1)
for x,y,t in((47,18,'4'),(42,25,'3'),(13,10,'3'),(57,50,'4'),(20,59,'3'),(5,57,"3")): put(x,y,t)
saida = Path(__file__).resolve().parent / "simbolo.txt"
saida.write_text("\n".join("".join(linha) for linha in g) + "\n", encoding="utf-8")
