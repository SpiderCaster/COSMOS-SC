window.scTest={behavior:function(t,c){
 var m=document.querySelector('.sc-lay-main').getBoundingClientRect(),s=document.querySelector('.sc-lay-side').getBoundingClientRect();
 if(c.width<900){t.ok('content_first_below_900',s.top>=m.bottom-1)}
 else{t.ok('side_left_of_main',s.right<=m.left+1);t.ok('side_300',Math.abs(s.width-300)<2,s.width);t.ok('tops_align',Math.abs(s.top-m.top)<2)}
 t.ok('dom_order_main_first',!!(document.querySelector('.sc-lay-main').compareDocumentPosition(document.querySelector('.sc-lay-side'))&4));
}};
