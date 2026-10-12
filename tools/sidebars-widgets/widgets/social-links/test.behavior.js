window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-social');var a=w.querySelectorAll('a');
 t.ok('three_links',a.length===3);
 t.ok('rel_me',Array.prototype.every.call(a,function(x){return /\bme\b/.test(x.rel)&&/noopener/.test(x.rel)}));
 t.ok('no_images_or_svg',w.querySelectorAll('img,svg').length===0);
 t.ok('wraps_without_overflow',w.scrollWidth<=w.clientWidth+1);
}};
