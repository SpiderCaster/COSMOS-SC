window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-links');
 t.ok('two_links',w.querySelectorAll('a').length===2);
 t.ok('note_optional',w.querySelectorAll('.sc-meta').length===1);
 t.ok('nav_named',!!document.getElementById(w.getAttribute('aria-labelledby')));
}};
