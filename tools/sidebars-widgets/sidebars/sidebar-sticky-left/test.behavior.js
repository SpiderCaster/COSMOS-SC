window.scTest={behavior:function(t,c){
 var s=document.querySelector('.sc-lay-side'),m=document.querySelector('.sc-lay-main'),pos=getComputedStyle(s).position;
 t.ok('toc_built_in_rail',s.querySelectorAll('.sc-toc a').length===5,String(s.querySelectorAll('.sc-toc a').length));
 if(c.width>=900){
  var mr=m.getBoundingClientRect(),sr=s.getBoundingClientRect();
  t.ok('rail_left_of_main',sr.right<=mr.left+1&&Math.abs(sr.width-260)<2,sr.width);
  t.ok('position_sticky',pos==='sticky',pos);
  window.scrollTo(0,700);
  return t.sleep(60).then(function(){var r=s.getBoundingClientRect();t.ok('rail_pinned_near_top',r.top>=0&&r.top<=40,'top='+r.top);window.scrollTo(0,0)});
 }else{t.ok('static_on_phone',pos==='static',pos)}
}};
