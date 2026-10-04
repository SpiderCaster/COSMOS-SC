window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-hours');var cur=w.querySelectorAll('tr[aria-current="date"]');
 t.ok('seven_rows',w.querySelectorAll('tbody tr').length===7);
 t.ok('row_headers',w.querySelectorAll('th[scope="row"]').length===7);
 t.ok('one_row_marked',cur.length===1);
 t.ok('marked_row_is_today',cur.length===1&&cur[0].getAttribute('data-day')===String(new Date().getDay()));
 t.ok('table_fits',w.querySelector('table').getBoundingClientRect().width<=w.getBoundingClientRect().width+1);
}};
