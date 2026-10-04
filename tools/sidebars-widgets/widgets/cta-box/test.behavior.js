window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-cta');var b=w.querySelector('a.sc-btn');
 t.ok('one_button',w.querySelectorAll('a').length===1);
 t.ok('button_full_width',Math.abs(b.getBoundingClientRect().width-(w.clientWidth-32))<2,b.getBoundingClientRect().width+' in '+w.clientWidth);
 t.ok('button_text_white',getComputedStyle(b).color==='rgb(255, 255, 255)',getComputedStyle(b).color);
 t.ok('button_18px',getComputedStyle(b).fontSize==='18px');
}};
