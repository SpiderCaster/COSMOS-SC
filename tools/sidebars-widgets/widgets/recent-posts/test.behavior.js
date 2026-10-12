window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-recent');var a=w.querySelectorAll('a.sc-row');
 t.ok('rows',a.length===3,a.length);
 t.ok('time_elements',w.querySelectorAll('time[datetime]').length===3);
 t.ok('current_marked',w.querySelectorAll('a[aria-current="page"]').length===1);
 t.ok('no_images',w.querySelectorAll('img').length===0);
 t.ok('heading_linked',document.getElementById(w.getAttribute('aria-labelledby')).textContent==='Recent posts');
 t.ok('rows_44',Array.prototype.every.call(a,function(x){return x.getBoundingClientRect().height>=44}));
}};
