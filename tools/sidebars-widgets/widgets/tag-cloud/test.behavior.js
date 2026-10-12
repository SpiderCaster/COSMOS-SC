window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-tags');var a=w.querySelectorAll('a');
 t.ok('five_chips',a.length===5);
 t.ok('rel_tag',Array.prototype.every.call(a,function(x){return x.rel==='tag'}));
 t.ok('chips_wrap_in_row',a[1].getBoundingClientRect().top<=a[0].getBoundingClientRect().bottom+8);
 var s={};Array.prototype.forEach.call(a,function(x){s[getComputedStyle(x).fontSize]=1});
 t.ok('one_font_size',Object.keys(s).length===1,Object.keys(s).join());
}};
