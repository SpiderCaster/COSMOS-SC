window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-call');var a=w.querySelectorAll('a');
 t.ok('tel_links',Array.prototype.every.call(a,function(x){return /^tel:/.test(x.getAttribute('href'))}));
 t.ok('urgent_marked_once',w.querySelectorAll('.sc-wc-u').length===1);
 t.ok('rows_44',Array.prototype.every.call(a,function(x){return x.getBoundingClientRect().height>=44}));
 t.ok('role_optional',w.querySelectorAll('.sc-meta').length===1);
}};
