import json,sys
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
head=t[:se].replace('<title>Marquetery All Products</title>','<title>Marquetery</title>')
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
hs=h[:h.index('</style>')+8]
hm=h[h.index('<main id="top">'):h.index('</main>')+7].replace('<main id="top">','<main id="view-home">',1)
hscript=h[h.index('<script>')+8:h.rindex('</script>')].replace('const PRODUCTS = /*DATA*/[];','')
hscript=hscript.replace('$("news").addEventListener("submit",e=>{e.preventDefault(); $("news-note").textContent = okEmail($("email").value) ? "Thank you. You\'re on the list." : "Enter a valid email address, like name@example.com.";});','')
assert '$("news")' not in hscript
router='''
(()=>{
  const PRODUCT_VIEWS=["collections","tables","storage","seating","lighting","accessories"];
  const home=document.getElementById("view-home"), prod=document.getElementById("view-products"), piece=document.getElementById("view-product"), proj=document.getElementById("view-projects"), rooms=document.getElementById("view-rooms");
  const navProj=document.querySelector('nav.main a[href="#bespoke"]'), navRooms=document.querySelector('nav.main a[href="#inspirations"]');
  const navCol=document.querySelector('nav.main a[href="#collections"]');
  function route(){
    const h=(location.hash||"").slice(1).toLowerCase();
    const isProj=h==="bespoke", isRooms=h==="inspirations"||h==="projects";
    const isProd=PRODUCT_VIEWS.includes(h);
    const isPiece=!isProd && !isProj && !isRooms && !!h && window.renderProduct(h);
    home.hidden=isProd||isPiece||isProj||isRooms; prod.hidden=!isProd; piece.hidden=!isPiece; proj.hidden=!isProj; rooms.hidden=!isRooms;
    if(navProj){ if(isProj) navProj.setAttribute("aria-current","page"); else navProj.removeAttribute("aria-current"); }
    if(navRooms){ if(isRooms) navRooms.setAttribute("aria-current","page"); else navRooms.removeAttribute("aria-current"); }
    if(isProj||isRooms){ navCol.removeAttribute("aria-current"); document.title=(isProj?"Bespoke":"Inspirations")+" · Marquetery"; window.scrollTo(0,0); return; }
    if(isPiece){ window.scrollTo(0,0); navCol.setAttribute("aria-current","page"); return; }
    if(isProd) navCol.setAttribute("aria-current","page"); else navCol.removeAttribute("aria-current");
    document.title = isProd ? "Collections · Marquetery" : "Marquetery";
    const target = !isProd && h && h!=="home" && h!=="top" ? document.getElementById(h) : null;
    if(target) target.scrollIntoView(); else window.scrollTo(0,0);
  }
  window.addEventListener("hashchange", route);
  document.querySelectorAll('a.logo, a[href="#home"]').forEach(a=>a.addEventListener("click",()=>{ if(location.hash==="#home"||!location.hash) setTimeout(route,0); }));
  route();
})();
'''
page=head+'\n'+hs+'\n'+pts+'\n'+pjs+'\n'+rms+'\n'+header+hm+'\n'+pm+'\n'+ptm+'\n'+pjm+'\n'+rmm+'\n'+footer+'\n'+drawer+'<script>\nconst PRODUCTS = '+data+';\n(()=>{'+hscript+'})();\n(()=>{'+pscript+'})();\n(()=>{'+ptscript+'})();\n(()=>{'+pjscript+'})();\n(()=>{'+rmscript+'})();\n'+router+'</script>\n'
pass
BASE_FIX='*{box-sizing:border-box}\nbody{margin:0}\nimg{max-width:100%}\n[hidden]{display:none!important}'
he=page.index('</style>')+8
doc='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'+page[:he]+'\n</head>\n<body>\n'+page[he:]+'\n</body>\n</html>\n'
open(OUT+'/index.html','w').write(doc.replace('*{box-sizing:border-box}',BASE_FIX,1))
