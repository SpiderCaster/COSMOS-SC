window.scTest={behavior:function(t,c){
 var s=document.querySelector('.sc-lay-side');var pos=getComputedStyle(s).position;
 if(c.width>=900){
  t.ok('position_sticky',pos==='sticky',pos);
  var top0=s.getBoundingClientRect().top;
  window.scrollTo(0,700);
  return t.sleep(60).then(function(){
   var r=s.getBoundingClientRect();
   t.ok('page_scrolled',window.pageYOffset>=600,'y='+window.pageYOffset);
   t.ok('side_pinned_near_top',r.top>=0&&r.top<=40,'top='+r.top+' before='+top0);
   window.scrollTo(0,0);
  });
 }else{t.ok('static_on_phone',pos==='static',pos)}
}};
