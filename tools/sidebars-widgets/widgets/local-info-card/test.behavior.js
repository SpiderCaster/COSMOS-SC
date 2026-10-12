window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-local');
 t.ok('definition_list',!!w.querySelector('dl')&&w.querySelectorAll('dt').length===2&&w.querySelectorAll('dd').length===2);
 t.ok('updated_time',!!w.querySelector('time[datetime]'));
 t.ok('source_link',/^Source: /.test(w.querySelector('.sc-lc-src').textContent));
 t.ok('value_right_aligned',getComputedStyle(w.querySelector('dd')).textAlign==='right');
}};
