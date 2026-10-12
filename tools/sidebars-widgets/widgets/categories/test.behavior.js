window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-cats');
 t.ok('three_links',w.querySelectorAll('a').length===3);
 t.ok('counts_only_when_set',w.querySelectorAll('.sc-count').length===2);
 t.ok('current_marked',w.querySelectorAll('a[aria-current="page"]').length===1);
 t.ok('nav_labelled',!!document.getElementById(w.getAttribute('aria-labelledby')));
 var c=w.querySelector('.sc-count');var r=c.getBoundingClientRect();var a=c.parentNode.getBoundingClientRect();
 t.ok('count_inside_row',r.right<=a.right+0.5&&r.left>=a.left);
}};
