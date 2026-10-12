window.scTest={behavior:function(t,c){
 var box=document.querySelector('.sc-drw'),btn=box.querySelector('.sc-drw-open'),p=box.querySelector('.sc-drw-panel'),cl=box.querySelector('.sc-drw-close'),ov=box.querySelector('.sc-drw-ov');
 function key(k,el,sh){(el||document.activeElement).dispatchEvent(new KeyboardEvent('keydown',{key:k,shiftKey:!!sh,bubbles:true}))}
 if(c.width<900){
  t.ok('panel_hidden_when_closed',getComputedStyle(p).visibility==='hidden');
  t.ok('opener_collapsed',btn.getAttribute('aria-expanded')==='false'&&btn.getBoundingClientRect().height>=44);
  btn.click();
  var r=p.getBoundingClientRect();
  t.ok('opens',p.classList.contains('sc-open')&&btn.getAttribute('aria-expanded')==='true');
  t.ok('panel_on_screen_left',r.left>=0&&r.right<=innerWidth&&r.width<=320.5,r.left+'..'+r.right);
  t.ok('focus_on_close',document.activeElement===cl);
  t.ok('overlay_shown_and_scroll_locked',!ov.hidden&&document.documentElement.classList.contains('sc-drw-lock'));
  key('Escape');
  t.ok('escape_closes',!p.classList.contains('sc-open')&&btn.getAttribute('aria-expanded')==='false');
  t.ok('focus_returns_to_opener',document.activeElement===btn);
  t.ok('lock_released',!document.documentElement.classList.contains('sc-drw-lock')&&ov.hidden);
  btn.click();ov.click();
  t.ok('overlay_click_closes',!p.classList.contains('sc-open'));
  btn.click();cl.click();
  t.ok('close_button_closes',!p.classList.contains('sc-open')&&document.activeElement===btn);
  btn.click();
  var f=p.querySelectorAll('a[href],button,input,select,textarea,summary'),last=f[f.length-1];
  last.focus();key('Tab',last,false);
  t.ok('tab_wraps_to_first',document.activeElement===f[0]);
  f[0].focus();key('Tab',f[0],true);
  t.ok('shift_tab_wraps_to_last',document.activeElement===last);
  cl.click();
  box.className=box.className.replace('sc-drw-left','sc-drw-right');
  t.ok('right_variant_parks_offscreen_right',p.getBoundingClientRect().left>=innerWidth-1,String(p.getBoundingClientRect().left));
  box.className=box.className.replace('sc-drw-right','sc-drw-left');
 }else{
  t.ok('opener_hidden_on_wide',getComputedStyle(btn).display==='none');
  t.ok('panel_visible_inline',getComputedStyle(p).visibility==='visible'&&getComputedStyle(p).position==='static');
  var m=box.querySelector('.sc-lay-main').getBoundingClientRect(),s=p.getBoundingClientRect();
  t.ok('left_side_before_main',s.right<=m.left+1&&Math.abs(s.width-300)<2,s.width);
 }
}, prepare:function(t,c){if(c.width<900){document.querySelector('.sc-drw-open').click()}}};
