window.scTest={behavior:function(t){
 var n=document.querySelector('.sc-toc');var a=n.querySelectorAll('a');
 var hs=document.querySelectorAll('article h2,article h3');
 t.ok('shown',!n.hidden);
 t.ok('one_link_per_heading',a.length===hs.length&&a.length===5,a.length+' vs '+hs.length);
 t.ok('hrefs_resolve',Array.prototype.every.call(a,function(x){return !!document.getElementById(x.getAttribute('href').slice(1))}));
 t.ok('ids_unique',(function(){var s={},ok=true;Array.prototype.forEach.call(hs,function(h){if(s[h.id])ok=false;s[h.id]=1});return ok})());
 t.ok('h3_indented',n.querySelector('.sc-toc-3')&&getComputedStyle(n.querySelector('.sc-toc-3 a')).paddingLeft==='20px');
}};
