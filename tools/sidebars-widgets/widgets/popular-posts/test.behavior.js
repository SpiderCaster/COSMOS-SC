window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-popular');var n=w.querySelectorAll('.sc-pop-n');
 t.ok('ordered_list',!!w.querySelector('ol'));
 t.ok('numbers_1_2_3',Array.prototype.map.call(n,function(x){return x.textContent}).join(',')==='1,2,3');
 t.ok('numbers_hidden_from_readers',Array.prototype.every.call(n,function(x){return x.getAttribute('aria-hidden')==='true'}));
 t.ok('meta_optional',w.querySelectorAll('.sc-meta').length===2);
}};
