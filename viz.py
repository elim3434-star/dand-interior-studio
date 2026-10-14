"""예시 도면(2D)과 3D 모델 SVG 생성. 실제 현장 도면이 아니라 '예시'입니다."""
import math
W,D=20,8   # 예시 상가 20m x 8m (약 48평)

def plan2d():
    s=44; mx=64; my=52
    X=lambda x: mx+x*s
    Y=lambda y: my+y*s
    o=[]
    L='rgba(255,255,255,.9)'; Y1='#ffd23f'
    o.append(f'<rect x="{X(0)}" y="{Y(0)}" width="{W*s}" height="{D*s}" fill="rgba(255,255,255,.04)"/>')
    # grid
    for k in range(1,W): o.append(f'<line x1="{X(k)}" y1="{Y(0)}" x2="{X(k)}" y2="{Y(D)}" stroke="rgba(255,255,255,.07)"/>')
    for k in range(1,D): o.append(f'<line x1="{X(0)}" y1="{Y(k)}" x2="{X(W)}" y2="{Y(k)}" stroke="rgba(255,255,255,.07)"/>')
    def wall(x0,y0,x1,y1): o.append(f'<rect x="{X(x0):.1f}" y="{Y(y0):.1f}" width="{(x1-x0)*s:.1f}" height="{(y1-y0)*s:.1f}" fill="rgba(255,255,255,.88)"/>')
    t=.3
    wall(0,0,W,t); wall(0,D-t,5,D); wall(7.5,D-t,W,D); wall(0,0,t,D); wall(W-t,0,W,D)     # 외벽 (입구 5~7.5m 개방)
    wall(13,0,13+t,3.2); wall(13,4.3,13+t,D-t)               # 주방/홀 사이 (출입구 3.2~4.3)
    wall(13,4.3,15,4.3+t); wall(16,4.3,18,4.3+t); wall(19,4.3,W,4.3+t)  # 주방 아래벽 (문 2곳)
    wall(17,4.3,17+t,D-t)                                    # 창고/화장실 칸막이
    # door arcs
    def arc(cx,cy,r,a0,a1,hinge):
        x0=cx+r*math.cos(math.radians(a0)); y0=cy+r*math.sin(math.radians(a0))
        x1=cx+r*math.cos(math.radians(a1)); y1=cy+r*math.sin(math.radians(a1))
        o.append(f'<path d="M{X(cx):.1f},{Y(cy):.1f} L{X(x0):.1f},{Y(y0):.1f} A{r*s:.1f},{r*s:.1f} 0 0 1 {X(x1):.1f},{Y(y1):.1f} Z" fill="rgba(255,210,63,.10)" stroke="{Y1}" stroke-width=".8"/>')
    o.append(f'<line x1="{X(5):.1f}" y1="{Y(D-t/2):.1f}" x2="{X(7.5):.1f}" y2="{Y(D-t/2):.1f}" stroke="{Y1}" stroke-width="2" stroke-dasharray="5 4"/>')
    arc(15,4.6,1.0,0,90,0)           # 창고 문
    arc(18,4.6,1.0,0,90,0)           # 화장실 문
    arc(13.15,3.2,1.1,-90,0,0)       # 주방 출입구
    # 홀 테이블
    for i in range(4):
        for j in range(2):
            x=2+i*2.6; y=1.6+j*3.6
            o.append(f'<rect x="{X(x):.1f}" y="{Y(y):.1f}" width="{1.4*s}" height="{1.4*s}" rx="3" fill="rgba(255,255,255,.12)" stroke="{L}" stroke-width="1"/>')
            for cx,cy in ((x+.7,y-.3),(x+.7,y+1.7)):
                o.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="{.25*s:.1f}" fill="none" stroke="rgba(255,255,255,.55)"/>')
    # 주방 설비
    o.append(f'<rect x="{X(14)}" y="{Y(.5)}" width="{5.5*s}" height="{1.1*s}" fill="rgba(255,255,255,.14)" stroke="{L}"/>')
    o.append(f'<rect x="{X(14)}" y="{Y(3)}" width="{4*s}" height="{.5*s}" fill="rgba(255,255,255,.14)" stroke="{L}"/>')
    # 라벨
    def lab(x,y,txt,sz=15,col='#fff',w=600): o.append(f'<text x="{X(x):.1f}" y="{Y(y):.1f}" fill="{col}" font-family="Noto Sans KR,sans-serif" font-size="{sz}" font-weight="{w}" text-anchor="middle">{txt}</text>')
    lab(6.5,4.15,'손님 홀 · 8테이블',14,'rgba(255,255,255,.85)',500)
    lab(16.4,2.7,'주방',15); lab(15,6.3,'창고',14); lab(18.5,6.3,'화장실',14)
    lab(6.25,D+.42,'출입구',12,Y1,600)
    # 치수선
    def dim(x0,y0,x1,y1,txt,off=(0,0),rot=False):
        o.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" stroke="{Y1}" stroke-width="1.1"/>')
        for px,py in ((x0,y0),(x1,y1)):
            o.append(f'<line x1="{X(px)-5:.1f}" y1="{Y(py)+5:.1f}" x2="{X(px)+5:.1f}" y2="{Y(py)-5:.1f}" stroke="{Y1}" stroke-width="1.4"/>')
        mxp=(X(x0)+X(x1))/2+off[0]; myp=(Y(y0)+Y(y1))/2+off[1]
        tr=f' transform="rotate(-90 {mxp:.1f} {myp:.1f})"' if rot else ''
        o.append(f'<text x="{mxp:.1f}" y="{myp:.1f}" fill="{Y1}" font-family="IBM Plex Mono,monospace" font-size="12" text-anchor="middle"{tr}>{txt}</text>')
    dim(0,-.55,W,-.55,'20,000',(0,-8)); dim(-.7,0,-.7,D,'8,000',(-8,0),True)
    dim(13,D+.55,W,D+.55,'7,000',(0,18)); dim(0,D+.55,13,D+.55,'13,000',(0,18))
    w=mx*2+W*s; h=my+D*s+70
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="상가 평면도 예시: 홀, 주방, 창고, 화장실과 치수">'+''.join(o)+'</svg>'

def iso3d():
    s=24.0; ox=D*0.866*s+30; oy=110
    def P(x,y,z): return ((x-y)*0.866*s+ox,(x+y)*0.5*s-z*s+oy)
    def pts(l): return ' '.join(f'{P(*p)[0]:.1f},{P(*p)[1]:.1f}' for p in l)
    items=[]
    def prism(x0,y0,x1,y1,h,k='wall'): items.append((x0+x1+y0+y1,x0,y0,x1,y1,h,k))
    def wx(x,y0,y1,h,t=.3):
        y=y0
        while y<y1-1e-6: e=min(y+1.5,y1); prism(x,y,x+t,e,h); y=e
    def wy(y,x0,x1,h,t=.3):
        x=x0
        while x<x1-1e-6: e=min(x+1.5,x1); prism(x,y,e,y+t,h); x=e
    Hh=2.3
    wy(0,0,W,Hh); wx(0,0,D,Hh); wy(D-.3,0,5,.18); wy(D-.3,7.5,W,.18); wx(W-.3,0,D,.18)
    PH=1.1; wx(13,0,3.2,PH); wx(13,4.3,D-.3,PH); wy(4.3,13,15,PH); wy(4.3,16,18,PH); wy(4.3,19,W,PH); wx(17,4.3,D-.3,PH)
    for i in range(4):
        for j in range(2): prism(2+i*2.6,1.6+j*3.6,3.4+i*2.6,3+j*3.6,.7,'t')
    prism(14,.5,19.5,1.6,.95,'c'); prism(14,3,18,3.5,.5,'c')
    items.sort(); o=[]
    o.append(f'<polygon points="{pts([(0,0,0),(W,0,0),(W,D,0),(0,D,0)])}" fill="rgba(255,255,255,.07)" stroke="rgba(255,255,255,.5)"/>')
    for it in items:
        _,x0,y0,x1,y1,h,k=it; top=.34 if k!='wall' else .28
        o.append(f'<polygon points="{pts([(x0,y1,0),(x1,y1,0),(x1,y1,h),(x0,y1,h)])}" fill="rgba(255,255,255,.10)" stroke="rgba(255,255,255,.75)" stroke-width=".9" stroke-linejoin="round"/>')
        o.append(f'<polygon points="{pts([(x1,y0,0),(x1,y1,0),(x1,y1,h),(x1,y0,h)])}" fill="rgba(255,255,255,.05)" stroke="rgba(255,255,255,.75)" stroke-width=".9" stroke-linejoin="round"/>')
        o.append(f'<polygon points="{pts([(x0,y0,h),(x1,y0,h),(x1,y1,h),(x0,y1,h)])}" fill="rgba(255,255,255,{top})" stroke="rgba(255,255,255,.9)" stroke-width=".9" stroke-linejoin="round"/>')
    def tx(x,y,z,t,c='#ffd23f'):
        a=P(x,y,z); return f'<text x="{a[0]:.1f}" y="{a[1]:.1f}" fill="{c}" font-family="Noto Sans KR,sans-serif" font-size="13" font-weight="600" text-anchor="middle">{t}</text>'
    o.append(tx(6.5,4.1,0,'홀')); o.append(tx(16.5,2.3,0,'주방')); o.append(tx(15,6.3,0,'창고')); o.append(tx(18.5,6.3,0,'화장실'))
    w=(W+D)*0.866*s+60; h=(W+D)*0.5*s+oy+30
    return f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="상가 3D 모델 예시">'+''.join(o)+'</svg>'
