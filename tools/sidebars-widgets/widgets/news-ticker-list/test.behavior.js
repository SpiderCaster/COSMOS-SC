window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-news-l');
 t.ok('two_items',w.querySelectorAll('li').length===2);
 t.ok('tag_optional',w.querySelectorAll('.sc-nw-tag').length===1);
 t.ok('no_motion',w.querySelectorAll('marquee').length===0&&getComputedStyle(w.querySelector('ul')).animationName==='none');
}};
