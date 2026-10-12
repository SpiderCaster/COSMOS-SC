window.scTest={behavior:function(t,c){
 var w=document.querySelector('.sc-jump');var l=w.querySelector('.sc-jp-l');
 t.ok('four_links',w.querySelectorAll('a').length===4);
 t.ok('strip_scrolls_when_narrow',c.width>=600||l.scrollWidth>l.clientWidth,l.scrollWidth+' vs '+l.clientWidth);
 t.ok('page_does_not_scroll_sideways',document.documentElement.scrollWidth<=innerWidth+1);
 t.ok('nav_named',w.getAttribute('aria-label')==='Jump to section');
}};
