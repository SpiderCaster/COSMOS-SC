window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-mread');
 t.ok('ordered',!!w.querySelector('ol')&&w.querySelectorAll('li').length===3);
 t.ok('period_shown',w.querySelector('.sc-mr-p').textContent==='Last 7 days');
 t.ok('reads_optional',w.querySelectorAll('.sc-mr-b .sc-meta').length===2);
 t.ok('rank_hidden_from_readers',w.querySelector('.sc-mr-n').getAttribute('aria-hidden')==='true');
}};
