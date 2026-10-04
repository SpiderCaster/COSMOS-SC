window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-related');
 t.ok('two_rows',w.querySelectorAll('a').length===2);
 t.ok('kicker_above_title',(function(){var k=w.querySelector('.sc-rel-k'),h=w.querySelector('.sc-rel-t');return k.getBoundingClientRect().bottom<=h.getBoundingClientRect().top+1})());
 t.ok('kicker_optional',w.querySelectorAll('.sc-rel-k').length===1);
 t.ok('aside_labelled',!!document.getElementById(w.getAttribute('aria-labelledby')));
}};
