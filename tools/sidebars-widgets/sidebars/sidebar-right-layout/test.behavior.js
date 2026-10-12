window.scTest={behavior:function(t,c){
 var m=document.querySelector('.sc-lay-main').getBoundingClientRect(),s=document.querySelector('.sc-lay-side').getBoundingClientRect();
 if(c.width<900){
  t.ok('stacked_below_900',s.top>=m.bottom-1,'side top '+s.top+' main bottom '+m.bottom);
  t.ok('full_width_when_stacked',Math.abs(s.width-m.width)<2);
 }else{
  t.ok('side_right_of_main',s.left>=m.right-1);
  t.ok('side_300',Math.abs(s.width-300)<2,s.width);
  t.ok('tops_align',Math.abs(s.top-m.top)<2);
 }
 t.ok('dom_order_main_first',!!(document.querySelector('.sc-lay-main').compareDocumentPosition(document.querySelector('.sc-lay-side'))&4));
 t.ok('aside_landmark',document.querySelector('.sc-lay-side').getAttribute('aria-label')==='Sidebar');
}};
