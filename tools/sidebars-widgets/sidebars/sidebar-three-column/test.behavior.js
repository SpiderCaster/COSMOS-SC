window.scTest={behavior:function(t,c){
 var m=document.querySelector('.sc-lay-main').getBoundingClientRect(),a=document.querySelector('.sc-lay-a').getBoundingClientRect(),b=document.querySelector('.sc-lay-b').getBoundingClientRect();
 if(c.width>=1100){
  t.ok('left_main_right_order',a.right<=m.left+1&&m.right<=b.left+1);
  t.ok('widths_240_280',Math.abs(a.width-240)<2&&Math.abs(b.width-280)<2,a.width+','+b.width);
 }else if(c.width>=700){t.ok('asides_side_by_side_under_main',a.top>=m.bottom-1&&Math.abs(a.top-b.top)<2&&b.left>=a.right-1)}
 else{t.ok('all_stacked',a.top>=m.bottom-1&&b.top>=a.bottom-1)}
 t.ok('two_aside_landmarks',document.querySelectorAll('.sc-lay aside').length===2||document.querySelectorAll('.sc-lay-side').length===2);
}};
