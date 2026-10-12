window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-spons');var a=w.querySelector('a');
 t.ok('rel_sponsored',/\bsponsored\b/.test(a.rel)&&/noopener/.test(a.rel));
 t.ok('label_before_name',w.querySelector('.sc-sp-l').getBoundingClientRect().bottom<=w.querySelector('.sc-sp-n').getBoundingClientRect().top+1);
 t.ok('no_images',w.querySelectorAll('img,svg').length===0);
 t.ok('label_text',w.querySelector('.sc-sp-l').textContent==='Sponsored');
}};
