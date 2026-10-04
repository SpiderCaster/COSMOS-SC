window.scTest={behavior:function(t){
 var a=document.querySelector('.sc-skip');
 t.ok('offscreen_until_focus',a.getBoundingClientRect().right<=0);
 a.focus();
 t.ok('on_screen_when_focused',a.getBoundingClientRect().left>=0&&a.getBoundingClientRect().right<=innerWidth);
 t.ok('target_exists',!!document.getElementById(a.getAttribute('href').slice(1)));
 a.blur();
}, prepare:function(){document.querySelector('.sc-skip').focus()}};
