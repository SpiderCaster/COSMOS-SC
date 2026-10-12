window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-pn');
 t.ok('prev_and_next',!!w.querySelector('a[rel=prev]')&&!!w.querySelector('a[rel=next]'));
 t.ok('nav_named',w.getAttribute('aria-label')==='Post navigation');
 var a=w.querySelectorAll('a');
 t.ok('stacked',a[1].getBoundingClientRect().top>=a[0].getBoundingClientRect().bottom);
}};
