import re
import json
#!/usr/bin/env python3
"""content/*.json 을 읽어 모든 HTML 페이지를 생성합니다. (관리자 페이지에서 저장하면 자동 실행됨)"""
import os, json, html, sys
from urllib.parse import urlsplit
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import viz
ROOT = os.path.dirname(os.path.abspath(__file__))
def load(n): return json.load(open(os.path.join(ROOT,'content',n),encoding='utf-8'))
S=load('site.json'); H=load('home.json'); A=load('about.json'); P=load('portfolio.json'); C=load('contact.json')
CASES=load('cases.json')['items']; CP=load('concepts.json'); PROJECTS=CP['items'] if CP.get('enabled',True) else []; PG=CP['page']
BYSLUG={p['slug']:p for p in PROJECTS}
TEL=S['tel']; TELH=''.join(ch for ch in TEL if ch.isdigit()); MAIL=S['mail']; ADDR=S['addr']; INSTA=S['insta']; BLOG=S['blog']

def e(s): return html.escape(str(s),quote=True)
def t(s): return e(s).replace('\n','<br>')
def num(x):
    try: return float(x)
    except: return 0

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2312100e'/%3E%3Ctext x='32' y='43' font-size='34' text-anchor='middle' fill='%23fff' font-family='Georgia,serif'%3ED%26%3C/text%3E%3C/svg%3E"

def site_origin():
    value=str(S.get('site_url','')).strip().rstrip('/')
    parsed=urlsplit(value)
    return value if parsed.scheme=='https' and parsed.netloc and not parsed.path else ''

def seo_extras(path, title, desc):
    url=site_origin()
    if not url: return ''
    canonical=url+'/'+path
    og=url+'/'+S['og_image'].lstrip('/')
    return f'''
  <link rel="canonical" href="{e(canonical)}">
  <meta property="og:url" content="{e(canonical)}">
  <meta property="og:image" content="{e(og)}">
'''

def meta_extra():
    out=''
    v=str(S.get('meta_domain_verification','')).strip()
    if v: out+=f'\n  <meta name="facebook-domain-verification" content="{e(v)}">'
    nv=str(S.get('naver_site_verification','')).strip()
    if nv: out+=f'\n  <meta name="naver-site-verification" content="{e(nv)}">'
    pid=re.sub(r'\D','',str(S.get('meta_pixel_id','')))
    if pid:
        out+=("\n  <script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','"+pid+"');fbq('track','PageView');</script>"
              "\n  <noscript><img height=\"1\" width=\"1\" style=\"display:none\" src=\"https://www.facebook.com/tr?id="+pid+"&ev=PageView&noscript=1\" alt=\"\"></noscript>")
    return out

def head(title, desc, depth=0, cls='', path='index.html', keywords=''):
    p='../'*depth
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">{('<meta name="keywords" content="'+e(keywords)+'">') if keywords else ''}
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:image" content="{p}{e(S['og_image'])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">{seo_extras(path, title, desc)}
  <meta name="theme-color" content="#12100e">
  <link rel="icon" type="image/png" href="{p}assets/images/favicon.png">
{meta_extra()}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Noto+Sans+KR:wght@300;400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}assets/styles.css">
</head>
<body{cls}>
'''

def topbar(depth=0, active=''):
    p='../'*depth
    def a(href,label,key):
        c=' class="active"' if key==active else ''
        return f'<a href="{p}{href}"{c}>{label}</a>'
    return f'''<a class="skip-link" href="#main">본문 바로가기</a>
<header class="topbar{' dark' if depth or active in ('about','portfolio','contact') else ''}" id="topbar">
  <div class="wrap nav">
    <a href="{p}index.html" class="brand" aria-label="{e(S['brand'])} 홈"><div class="brand-mark"><img src="{p}assets/images/logo-mark-white.png" alt="" width="44" height="42"></div><div class="brand-text"><strong>{e(S['brand'])}</strong><span>{e(S['brand_sub'])}</span></div></a>
    <nav class="nav-links" id="mobileNav" aria-label="사이트 메뉴">
      {a('index.html','Home','home')}{a('about.html','소개','about')}{a('portfolio.html','시공 사례','portfolio')}{a('contact.html','견적 문의','contact')}
    </nav>
    <div class="nav-cta"><a class="btn-cta" href="{p}contact.html#calc">무료 견적/상담 문의</a><button class="menu-btn" id="menuBtn" type="button" aria-controls="mobileNav">Menu</button></div>
  </div>
</header>
'''

def biz_line():
    if not S.get('biz_regno'): return ''
    return f'<br>상호 {e(S["biz_name"])} · 대표 {e(S["biz_rep"])} · 사업자등록번호 {e(S["biz_regno"])}'

def footer(depth=0):
    p='../'*depth
    return f'''<footer class="footer"><div class="wrap footer-row">
  <div><strong>{e(S['brand'])}</strong> · {e(S['footer_line'])}<br>{e(ADDR)} · {e(TEL)} · {e(MAIL)}{biz_line()}</div>
  <div><a href="{e(INSTA)}" target="_blank" rel="noopener">Instagram</a> · <a href="{e(BLOG)}" target="_blank" rel="noopener">Blog</a>{(' · <a href="'+e(S['youtube'])+'" target="_blank" rel="noopener">YouTube</a>') if S.get('youtube') else ''}{(' · <a href="'+e(S['pinterest'])+'" target="_blank" rel="noopener">Pinterest</a>') if S.get('pinterest') else ''}<br>{e(S['footer_note'])} · <a href="{p}privacy.html">개인정보처리방침</a></div>
</div></footer>
<div class="floating-cta"><a href="{p}contact.html#quoteForm">{e(S['float_quote'])}</a><a class="alt" href="tel:{TELH}">{e(S['float_tel'])}</a></div>
<script>window.DAND_TEL="{TELH}";window.DAND_MAIL="{e(MAIL)}";</script>
<script src="{p}assets/js/main.js"></script>
</body></html>
'''

def concept_card(p, depth=0, span='span-4 mid'):
    pre='../'*depth
    return f'''<a class="portfolio-card {span}" href="{pre}projects/{e(p['slug'])}.html" data-filterable data-category="{e(p['cat'])}" data-style="{e(p.get('style_filter',''))}" data-size="{e(p.get('size_filter',''))}"><img src="{pre}{e(p['img'])}" alt="{e(p['title'])} 디자인 컨셉" loading="lazy"><div class="portfolio-overlay"><span class="tag">{e(p['tag'])} · {e(PG['badge_suffix'])}</span><h3 class="serif">{e(p['title'])}</h3><p>{e(p['ko'])} — {e(p['desc'])}</p></div></a>'''

def real_cards(depth=0, limit=None, cat=None):
    pre='../'*depth
    out=''
    shown=[r for r in CASES if os.path.exists(os.path.join(ROOT,r.get('img','x'))) and (cat is None or r.get('cat','commercial')==cat)]
    for r in (shown[:limit] if limit else shown):
        if r.get('slug') and r.get('gallery'): link=f'<a class="btn secondary" href="{pre}cases/{e(r["slug"])}.html">{e(r["link_text"])}</a>'
        else: link=f'<a class="btn secondary" href="{e(r["link"])}" target="_blank" rel="noopener">{e(r["link_text"])}</a>' if r.get('link') else ''
        out+=f'''<article class="real-card" data-filterable data-category="{e(r.get('cat','commercial'))}" data-style="{e(r.get('style_filter',''))}" data-size="{e(r.get('size_filter',''))}"><div class="real-ph"><span class="real-place serif">{e(r['place'])}</span><img src="{pre}{e(r['img'])}" alt="{e(r['title'])} 시공 사진" loading="lazy" onerror="this.remove()"></div><div class="real-body"><span class="badge-solid">{e(r['badge'])}</span><h3>{e(r['title'])}</h3><p>{e(r['desc'])}</p>{link}</div></article>'''
    return out

def cat_blocks():
    out=''
    for cat,name,sub in (('residential','주거 공간','아파트 · 빌라 · 주택'),('commercial','상업 공간','식당 · 카페 · 학원 · 매장'),('facility','시설 · 외부 공사','학교 시설 · 외부 데크 · 난간')):
        cards=real_cards(0,None,cat)
        if not cards: continue
        n=cards.count('<article ')
        out+=f'<div class="cat-block" data-cat-block><div class="cat-head"><h3>{name}</h3><span>{sub} · {n}건</span></div><div class="real-grid">{cards}</div></div>'
    return out

def social_icons():
    ig='<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>'
    bl='<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><rect x="2" y="2" width="20" height="20" rx="5" fill="currentColor"/><path d="M7.6 6.8h4.5c2.3 0 3.6 1.1 3.6 2.9 0 1.1-.6 1.9-1.5 2.3 1.2.3 2 1.2 2 2.6 0 2-1.5 3.1-3.9 3.1H7.6z M10 8.7v2.3h1.6c.8 0 1.3-.4 1.3-1.1s-.5-1.2-1.3-1.2z M10 12.7v2.5h1.9c.9 0 1.4-.5 1.4-1.2s-.5-1.3-1.4-1.3z" fill="#fff" fill-rule="evenodd"/></svg>'
    return f'<span class="social-ic"><a href="{e(BLOG)}" target="_blank" rel="noopener" aria-label="네이버 블로그 바로가기" title="블로그">{bl}</a><a href="{e(INSTA)}" target="_blank" rel="noopener" aria-label="인스타그램 바로가기" title="인스타그램">{ig}</a></span>'

def sec_head(d, lg=True, extra=''):
    cls='title-lg' if lg else 'title-xl'
    return f'<div class="section-head"><div><span class="eyebrow">{e(d["eyebrow"])}</span><h2 class="{cls}">{t(d["title"])}</h2></div><div class="sh-right"><p>{t(d["desc"])}</p>{extra}</div></div>'

def page_hero(d, crumb, depth=0):
    return f'''<section class="page-hero"><div class="page-hero-media"><img src="{e(d['img'])}" alt="D& 인테리어 시공 현장"></div><div class="wrap hero-content"><div class="breadcrumb"><a href="index.html">Home</a><span class="sep">/</span><span>{e(crumb)}</span></div><span class="eyebrow">{e(d['eyebrow'])}</span><h1 class="display" style="max-width:9em">{t(d['title'])}</h1><p style="max-width:42em;color:rgba(255,255,255,.78);margin:0">{t(d['text'])}</p></div></section>'''

def flow_html():
    fl=H['process'].get('flow') or []
    if not fl: return ''
    return '<ol class="flow" aria-label="진행 흐름">'+''.join(f'<li><span class="fn">{i+1}</span><span class="ft">{e(x)}</span></li>' for i,x in enumerate(fl))+'</ol>'

def testimonials_html():
    T=H.get('testimonials') or {}
    its=[x for x in T.get('items',[]) if x.get('quote')]
    links=[x for x in S.get('review_links',[]) if x.get('url')]
    if not its and not links: return ''
    cards=''.join(f'<figure class="tcard"><blockquote>“{t(x["quote"])}”</blockquote><figcaption><strong>{e(x.get("who",""))}</strong>{(" · "+e(x["project"])) if x.get("project") else ""}</figcaption></figure>' for x in its)
    lk=('<p class="review-links">'+''.join(f'<a class="btn secondary" href="{e(x["url"])}" target="_blank" rel="noopener">{e(x.get("label","후기 보기"))} ↗</a>' for x in links)+'</p>') if links else ''
    return f'<section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(T)}{('<div class="tgrid">'+cards+'</div>') if its else ''}{lk}</div></section>'

def materials_html():
    M=H.get('materials') or {}
    its=[x for x in M.get('items',[]) if x.get('name')]
    if not its: return ''
    cards=''.join(f'<article class="mcard">{("<img src=\""+e(x["img"])+"\" alt=\""+e(x["name"])+"\" loading=\"lazy\">") if x.get("img") else ""}<div><strong>{e(x["name"])}</strong><p>{t(x.get("spec",""))}</p></div></article>' for x in its)
    return f'<section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(M)}<div class="mgrid">{cards}</div></div></section>'

def share_bar(title, img, depth=1):
    pre='../'*depth
    return f'''<div class="share-bar" data-share data-title="{e(title)}" data-img="{pre}{e(img)}"><span class="share-label">저장·공유</span><button type="button" class="share-btn" data-act="pin">Pinterest에 저장</button><button type="button" class="share-btn" data-act="share">인스타·카톡 공유</button><button type="button" class="share-btn" data-act="copy">링크 복사</button></div>'''

def ba_html(r):
    its=[x for x in r.get('before_after',[]) if x.get('before') and x.get('after')]
    if not its: return ''
    out=''.join(f'<figure class="ba" data-ba><div class="ba-stage"><img class="ba-after" src="../{e(x["after"])}" alt="{e(r["title"])} 시공 후" loading="lazy"><div class="ba-before-wrap"><img class="ba-before" src="../{e(x["before"])}" alt="{e(r["title"])} 시공 전" loading="lazy"></div><span class="ba-tag b">Before</span><span class="ba-tag a">After</span><div class="ba-handle" role="slider" aria-label="시공 전후 비교" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50" tabindex="0"><i></i></div></div>{("<figcaption>"+e(x["caption"])+"</figcaption>") if x.get("caption") else ""}</figure>' for x in its)
    return f'<section class="cs-group" id="ba"><div class="cs-head"><span class="num">BA</span><h2 class="title-md">시공 전 · 후 비교</h2><p class="muted">가운데 선을 좌우로 움직여 비교해 보세요.</p></div><div class="ba-list">{out}</div></section>'

def extras_html(r):
    out=''
    vids=[x for x in r.get('videos',[]) if x.get('url')]
    posts=[x for x in r.get('blog_posts',[]) if x.get('url')]
    if vids or posts:
        links=''.join(f'<a class="btn secondary" href="{e(x["url"])}" target="_blank" rel="noopener">▶ {e(x.get("label","시공 영상 보기"))}</a>' for x in vids)+''.join(f'<a class="btn secondary" href="{e(x["url"])}" target="_blank" rel="noopener">{e(x.get("label","블로그에서 시공 과정 보기"))}</a>' for x in posts)
        out+=f'<section class="cs-group"><div class="cs-head"><span class="num">+</span><h2 class="title-md">시공 과정·현장 영상</h2></div><div class="inline-actions">{links}</div></section>'
    tm=r.get('testimonial') or {}
    if tm.get('quote'):
        out+=f'<section class="cs-group"><div class="cs-head"><span class="num">“</span><h2 class="title-md">고객 후기</h2></div><figure class="tcard"><blockquote>“{t(tm["quote"])}”</blockquote><figcaption><strong>{e(tm.get("who",""))}</strong></figcaption></figure></section>'
    return out

def build_index():
    h=H['hero']
    s=head(f"{S['brand']} | 안산 상가·아파트 인테리어", S['site_desc'],keywords=S.get('seo_keywords',''))+topbar(0,'home')
    stats=''.join(f'<article{" class=has-pop tabindex=0" if x.get("img") else ""}><strong>{e(x["t"])}</strong><span>{e(x["d"])}</span>'+(f'<figure class="stat-pop" aria-hidden="true"><img src="{e(x["img"])}" alt="" loading="lazy"><figcaption>{e(x.get("cap",""))}</figcaption></figure>' if x.get("img") else '')+'</article>' for x in H['stats'])
    def slider(x):
        im=[i for i in x.get('images',[]) if i]
        if not im: return ''
        sl=''.join(f'<div class="sl-slide"><img src="{e(i)}" alt="{e(x["t"])} 사진 {n+1}" loading="lazy"></div>' for n,i in enumerate(im))
        nav=''
        if len(im)>1:
            dots=''.join(f'<button type="button" class="sl-dot{" on" if n==0 else ""}" data-i="{n}" aria-label="{n+1}번 사진"></button>' for n in range(len(im)))
            nav=f'<button type="button" class="sl-btn prev" aria-label="이전 사진">&#8249;</button><button type="button" class="sl-btn next" aria-label="다음 사진">&#8250;</button><div class="sl-dots">{dots}</div>'
        note=f'<span class="sl-note">{e(x["img_note"])}</span>' if x.get('img_note') else ''
        return f'<div class="slider" data-slider><div class="sl-track">{sl}</div>{nav}{note}</div>'
    services=''.join(f'<article class="service-card svc">{slider(x)}<div class="svc-body"><strong>{e(x["t"])}</strong><p>{t(x["d"])}</p></div></article>' for x in H['services']['items'])
    sc=H['schedule']
    rows=''.join(f'<div class="s-lab">{e(r["label"])}</div><div class="s-track"><i{" class=\"b\"" if r.get("dark") else ""} style="left:{num(r["start"])}%;width:{num(r["width"])}%">{e(r["bar"])}</i></div>' for r in sc['rows'])
    weeks=''.join(f'<div class="s-head">{e(w)}</div>' for w in sc['weeks'])
    steps=''.join(f'<article class="process-card"><span class="num">{i+1:02d}</span><strong>{e(x["t"])}</strong><p>{t(x["d"])}</p></article>' for i,x in enumerate(H['process']['steps']))
    spans=['span-7 tall','span-5 mid','span-4 mid','span-4 mid','span-4 mid']
    feat=[BYSLUG[k] for k in H['concept']['featured'] if k in BYSLUG]
    cc=''.join(concept_card(p,0,spans[i%5] if i<5 else 'span-4 mid') for i,p in enumerate(feat))
    concept_home=(f'<section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(H["concept"])}<div class="portfolio-grid">{cc}</div><p style="margin-top:22px"><a class="btn secondary" href="portfolio.html#concept">{e(H["concept"]["btn"])}</a></p></div></section>' if feat else '')
    faq=''.join(f'<article class="faq-item"><h4>{t(x["q"])}</h4><p>{t(x["a"])}</p></article>' for x in H['faq'])
    ds=H['design']; svgs=[viz.plan2d(),viz.iso3d()]
    tabs=''.join(f'<button type="button" class="d-tab{" on" if i==0 else ""}" data-i="{i}"><span class="d-no">{e(x["no"])}</span><span class="d-tt"><strong>{e(x["title"])}</strong><small>{t(x["desc"])}</small></span></button>' for i,x in enumerate(ds['stages']))
    def fig(i,x):
        if x.get('img'): return f'<img src="{e(x["img"])}" alt="{e(x["title"])}" loading="lazy">'
        return svgs[i] if i<len(svgs) else ''
    panels=''.join(f'<figure class="d-panel{" on" if i==0 else ""}" data-i="{i}"><div class="d-fig{" photo" if x.get("img") else ""}{" contain" if x.get("contain") else ""}">{fig(i,x)}</div><figcaption>{e(x["caption"])}</figcaption></figure>' for i,x in enumerate(ds['stages']))
    dlink=(f'<p style="margin-top:14px"><a class="btn secondary" href="{e(ds["link"])}">{e(ds["link_text"])}</a></p>' if ds.get('link') and ds.get('link_text') else '')
    design_html=f'<section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(ds)}<div class="design" data-design><div class="d-tabs" role="tablist">{tabs}</div><div class="d-panels">{panels}</div></div><p class="img-note">{t(ds["note"])}</p>{dlink}</div></section>'
    ct=H['cta']
    s+=f'''<main id="main">
  <section class="hero">
    <div class="hero-media"><img src="{e(h['img'])}" alt="{e(h['img_alt'])}"></div>
    <div class="wrap hero-content">
      <div class="hero-grid">
        <div class="hero-copy">
          <span class="eyebrow">{e(h['eyebrow'])}</span>
          <h1 class="display">{t(h['title'])}</h1>
          <p>{t(h['text'])}</p>
          <div class="hero-actions"><a class="btn light" href="contact.html#quoteForm">{e(h['btn1'])}</a><a class="btn secondary" href="portfolio.html">{e(h['btn2'])}</a></div>
        </div>
        <aside class="glass-card hero-note"><strong class="serif">{e(h['note_title'])}</strong><p>{t(h['note_text'])}</p></aside>
      </div>
      <div class="stats">{stats}</div>
      <p class="img-note">{t(h['img_note'])}</p>
    </div>
  </section>
  <section class="section"><div class="wrap">{sec_head(H['services'],False)}<div class="services-grid">{services}</div></div></section>
  {design_html}
  <section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(H['cases'],False,social_icons())}<div class="real-grid">{real_cards(0,6)}</div><p style="text-align:center;margin:28px 0 0"><a class="btn secondary" href="portfolio.html">시공 사례 전체 보기 ↗</a></p></div></section>
  <section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(sc)}
    <div class="sched" style="--n:{len(sc['weeks'])}" role="table" aria-label="{e(sc['aria'])}"><div class="s-head"></div>{weeks}{rows}</div></div></section>
  <section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(H['process'])}{flow_html()}<div class="steps8">{steps}</div></div></section>
  {materials_html()}
  {testimonials_html()}
  {concept_home}
  <section class="section-sm" style="padding-top:0"><div class="wrap premium-grid">
    <div class="cta-banner"><div class="content"><div><span class="eyebrow" style="color:rgba(255,255,255,.56)">{e(ct['eyebrow'])}</span><h2 class="title-md" style="color:#fff;margin-bottom:6px">{t(ct['title'])}</h2><p style="margin:0;color:rgba(255,255,255,.72)">{t(ct['text'])}</p></div><div class="inline-actions"><a class="btn light" href="contact.html#quoteForm">{e(ct['btn'])}</a><a class="btn secondary" style="color:#fff;border-color:rgba(255,255,255,.4)" href="tel:{TELH}">{e(TEL)}</a></div></div></div>
    <div class="faq-list">{faq}</div></div></section>
</main>
'''+footer(0)
    ld={"@context":"https://schema.org","@type":"HomeAndConstructionBusiness","name":S['brand'],"telephone":"+82-"+(TEL[1:] if TEL.startswith("0") else TEL),"email":MAIL,
        "address":{"@type":"PostalAddress","streetAddress":ADDR,"addressCountry":"KR"},"areaServed":S['region'],"sameAs":[INSTA,BLOG],"description":S['site_desc']}
    return s.replace('</head>','<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False).replace('</','<\\/')+'</script>\n</head>',1)

def build_about():
    st=A['story']; b=A['business']
    pts=''.join(f'<article data-i="{i}" tabindex="0"{" class=\"on\"" if i==0 else ""}><strong>{e(x["t"])}</strong><p>{t(x["d"])}</p></article>' for i,x in enumerate(st['points']))
    simgs=''.join(f'<img class="si{" on" if i==0 else ""}" src="{e(x.get("img") or st["img"])}" alt="{e(x.get("alt","디자인 컨셉 이미지"))}" loading="{"eager" if i==0 else "lazy"}">' for i,x in enumerate(st['points']))
    def kvlink(x):
        k=x['k']; v=x['v']
        if k=='전화': return f'tel:{TELH}',False
        if k=='이메일': return f'mailto:{MAIL}',False
        if k in ('인스타그램','Instagram'): return INSTA,True
        if k in ('블로그','Blog'): return BLOG,True
        return None,False
    def kvbox(x):
        href,ext=kvlink(x)
        if not href: return f'<dl class="kv-box"><dt>{e(x["k"])}</dt><dd>{t(x["v"])}</dd></dl>'
        tgt=' target="_blank" rel="noopener"' if ext else ''
        return f'<a class="kv-box kv-link" href="{e(href)}"{tgt}><dl><dt>{e(x["k"])}</dt><dd>{t(x["v"])} <span class="kv-go" aria-hidden="true">↗</span></dd></dl></a>'
    kv=''.join(kvbox(x) for x in b['items'])
    HI=A.get('history') or {}
    hist=''.join(f'<li><span class="tl-date serif">{e(x["date"])}</span><div><strong>{e(x["title"])}</strong>{("<p>"+t(x["desc"])+"</p>") if x.get("desc") else ""}</div></li>' for x in HI.get('items',[]))
    hist_html=f'<section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(HI)}<ol class="timeline">{hist}</ol></div></section>' if hist else ''
    return head(A['seo_title'],A['seo_desc'],path="about.html",keywords=A.get('seo_keywords',''))+topbar(0,'about')+f'''<main id="main">
{page_hero(A['hero'],'소개')}
<section class="section"><div class="wrap story-grid"><div class="story-image" id="storyImgs">{simgs}</div><div class="card-panel story-card"><span class="eyebrow">{e(st['eyebrow'])}</span><h2 class="title-lg">{t(st['title'])}</h2><p class="muted">{t(st['text'])}</p><div class="story-points" id="storyPts">{pts}</div></div></div></section>
<section class="section-sm" style="padding-top:0"><div class="wrap">{sec_head(b)}<div class="kv-grid">{kv}</div></div></section>
{hist_html}
</main>
'''+footer(0)

def build_portfolio():
    cards=''.join(concept_card(p,0,'span-4 mid') for p in PROJECTS)
    concept_sec=(f'<section class="section" id="concept" style="padding-top:0"><div class="wrap">{sec_head(P["concept"])}<div class="portfolio-grid" id="conceptGrid">{cards}</div></div></section>' if PROJECTS else '')
    F=P.get('filters',{})
    items=[r for r in CASES if r.get('slug') or r.get('img')]+PROJECTS
    names=F.get('cat_names',{'residential':'주거','commercial':'상업','bath':'욕실','showroom':'쇼룸'})
    used=[]
    for p in items:
        c=p.get('cat')
        if c and c not in used: used.append(c)
    def group(key,label,opts,attr):
        have=[o for o in opts if any(x.get(attr)==o for x in items)]
        if not have: return ''
        chips='<button class="filter-chip active" type="button" data-group="%s" data-filter="all">전체</button>'%key+''.join(f'<button class="filter-chip" type="button" data-group="{key}" data-filter="{e(o)}">{e(o)}</button>' for o in have)
        return f'<div class="filter-row"><span class="filter-label">{label}</span><div class="filter-bar">{chips}</div></div>'
    catopts=[c for c in names if c in used]+[c for c in used if c not in names]
    catchips='<button class="filter-chip active" type="button" data-group="category" data-filter="all">전체</button>'+''.join(f'<button class="filter-chip" type="button" data-group="category" data-filter="{e(c)}">{e(names.get(c,c))}</button>' for c in catopts)
    filters=f'<div class="filter-panel" data-project-filter><div class="filter-row"><span class="filter-label">공간별</span><div class="filter-bar">{catchips}</div></div>'+group('style','스타일별',F.get('styles',[]),'style_filter')+group('size','규모별',F.get('sizes',[]),'size_filter')+'<p class="filter-empty" id="filterEmpty" hidden>조건에 맞는 프로젝트가 아직 없습니다. 다른 조건을 선택해 보세요.</p></div>'
    return head(P['seo_title'],P['seo_desc'],path="portfolio.html",keywords=P.get('seo_keywords',''))+topbar(0,'portfolio')+f'''<main id="main">
{page_hero(P['hero'],'시공 사례')}
<section class="section" style="padding-top:0"><div class="wrap">{sec_head(P['real'],True,social_icons())}<div style="margin-bottom:34px">{filters}</div>{cat_blocks()}</div></section>
{concept_sec}
</main>
'''+footer(0)

def build_contact():
    d=C['direct']; f=C['form']; CALC=C['calc']
    to=''.join(f'<option>{e(x)}</option>' for x in f['types']); so=''.join(f'<option>{e(x)}</option>' for x in f['scopes']); so2=''.join(f'<option>{e(x)}</option>' for x in f.get('sources',[])); bo=''.join(f'<option>{e(x)}</option>' for x in f.get('budgets',[]))
    return head(C['seo_title'],C['seo_desc'],path="contact.html",keywords=C.get('seo_keywords',''))+topbar(0,'contact')+f'''<main id="main">
{page_hero(C['hero'],'견적 문의')}
<section class="section" style="padding-bottom:0"><div class="wrap"><div class="card-panel calc" id="calc" data-kinds='{json.dumps(CALC['kinds'],ensure_ascii=False)}'><span class="eyebrow">{e(CALC['eyebrow'])}</span><h2 class="title-lg">{t(CALC['title'])}</h2><p class="muted">{t(CALC['intro'])}</p>
<div class="calc-row"><label>공간<select id="calcKind">{''.join(f'<option value="{i}">{e(k["name"])}</option>' for i,k in enumerate(CALC['kinds']))}</select></label><label>마감<select id="calcTier"></select></label><label>{e(CALC['area_label'])}<input id="calcArea" inputmode="numeric" placeholder="예: 20"></label><label class="calc-out">{e(CALC['label'])} 기준 약<output id="calcResult">-</output></label></div>
<p class="muted" style="font-size:14px;margin:10px 0 4px" id="calcKindNote"></p><p class="muted" style="font-size:14px;margin:0 0 14px">{t(CALC['note'])}</p><a class="btn primary" href="#quoteForm" id="calcGo">{e(CALC['btn'])}</a></div></div></section>
<section class="section"><div class="wrap contact-grid">
<div class="card-panel contact-card"><span class="eyebrow">{e(d['eyebrow'])}</span><h2 class="title-lg">{t(d['title'])}</h2>
<div class="line-list"><dl class="line-item"><dt>전화 / 문자</dt><dd class="big-contact">{e(TEL)}</dd></dl><dl class="line-item"><dt>이메일</dt><dd>{e(MAIL)}</dd></dl><dl class="line-item"><dt>주소</dt><dd>{e(ADDR)}</dd></dl><dl class="line-item"><dt>Instagram</dt><dd><a href="{e(INSTA)}" target="_blank" rel="noopener">{e(INSTA.rstrip('/').split('/')[-1] and '@'+INSTA.rstrip('/').split('/')[-1])}</a></dd></dl><dl class="line-item"><dt>Blog</dt><dd><a href="{e(BLOG)}" target="_blank" rel="noopener">{e(BLOG.replace('https://',''))}</a></dd></dl></div>
<div class="inline-actions" style="margin-top:22px"><a class="btn primary" href="tel:{TELH}">{e(d['btn_tel'])}</a><a class="btn secondary" href="mailto:{e(MAIL)}">{e(d['btn_mail'])}</a></div></div>
<form class="card-panel form-card" id="quoteForm" novalidate><span class="eyebrow">{e(f['eyebrow'])}</span><h2 class="title-lg">{t(f['title'])}</h2><p class="muted" style="margin-top:-2px;margin-bottom:22px">{t(f['intro'])}</p>
<div class="form-grid">
<label>현장명 *<input id="siteName" placeholder="예: ○○아파트 / ○○식당"></label>
<label>연락처 *<input id="phone" inputmode="tel" autocomplete="tel" placeholder="010-0000-0000"></label>
<label>시공 분야 *<select id="type"><option value="">선택하세요</option>{to}</select></label>
<label>시공 범위<select id="scope"><option value="">선택하세요</option>{so}</select></label>
<label>평수<input id="area" inputmode="numeric" placeholder="예: 32"></label>
<label>시공 예정일<input id="when" placeholder="예: 12월 초"></label>
<label>{e(f.get('budget_label','예산 범위'))}<select id="budget"><option value="">선택하세요</option>{bo}</select></label>
<label>{e(f.get('location_label','현장 위치'))}<input id="location" placeholder="{e(f.get('location_ph','예: 안산시 상록구 ○○동'))}"></label>
<label>{e(f.get('source_label','어디서 보고 오셨나요?'))}<select id="source"><option value="">선택하세요</option>{so2}</select></label>
<label>{e(f.get('referrer_label','소개해 주신 분 (선택)'))}<input id="referrer" placeholder="예: 홍길동 / ○○공인중개사"></label>
<label class="full">상담 내용<textarea id="memo" placeholder="원하시는 분위기, 공사 범위, 일정 등을 적어주세요."></textarea></label>
<label class="full agree"><input type="checkbox" id="agree"> <span>{e(f['agree'])} <a href="privacy.html" target="_blank" rel="noopener">개인정보처리방침</a></span></label>
<div class="full"><p class="form-err" id="formErr" role="alert"></p><button class="btn primary" type="submit">{e(f['submit'])}</button></div></div>
<div class="output" id="outputBox"><pre id="outputText"></pre><div class="inline-actions"><a class="btn primary" id="smsLink" href="#">문자로 보내기</a><a class="btn secondary" id="mailLink" href="#">이메일로 보내기</a><button class="btn secondary" id="copyBtn" type="button">내용 복사</button></div><p class="muted" style="font-size:14px;margin:12px 0 0">{t(f['sent_note'])}</p></div></form>
</div></section>
</main>
'''+footer(0)

def proj_cta(title):
    return f'''<section class="section-sm" style="padding-top:0"><div class="wrap"><div class="cta-banner"><div class="content"><div><span class="eyebrow" style="color:rgba(255,255,255,.56)">Quote</span><h2 class="title-md" style="color:#fff;margin-bottom:6px">이 프로젝트와 유사한 공간 연출을 원하시나요?</h2><p style="margin:0;color:rgba(255,255,255,.72)">평수와 공간만 알려주시면 대략 견적을 바로 확인하고, 상담을 신청할 수 있습니다.</p></div><div class="inline-actions"><a class="btn light" href="../contact.html#calc">간편 견적 문의하기</a><a class="btn secondary" style="color:#fff;border-color:rgba(255,255,255,.4)" href="tel:{TELH}">전화 상담</a></div></div></div></div></section>
'''

def build_project(p):
    s=head(p.get('seo_title') or f"{p['title']} 디자인 컨셉 | {S['brand']}",p['desc'],1,path=f"projects/{p['slug']}.html",keywords=p.get('seo_keywords',''))+topbar(1,'portfolio')
    rel=[q for q in PROJECTS if q['slug']!=p['slug']]
    same=[q for q in rel if q['cat']==p['cat']]
    rel=(same+[q for q in rel if q not in same])[:3]
    relhtml=''.join(f'''<a class="related-card" href="{e(q['slug'])}.html"><img src="../{e(q['img'])}" alt="{e(q['title'])} 디자인 컨셉" loading="lazy"><div class="body"><span class="badge-solid">{e(q['tag'])} · {e(PG['badge_suffix'])}</span><h4 class="serif">{e(q['title'])}</h4><p>{e(q['ko'])}</p></div></a>''' for q in rel)
    s+=f'''<main id="main">
<section class="hero project-hero"><div class="hero-media"><img src="../{e(p['img'])}" alt="{e(p['title'])} 디자인 컨셉"></div><div class="wrap hero-content"><div class="breadcrumb"><a href="../index.html">Home</a><span class="sep">/</span><a href="../portfolio.html#concept">시공 사례</a><span class="sep">/</span><span>{e(p['title'])}</span></div><span class="eyebrow">{e(p['tag'])} · {e(PG['eyebrow_suffix'])}</span><h1 class="display serif" style="max-width:8em">{e(p['title'])}</h1><p style="max-width:42em;color:rgba(255,255,255,.78);margin:0">{e(p['ko'])} — {e(p['desc'])}</p><div class="project-facts"><dl class="fact-box"><dt>구분</dt><dd>{e(p['type'])}</dd></dl><dl class="fact-box"><dt>스타일</dt><dd>{e(p['style'])}</dd></dl><dl class="fact-box"><dt>범위</dt><dd>{e(p['scope'])}</dd></dl><dl class="fact-box"><dt>이미지</dt><dd>{e(PG['image_fact'])}</dd></dl></div></div></section>
<section class="section"><div class="wrap project-content"><div class="sticky-box"><div class="card-panel facts-card"><span class="eyebrow">{e(PG['side_eyebrow'])}</span><h2 class="title-md">{e(PG['side_title'])}</h2><p class="muted">{e(p['desc'])}</p><div class="note-card"><p>{t(PG['side_note'])}</p></div><div class="inline-actions" style="margin-top:18px"><a class="btn primary" href="../contact.html#quoteForm">{e(PG['btn1'])}</a><a class="btn secondary" href="../portfolio.html#concept">{e(PG['btn2'])}</a></div></div></div>
<div><div class="gallery-grid"><figure class="large"><img src="../{e(p['img'])}" alt="{e(p['title'])} 디자인 컨셉"></figure></div><div class="note-card" style="margin-top:24px"><span class="eyebrow">{e(PG['note_eyebrow'])}</span><h3 class="title-md" style="margin-top:8px">{e(PG['note_title'])}</h3><p>{t(p['note'])}</p></div></div></div></section>
<section class="section-sm" style="padding-top:0"><div class="wrap"><div class="section-head"><div><span class="eyebrow">{e(PG['more_eyebrow'])}</span><h2 class="title-lg">{e(PG['more_title'])}</h2></div></div><div class="related-grid">{relhtml}</div></div></section>
<section class="section-sm" style="padding-top:0"><div class="wrap">{share_bar(p['title'],p['img'])}</div></section>{proj_cta(p['title'])}</main>
'''+footer(1)
    return s

def build_case(r):
    s=head(f"{r['title']} | {S['brand']}",r.get('intro') or r['desc'],1,path=f"cases/{r['slug']}.html",keywords=r.get('seo_keywords',''))+topbar(1,'portfolio')
    groups=[]
    for it in r['gallery']:
        if it['group'] not in [x[0] for x in groups]: groups.append((it['group'],[]))
        [x for x in groups if x[0]==it['group']][0][1].append(it)
    facts=''.join(f'<dl class="fact-box"><dt>{e(f["k"])}</dt><dd>{e(f["v"])}</dd></dl>' for f in r.get('facts',[]))
    toc=''.join(f'<a href="#g{i}">{e(n)}</a>' for i,(n,_) in enumerate(groups))
    body=''
    for i,(n,its) in enumerate(groups):
        figs=''.join(f'<figure class="cs-fig"><button type="button" class="cs-open" data-full="../{e(it["img"])}" data-cap="{e(it.get("caption",""))}"><img src="../{e(it["img"])}" alt="{e(r["title"])} {e(n)}" loading="lazy"></button>' + (f'<figcaption>{e(it["caption"])}</figcaption>' if it.get('caption') and len(its)==1 else '') + '</figure>' for it in its)
        cap=next((it['caption'] for it in its if it.get('caption')),'')
        body+=f'<section class="cs-group" id="g{i}"><div class="cs-head"><span class="num">{i+1:02d}</span><h2 class="title-md">{e(n)}</h2>' + (f'<p class="muted">{e(cap)}</p>' if cap and len(its)>1 else '') + f'</div><div class="cs-grid n{min(len(its),4)}">{figs}</div></section>'
    s+=f'''<main id="main">
<section class="hero project-hero"><div class="hero-media"><img src="../{e(r['img'])}" alt="{e(r['title'])}"></div><div class="wrap hero-content"><div class="breadcrumb"><a href="../index.html">Home</a><span class="sep">/</span><a href="../portfolio.html">시공 사례</a><span class="sep">/</span><span>{e(r['title'])}</span></div><span class="eyebrow">{e(r['badge'])}</span><h1 class="display" style="max-width:9em">{e(r['title'])}</h1><p style="max-width:42em;color:rgba(255,255,255,.78);margin:0">{t(r.get('intro') or r['desc'])}</p><div class="project-facts">{facts}</div></div></section>
<section class="section-sm"><div class="wrap"><nav class="cs-toc">{toc}</nav>{ba_html(r)}{body}{extras_html(r)}{share_bar(r['title'],r['img'])}<p style="margin-top:34px"><a class="btn primary" href="../contact.html#quoteForm">이런 공사 상담하기</a> <a class="btn secondary" href="../portfolio.html">시공 사례 목록</a></p></div></section>
{proj_cta(r['title'])}</main>
<div class="lb" id="lb" hidden><button type="button" class="lb-x" aria-label="닫기">&times;</button><img alt=""><p></p></div>
'''+footer(1)
    return s


def build_privacy():
    body=f'''<main id="main"><section class="section"><div class="wrap" style="max-width:820px"><span class="eyebrow">Privacy</span><h1 class="title-lg" style="margin:8px 0 18px">개인정보처리방침</h1>
<p class="muted">{e(S['brand'])}(이하 "회사")는 견적·상담 문의 과정에서 최소한의 개인정보만 다루며, 아래와 같이 안내드립니다.</p>
<h2 class="title-md" style="margin-top:28px">1. 수집하는 항목</h2><p>현장명, 연락처, 시공 분야·공간 정보, 상담 내용, 소개해 주신 분(선택 입력 시).</p>
<h2 class="title-md" style="margin-top:28px">2. 이용 목적</h2><p>견적 산출, 상담 회신, 현장 방문 일정 조율.</p>
<h2 class="title-md" style="margin-top:28px">3. 전달 방식</h2><p>견적 문의 양식은 서버에 저장되지 않습니다. 입력하신 내용은 방문자께서 직접 누르는 문자 또는 이메일 앱으로 회사에 전달되며, 그 시점에 회사가 받게 됩니다.</p>
<h2 class="title-md" style="margin-top:28px">4. 보유 및 파기</h2><p>상담이 종료되면 지체 없이 파기합니다. 계약이 체결된 경우 관련 법령이 정한 기간 동안만 보관합니다.</p>
<h2 class="title-md" style="margin-top:28px">5. 제3자 제공</h2><p>법령에 근거한 경우를 제외하고 동의 없이 제3자에게 제공하지 않습니다.</p>
<h2 class="title-md" style="margin-top:28px">6. 방문 통계</h2><p>사이트 이용 통계(방문 수, 문의 버튼 클릭 등)를 위해 광고·분석 도구를 사용하는 경우가 있으며, 이 경우 쿠키 등으로 접속 정보가 수집될 수 있습니다. 브라우저 설정에서 쿠키를 거부할 수 있습니다.</p>
<h2 class="title-md" style="margin-top:28px">7. 이용자의 권리와 문의</h2><p>열람·정정·삭제를 요청하실 수 있습니다. 개인정보 보호책임자: {e(S.get('biz_rep',''))} (대표) · 문의: {e(TEL)} · {e(MAIL)}</p>
<p class="muted" style="margin-top:28px">시행일: 사이트 공개일부터 적용합니다.</p></div></section></main>'''
    return head('개인정보처리방침 | '+S['brand'],'D& 인테리어 개인정보처리방침',path="privacy.html")+topbar(0,'privacy')+body+footer(0)

def build_404():
    body='''<main id="main"><section class="section"><div class="wrap" style="text-align:center;max-width:640px"><span class="eyebrow">404</span><h1 class="title-lg" style="margin:8px 0 14px">페이지를 찾을 수 없습니다</h1><p class="muted">주소가 바뀌었거나 삭제된 페이지입니다. 아래 버튼으로 이동해 주세요.</p><div class="inline-actions" style="justify-content:center;margin-top:22px"><a class="btn primary" href="/index.html">홈으로</a><a class="btn secondary" href="/portfolio.html">시공 사례 보기</a><a class="btn secondary" href="/contact.html#quoteForm">견적 문의</a></div></div></section></main>'''
    return head('페이지를 찾을 수 없습니다 | '+S['brand'],'요청하신 페이지를 찾을 수 없습니다.',path="404.html")+topbar(0,'404')+body+footer(0)

import re as _re
try:
    from PIL import Image as _Im
except Exception: _Im=None
def _fix_imgs(content,path):
    depth=path.count('/')
    def rep(m):
        tag=m.group(0)
        src=_re.search(r'src="([^"]+)"',tag)
        if not src or src.group(1).startswith(('http','data:')): return tag
        if 'width=' not in tag and _Im:
            fp=os.path.normpath(os.path.join(ROOT,os.path.dirname(path),src.group(1)))
            if os.path.isfile(fp):
                try:
                    w,h=_Im.open(fp).size; tag=tag[:-1].rstrip('/')+f' width="{w}" height="{h}">'
                except Exception: pass
        ctx=content[max(0,m.start()-60):m.start()]
        if 'loading=' not in tag and 'hero' not in tag and 'hero-media' not in ctx and 'brand-mark' not in ctx: tag=tag[:-1]+' loading="lazy">'
        if 'decoding=' not in tag: tag=tag[:-1]+' decoding="async">'
        return tag
    return _re.sub(r'<img\b[^>]*>',rep,content)

def write(path,content):
    if path.endswith('.html'): content=_fix_imgs(content,path)

    full=os.path.join(ROOT,path); os.makedirs(os.path.dirname(full),exist_ok=True)
    open(full,'w',encoding='utf-8').write(content)

if __name__=='__main__':
    # 삭제된 컨셉 페이지 정리
    pd=os.path.join(ROOT,'projects')
    keep={p['slug']+'.html' for p in PROJECTS}
    if os.path.isdir(pd):
        for f in os.listdir(pd):
            if f.endswith('.html') and f not in keep: os.remove(os.path.join(pd,f))
    write('index.html',build_index()); write('about.html',build_about()); write('portfolio.html',build_portfolio()); write('contact.html',build_contact()); write('privacy.html',build_privacy()); write('404.html',build_404())
    for p in PROJECTS: write(f'projects/{p["slug"]}.html',build_project(p))
    cd=os.path.join(ROOT,'cases'); ck={r['slug']+'.html' for r in CASES if r.get('slug') and r.get('gallery')}
    os.makedirs(cd,exist_ok=True)
    for f in os.listdir(cd):
        if f.endswith('.html') and f not in ck: os.remove(os.path.join(cd,f))
    for r in CASES:
        if r.get('slug') and r.get('gallery'): write(f'cases/{r["slug"]}.html',build_case(r))
    origin=site_origin()
    if origin:
        paths=['index.html','about.html','portfolio.html','contact.html','privacy.html']
        paths += [f"projects/{p['slug']}.html" for p in PROJECTS]
        paths += [f"cases/{r['slug']}.html" for r in CASES if r.get('slug') and r.get('gallery')]
        xml='<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{e(origin+"/"+x)}</loc></url>\n' for x in paths)+'</urlset>\n'
        write('sitemap.xml',xml)
        write('robots.txt',f'User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\nSitemap: {origin}/sitemap.xml\n')
    else:
        # 아직 도메인이 없으므로 잘못된 canonical/sitemap 을 공개하지 않습니다.
        for name in ('sitemap.xml','robots.txt'):
            f=os.path.join(ROOT,name)
            if os.path.exists(f): os.remove(f)
    print('generated',4+len(PROJECTS),'pages; SEO domain:',origin or 'pending')
