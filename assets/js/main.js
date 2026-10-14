
// 공통 커스텀 선택 목록: 칸 바로 아래, 같은 너비, 글자 가운데 정렬
window.enhanceSelect=function(sel){
  if(sel.classList.contains('dd-native'))return;
  var wrap=document.createElement('div'); wrap.className='dd';
  var btn=document.createElement('button'); btn.type='button'; btn.className='dd-btn'; btn.setAttribute('aria-haspopup','listbox');
  var ul=document.createElement('ul'); ul.className='dd-list'; ul.setAttribute('role','listbox');
  sel.parentNode.insertBefore(wrap,sel); wrap.appendChild(sel); wrap.appendChild(btn); wrap.appendChild(ul); sel.classList.add('dd-native'); sel.tabIndex=-1;
  function label(){ var o=sel.options[sel.selectedIndex]; btn.textContent=o?o.text:''; btn.classList.toggle('ph',!sel.value); }
  function build(){ ul.innerHTML=''; Array.prototype.forEach.call(sel.options,function(o,i){ var li=document.createElement('li'); li.textContent=o.text; li.setAttribute('role','option'); if(i===sel.selectedIndex) li.className='on';
    li.addEventListener('click',function(){ sel.selectedIndex=i; sel.dispatchEvent(new Event('change',{bubbles:true})); close(); }); ul.appendChild(li); }); }
  function close(){ wrap.classList.remove('open'); }
  btn.addEventListener('click',function(e){ e.stopPropagation(); var was=wrap.classList.contains('open'); document.querySelectorAll('.dd.open').forEach(function(d){d.classList.remove('open')}); if(!was){ build(); wrap.classList.add('open'); } });
  sel.addEventListener('change',label);
  new MutationObserver(label).observe(sel,{childList:true});
  document.addEventListener('click',close);
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') close(); });
  label();
};
(function(){
  var top=document.querySelector('.topbar');
  function onS(){ if(top) top.classList.toggle('scrolled', window.scrollY>20); }
  onS(); window.addEventListener('scroll',onS,{passive:true});
  var mt=document.getElementById('menuBtn'), nav=document.querySelector('.nav-links');
  if(mt&&nav) mt.setAttribute('aria-expanded','false'); mt.addEventListener('click',function(){ mt.setAttribute('aria-expanded', nav.classList.toggle('open')?'true':'false'); });

  // 프로젝트 필터 (공간·스타일·규모, 여러 조건 동시 적용)
  var chips=document.querySelectorAll('.filter-chip[data-filter]');
  var fcards=document.querySelectorAll('[data-filterable]');
  var fstate={};
  function applyFilter(){
    var shown=0;
    fcards.forEach(function(k){
      var ok=true;
      Object.keys(fstate).forEach(function(g){
        var v=fstate[g]; if(!v||v==='all')return;
        if(k.getAttribute('data-'+g)!==v) ok=false;
      });
      k.style.display=ok?'':'none'; if(ok) shown++;
    });
    document.querySelectorAll('[data-cat-block]').forEach(function(b){var any=false;b.querySelectorAll('[data-filterable]').forEach(function(k){if(k.style.display!=='none')any=true;});b.style.display=any?'':'none';});
    var em=document.getElementById('filterEmpty'); if(em) em.hidden=shown>0;
  }
  chips.forEach(function(c){
    c.addEventListener('click',function(){
      var g=c.getAttribute('data-group')||'category', f=c.getAttribute('data-filter');
      fstate[g]=f;
      chips.forEach(function(x){ if((x.getAttribute('data-group')||'category')===g) x.classList.toggle('active',x===c); });
      applyFilter();
    });
  });

  // quote form (no backend: builds text, user sends via SMS/mail/copy)
  var form=document.getElementById('quoteForm');
  if(form){
    var g=function(id){var e=document.getElementById(id);return e?e.value.trim():''};
    form.addEventListener('submit',function(ev){ try{ if(window.fbq) fbq('track','Lead'); }catch(_){}
      ev.preventDefault();
      var err=document.getElementById('formErr');
      var agree=document.getElementById('agree');
      if(!g('siteName')||!g('phone')){ err.textContent='현장명(위치)과 연락처는 꼭 입력해 주세요.'; return; }
      if(agree&&!agree.checked){ err.textContent='개인정보 수집·이용에 동의해 주세요.'; return; }
      err.textContent='';
      var t=['[D& 인테리어 견적 문의]',
        '현장: '+g('siteName'),'연락처: '+g('phone'),'공간유형: '+g('type'),
        '공사범위: '+g('scope'),'면적: '+g('area'),'희망시기: '+g('when'),
        '현장 위치: '+g('location'),'예산: '+g('budget'),'유입 경로: '+g('source')+(g('referrer')?' / 소개: '+g('referrer'):''),'요청: '+g('memo')].join('\n');
      document.getElementById('outputText').textContent=t;
      document.getElementById('outputBox').classList.add('on');
      var tel=(window.DAND_TEL||'07077771114');
      var sm=document.getElementById('smsLink'); var sn=window.DAND_SMS||''; if(sn){sm.href='sms:'+sn+'?body='+encodeURIComponent(t);} else {sm.style.display='none';}
      document.getElementById('mailLink').href='mailto:'+(window.DAND_MAIL||'theproper@naver.com')+'?subject='+encodeURIComponent('[견적문의] '+g('siteName'))+'&body='+encodeURIComponent(t);
      document.getElementById('outputBox').scrollIntoView({behavior:'smooth',block:'nearest'});
    });
    try{ var q=new URLSearchParams(location.search).get('src'); var map={blog:'네이버 블로그',insta:'인스타그램',carrot:'당근',search:'네이버 검색·플레이스',agent:'중개사 소개',ref:'지인 소개'};
      var sel=document.getElementById('source'); if(q&&map[q]&&sel){ for(var i=0;i<sel.options.length;i++){ if(sel.options[i].text===map[q]){ sel.selectedIndex=i; sel.dispatchEvent(new Event('change')); } } } }catch(e){}
    var cb=document.getElementById('copyBtn');
    if(cb) cb.addEventListener('click',function(){
      var t=document.getElementById('outputText').textContent;
      function done(){cb.textContent='복사됨 ✓';setTimeout(function(){cb.textContent='내용 복사'},1500)}
      if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(done,fb)}else fb();
      function fb(){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');done()}catch(e){}a.remove()}
    });
  }
})();

// 슬라이더
(function(){
  document.querySelectorAll('[data-slider]').forEach(function(sl){
    var tr=sl.querySelector('.sl-track'), dots=sl.querySelectorAll('.sl-dot'), n=tr.children.length, timer=null;
    function cur(){return Math.round(tr.scrollLeft/tr.clientWidth)}
    function go(i){ i=(i+n)%n; tr.scrollTo({left:i*tr.clientWidth,behavior:'smooth'}); }
    function mark(){var c=cur();dots.forEach(function(d,k){d.classList.toggle('on',k===c)})}
    tr.addEventListener('scroll',function(){clearTimeout(tr._t);tr._t=setTimeout(mark,60)},{passive:true});
    var p=sl.querySelector('.prev'),nx=sl.querySelector('.next');
    if(p)p.addEventListener('click',function(){go(cur()-1);reset()});
    if(nx)nx.addEventListener('click',function(){go(cur()+1);reset()});
    dots.forEach(function(d,k){d.addEventListener('click',function(){go(k);reset()})});
    function reset(){ if(timer)clearInterval(timer); start() }
    function start(){ if(n<2||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return; timer=setInterval(function(){go(cur()+1)},5000) }
    sl.addEventListener('mouseenter',function(){clearInterval(timer)});
    sl.addEventListener('mouseleave',start);
    start();
  });
})();

// 설계 단계 탭 (클릭 또는 마우스 오버)
(function(){
  document.querySelectorAll('[data-design]').forEach(function(box){
    var tabs=box.querySelectorAll('.d-tab'), panels=box.querySelectorAll('.d-panel');
    function show(i){ tabs.forEach(function(t,k){t.classList.toggle('on',k===i)}); panels.forEach(function(p,k){p.classList.toggle('on',k===i)}); }
    tabs.forEach(function(t,k){
      t.addEventListener('click',function(){show(k)});
      t.addEventListener('mouseenter',function(){ if(window.matchMedia('(hover:hover)').matches) show(k) });
    });
  });
})();

// 사진 확대 보기
(function(){
  var lb=document.getElementById('lb'); if(!lb) return;
  var im=lb.querySelector('img'), cp=lb.querySelector('p');
  document.querySelectorAll('.cs-open').forEach(function(b){
    b.addEventListener('click',function(){ im.src=b.dataset.full; cp.textContent=b.dataset.cap||''; lb.hidden=false; });
  });
  function close(){lb.hidden=true; im.src=''}
  lb.addEventListener('click',close);
  document.addEventListener('keydown',function(e){ if(e.key==='Escape') close() });
})();

// 대략 견적 계산기
(function(){
  var c=document.getElementById('calc'); if(!c)return;
  var kinds=JSON.parse(c.getAttribute('data-kinds')), kind=document.getElementById('calcKind'), tier=document.getElementById('calcTier'),
      inp=document.getElementById('calcArea'), out=document.getElementById('calcResult'), kn=document.getElementById('calcKindNote');
  function fmt(m){ var eok=Math.floor(m/10000), r=Math.round(m%10000); return (eok?eok+'억 ':'')+(r?r.toLocaleString('ko-KR')+'만 원':(eok?'':'0원')); }
  function fill(){
    var k=kinds[+kind.value]; tier.innerHTML='';
    k.tiers.forEach(function(t){var o=document.createElement('option');o.value=t.py;o.textContent=t.name+' · 평당 '+t.py+'만';tier.appendChild(o)});
    kn.textContent=k.note||''; upd();
  }
  function upd(){
    var py=parseFloat(tier.value)||0;
    var a=parseFloat(inp.value.replace(/[^0-9.]/g,''));
    out.textContent=(a>0&&a<1000)?fmt(a*py):'-';
    sync(a, (a>0&&a<1000)?fmt(a*py):'');
  }
  // 간단 견적 -> 간편 견적 문의 양식 동기화
  function sync(a, price){
    var f=document.getElementById('area'); if(f&&a>0) f.value=String(a);
    var ty=document.getElementById('type');
    if(ty){ var kname=kinds[+kind.value].name; for(var i=0;i<ty.options.length;i++){ if(ty.options[i].text.indexOf(kname)===0){ ty.selectedIndex=i; ty.dispatchEvent(new Event('change')); break; } } }
    var memo=document.getElementById('memo');
    if(memo){
      var tag='[간단 견적] ';
      var line=(a>0&&price)?tag+kinds[+kind.value].name+' · '+tier.options[tier.selectedIndex].text.split(' · ')[0]+' · '+a+'평 · 약 '+price+' (별도 항목 제외, 상담 후 확정)':'';
      var rest=memo.value.split('\n').filter(function(l){return l.indexOf(tag)!==0}).join('\n').replace(/^\n+/,'');
      memo.value=line?(rest?line+'\n'+rest:line):rest;
    }
  }
  inp.addEventListener('input',upd); tier.addEventListener('change',upd); kind.addEventListener('change',fill);
  fill();
  document.querySelectorAll('.calc select').forEach(window.enhanceSelect);
})();

document.querySelectorAll('.form-card select').forEach(window.enhanceSelect);

// 소개 페이지: 설계/시공/일정에 마우스를 올리면 해당 이미지로 전환
(function(){
  var box=document.getElementById('storyImgs'), pts=document.getElementById('storyPts'); if(!box||!pts)return;
  var imgs=box.querySelectorAll('.si'), items=pts.querySelectorAll('article');
  function show(i){ imgs.forEach(function(m,k){m.classList.toggle('on',k===i)}); items.forEach(function(a,k){a.classList.toggle('on',k===i)}); }
  items.forEach(function(a,i){
    a.addEventListener('mouseenter',function(){show(i)});
    a.addEventListener('focus',function(){show(i)});
    a.addEventListener('click',function(){show(i)});
  });
})();

// 시공 전·후 비교 슬라이더
(function(){
  document.querySelectorAll('[data-ba]').forEach(function(ba){
    var stage=ba.querySelector('.ba-stage'), wrap=ba.querySelector('.ba-before-wrap'), h=ba.querySelector('.ba-handle'), dragging=false;
    function set(p){ p=Math.max(0,Math.min(100,p)); wrap.style.width=p+'%'; h.style.left=p+'%'; h.setAttribute('aria-valuenow',Math.round(p)); }
    function pos(e){ var r=stage.getBoundingClientRect(); var x=(e.touches?e.touches[0].clientX:e.clientX)-r.left; set(x/r.width*100); }
    stage.addEventListener('pointerdown',function(e){ dragging=true; stage.setPointerCapture&&stage.setPointerCapture(e.pointerId); pos(e); });
    stage.addEventListener('pointermove',function(e){ if(dragging) pos(e); });
    stage.addEventListener('pointerup',function(){ dragging=false; });
    stage.addEventListener('pointercancel',function(){ dragging=false; });
    h.addEventListener('keydown',function(e){ var v=parseFloat(h.getAttribute('aria-valuenow'))||50; if(e.key==='ArrowLeft') set(v-5); if(e.key==='ArrowRight') set(v+5); });
    set(50);
  });
})();

// 저장·공유 (Pinterest / 인스타·카톡 공유 / 링크 복사)
(function(){
  document.querySelectorAll('[data-share]').forEach(function(bar){
    var title=bar.getAttribute('data-title')||document.title;
    function absImg(){ var a=document.createElement('a'); a.href=bar.getAttribute('data-img'); return a.href; }
    bar.querySelectorAll('[data-act]').forEach(function(b){
      b.addEventListener('click',function(){
        var act=b.getAttribute('data-act'), url=location.href.split('#')[0];
        if(act==='pin'){ window.open('https://www.pinterest.com/pin/create/button/?url='+encodeURIComponent(url)+'&media='+encodeURIComponent(absImg())+'&description='+encodeURIComponent(title+' | D& 인테리어'),'_blank','noopener'); }
        else if(act==='share'){
          if(navigator.share){ navigator.share({title:title,text:title+' | D& 인테리어',url:url}).catch(function(){}); }
          else copy(url,b);
        } else copy(url,b);
      });
    });
    function copy(u,btn){
      var old=btn.textContent;
      function done(){ btn.textContent='링크가 복사되었습니다 ✓'; setTimeout(function(){btn.textContent=old},1600); }
      if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(u).then(done,fb); } else fb();
      function fb(){ var a=document.createElement('textarea'); a.value=u; document.body.appendChild(a); a.select(); try{document.execCommand('copy');done()}catch(e){} a.remove(); }
    }
  });
})();

(function(){document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="tel:"],a[href^="sms:"]');if(a){try{if(window.fbq)fbq('track','Contact');}catch(_){}}});})();
