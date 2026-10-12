window.scTest={behavior:function(t){
 var b=document.querySelector('.sc-btt');
 t.ok('hidden_at_top',b.hidden===true);
 window.scrollTo(0,900);window.dispatchEvent(new Event('scroll'));
 return t.sleep(60).then(function(){
  t.ok('shown_after_scroll',b.hidden===false,'y='+window.pageYOffset);
  var r=b.getBoundingClientRect();
  t.ok('fixed_in_viewport',r.right<=innerWidth&&r.bottom<=innerHeight&&r.width>=44&&r.height>=44);
  b.click();window.dispatchEvent(new Event('scroll'));return t.sleep(60)}).then(function(){
  t.ok('click_scrolls_to_top',window.pageYOffset===0,'y='+window.pageYOffset);
  t.ok('hidden_again',b.hidden===true);
  window.scrollTo(0,900);window.dispatchEvent(new Event('scroll'));return t.sleep(60)});
}, prepare:function(t){window.scrollTo(0,900);window.dispatchEvent(new Event('scroll'));return t.sleep(60)}};
