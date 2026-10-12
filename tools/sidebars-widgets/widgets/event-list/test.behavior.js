window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-events');
 t.ok('two_events',w.querySelectorAll('.sc-ev-i').length===2);
 t.ok('time_elements',w.querySelectorAll('time[datetime]').length===2);
 t.ok('title_link_optional',w.querySelectorAll('.sc-ev-a').length===1&&w.querySelectorAll('.sc-ev-t').length===1);
 t.ok('place_optional',/at Fixture hall/.test(w.textContent)&&!/at\s*$/.test(w.querySelectorAll('.sc-ev-b')[1].textContent.trim()));
 t.ok('more_link',!!w.querySelector('.sc-ev-more'));
}};
