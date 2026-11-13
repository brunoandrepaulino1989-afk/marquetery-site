import json,sys, os
S=sys.argv[1]; OUT=sys.argv[2]
t=open(S+'/template.html').read(); h=open(S+'/home_template.html').read()
data=json.dumps(json.load(open(S+'/products.json')),ensure_ascii=False)
def links(s):
    s=s.replace('products.html#','#').replace('"products.html"','"#collections"').replace('href="products.html"','href="#collections"').replace('"index.html"','"#home"')
    return s
t=links(t); h=links(h)
t=t.replace('try{history.replaceState(null,"",state.group==="all"?location.pathname:"#"+slug(state.group))}catch(err){}','try{history.replaceState(null,"","#"+(state.group==="all"?"collections":slug(state.group)))}catch(err){}')
assert '"#"+(state.group' in t
se=t.index('</style>')+len('</style>')
head=t[:se].replace('<title>Marquetry All Products</title>','<title>Marquetry</title>')
header=t[t.index('<div class="notice">'):t.index('<main id="top">')].replace(' aria-current="page"','')
pm=t[t.index('<main id="top">'):t.index('</main>')+7]
pm=pm[:pm.index('<section class="band" id="bespoke">')]+'</main>'
pm=pm.replace('<main id="top">','<main id="view-products" hidden>',1)
footer=t[t.index('<footer id="contact">'):t.index('</footer>')+9]
drawer=t[t.index('<div class="scrim"'):t.index('<script>')]
pscript=t[t.index('<script>')+8:t.rindex('</script>')].replace('const PRODUCTS = /*DATA*/[];','')
pt=open(S+'/product_template.html').read()
pts=pt[:pt.index('</style>')+8]
ptm=pt[pt.index('<main id="view-product" hidden>'):pt.index('</main>')+7]
ptscript=pt[pt.index('<script>')+8:pt.rindex('</script>')]
pj=open(S+'/projects_template.html').read()
pjs=pj[:pj.index('</style>')+8]
pjm=pj[pj.index('<main id="view-projects" hidden>'):pj.index('<script>')]
pjscript=pj[pj.index('<script>')+8:pj.rindex('</script>')]
rm=open(S+'/rooms_template.html').read()
rms=rm[:rm.index('</style>')+8]
rmm=rm[rm.index('<main id="view-rooms" hidden>'):rm.index('<script>')]
rmscript=rm[rm.index('<script>')+8:rm.rindex('</script>')]
tr=open(S+'/trade_template.html').read()
trs=tr[:tr.index('</style>')+8]
trm=tr[tr.index('<main id="view-trade" hidden>'):tr.index('<script>')]
trscript=tr[tr.index('<script>')+8:tr.rindex('</script>')]
ab=open(S+'/about_template.html').read()
abs_=ab[:ab.index('</style>')+8]
abm=ab[ab.index('<main id="view-about" hidden>'):ab.index('<script>')]
pl=open(S+'/pricelist_template.html').read()
pls=pl[:pl.index('</style>')+8]
plm=pl[pl.index('<main id="view-pricelist" hidden>'):pl.index('<script>')]
plscript=pl[pl.index('<script>')+8:pl.rindex('</script>')]
hs=h[:h.index('</style>')+8]
hm=h[h.index('<main id="top">'):h.index('</main>')+7].replace('<main id="top">','<main id="view-home">',1)
hscript=h[h.index('<script>')+8:h.rindex('</script>')].replace('const PRODUCTS = /*DATA*/[];','')
hscript=hscript.replace('$("news").addEventListener("submit",e=>{e.preventDefault(); $("news-note").textContent = okEmail($("email").value) ? "Thank you. You\'re on the list." : "Enter a valid email address, like name@example.com.";});','')
assert '$("news")' not in hscript
router='''
(()=>{ const hd=document.querySelector("header.site"), mb=document.querySelector(".menu-btn"); if(!hd||!mb) return;
  mb.setAttribute("aria-expanded","false");
  const set=o=>{ hd.classList.toggle("menu-open",o); mb.setAttribute("aria-expanded",String(o)); mb.textContent=o?"Close":"Menu"; };
  mb.addEventListener("click",()=>set(!hd.classList.contains("menu-open")));
  document.querySelector("nav.main").addEventListener("click",e=>{ if(e.target.closest("a")) set(false); });
  window.addEventListener("hashchange",()=>set(false));
  document.addEventListener("keydown",e=>{ if(e.key==="Escape") set(false); });
})();

(()=>{
  const PRODUCT_VIEWS=["collections","tables","storage","seating","lighting","accessories"];
  const home=document.getElementById("view-home"), prod=document.getElementById("view-products"), piece=document.getElementById("view-product"), proj=document.getElementById("view-projects"), rooms=document.getElementById("view-rooms"), trade=document.getElementById("view-trade"), navTrade=document.querySelector('nav.main a[href="#trade"]'), about=document.getElementById("view-about"), plist=document.getElementById("view-pricelist"), navAbout=document.querySelector('nav.main a[href="#about"]');
  const navProj=document.querySelector('nav.main a[href="#atelier"]'), navRooms=document.querySelector('nav.main a[href="#inspirations"]');
  const navCol=document.querySelector('nav.main a[href="#collections"]');
  function route(){
    const h=(location.hash||"").slice(1).toLowerCase();
    const isProj=h==="atelier"||h==="bespoke", isRooms=h==="inspirations"||h==="projects", isTrade=h==="trade", isAbout=h==="about", isPl=!!plist&&(h==="pricelist"||h==="price-list");
    const isProd=PRODUCT_VIEWS.includes(h);
    const isPiece=!isProd && !isProj && !isRooms && !isTrade && !isAbout && !isPl && !!h && window.renderProduct(h);
    home.hidden=isProd||isPiece||isProj||isRooms||isTrade||isAbout||isPl; trade.hidden=!isTrade; about.hidden=!isAbout; if(plist) plist.hidden=!isPl; if(navAbout){ if(isAbout) navAbout.setAttribute("aria-current","page"); else navAbout.removeAttribute("aria-current"); } if(navTrade){ if(isTrade) navTrade.setAttribute("aria-current","page"); else navTrade.removeAttribute("aria-current"); } prod.hidden=!isProd; piece.hidden=!isPiece; proj.hidden=!isProj; rooms.hidden=!isRooms;
    if(navProj){ if(isProj) navProj.setAttribute("aria-current","page"); else navProj.removeAttribute("aria-current"); }
    if(navRooms){ if(isRooms) navRooms.setAttribute("aria-current","page"); else navRooms.removeAttribute("aria-current"); }
    if(isProj||isRooms||isTrade||isAbout||isPl){ navCol.removeAttribute("aria-current"); document.title=(isProj?"Atelier":isTrade?"Trade":isAbout?"About":isPl?"Price List":"Inspirations")+" · Marquetry"; window.scrollTo(0,0); return; }
    if(isPiece){ window.scrollTo(0,0); navCol.setAttribute("aria-current","page"); return; }
    if(isProd) navCol.setAttribute("aria-current","page"); else navCol.removeAttribute("aria-current");
    document.title = isProd ? "Collections · Marquetry" : "Marquetry.uk | Handcrafted marquetry furniture, made to order";
    const target = !isProd && h && h!=="home" && h!=="top" ? document.getElementById(h) : null;
    if(target) target.scrollIntoView(); else window.scrollTo(0,0);
  }
  window.addEventListener("hashchange", route);
  document.querySelectorAll('a.logo, a[href="#home"]').forEach(a=>a.addEventListener("click",()=>{ if(location.hash==="#home"||!location.hash) setTimeout(route,0); }));
  route();
})();
'''
page=head+'\n'+hs+'\n'+pts+'\n'+pjs+'\n'+rms+'\n'+trs+'\n'+abs_+'\n'+pls+'\n'+header+hm+'\n'+pm+'\n'+ptm+'\n'+pjm+'\n'+rmm+'\n'+trm+'\n'+abm+'\n'+plm+'\n'+footer+'\n'+drawer+'<script>\nconst PRODUCTS = '+data+';\n(()=>{'+hscript+'})();\n(()=>{'+pscript+'})();\n(()=>{'+ptscript+'})();\n(()=>{'+pjscript+'})();\n(()=>{'+rmscript+'})();\n(()=>{'+trscript+'})();\n'+plscript+'\n'+router+'</script>\n'
pass
BASE_FIX='*{box-sizing:border-box}\nbody{margin:0}\nimg{max-width:100%}\n[hidden]{display:none!important}'
he=page.index('</style>')+8
doc='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'+page[:he]+'\n</head>\n<body>\n'+page[he:]+'\n</body>\n</html>\n'
PRIVATE='price-list-a19173cf.html'
def wrap(pg,extra=''):
  he=pg.index('</style>')+8
  return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'+extra+pg[:he]+'\n</head>\n<body>\n'+pg[he:]+'\n</body>\n</html>\n').replace('*{box-sizing:border-box}',BASE_FIX,1)
public=page.replace(pls+'\n','',1).replace(plm+'\n','',1).replace(plscript+'\n','',1)
SEO=('<link rel="canonical" href="https://marquetry.uk/">\n'
 '<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<link rel="icon" href="/favicon.ico" sizes="32x32">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
 '<meta name="theme-color" content="#F0EEE9">\n'
 '<meta property="og:type" content="website">\n<meta property="og:site_name" content="Marquetry.uk">\n'
 '<meta property="og:title" content="Marquetry.uk | Handcrafted marquetry furniture">\n'
 '<meta property="og:description" content="Marquetry furniture made to order in Portugal and delivered white glove across the UK. Tables, storage, seating and bespoke pieces.">\n'
 '<meta property="og:url" content="https://marquetry.uk/">\n<meta property="og:image" content="https://marquetry.uk/og-image.jpg">\n'
 '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n'
 '<script type="application/ld+json">{"@context":"https://schema.org","@type":"FurnitureStore","name":"Marquetry.uk","legalName":"After Hours Collections Ltd","url":"https://marquetry.uk/","logo":"https://marquetry.uk/apple-touch-icon.png","image":"https://marquetry.uk/og-image.jpg","email":"info@marquetry.uk","telephone":"+447519450282","address":{"@type":"PostalAddress","streetAddress":"66 Paul Street","addressLocality":"London","postalCode":"EC2A 4NA","addressCountry":"GB"}}</script>\n')
public=public.replace('<title>Marquetry</title>','<title>Marquetry.uk | Handcrafted marquetry furniture, made to order</title>',1)
open(OUT+'/index.html','w').write(wrap(public,SEO))
priv=page.replace(router,'if(!location.hash) history.replaceState(null,"","#pricelist");\n'+router,1)
open(OUT+'/'+PRIVATE,'w').write(wrap(priv,'<meta name="robots" content="noindex, nofollow">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'))

# Server-side price data for the price-request email function (not linked from the site; /netlify/* is blocked in netlify.toml)
import re as _re
_g=json.loads(_re.search(r'const PL_GBP = (\{.*?\});',pl).group(1))
_P=json.load(open(S+'/products.json'))
os.makedirs(OUT+'/netlify/functions',exist_ok=True)
json.dump({p['id']:{'name':p['name'],'price':_g[p['id']],'dimensions':p.get('dimensions',''),'image':p.get('image','')} for p in _P if p['id'] in _g},open(OUT+'/netlify/functions/prices.json','w'),ensure_ascii=False,indent=1)
