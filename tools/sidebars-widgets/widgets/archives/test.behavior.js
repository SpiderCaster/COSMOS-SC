window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-arch');
 t.ok('three_links',w.querySelectorAll('a').length===3);
 t.ok('count_optional',w.querySelectorAll('.sc-arch-c').length===2);
 t.ok('urls_are_paths',Array.prototype.every.call(w.querySelectorAll('a'),function(a){return /^\/\d{4}\/\d{2}\/$/.test(a.getAttribute('href'))}));
}};
