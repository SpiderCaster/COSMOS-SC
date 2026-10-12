window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-sched');
 t.ok('caption',!!w.querySelector('caption'));
 t.ok('column_and_row_headers',w.querySelectorAll('thead th[scope=col]').length===3&&w.querySelectorAll('tbody th[scope=row]').length===2);
 t.ok('no_images',w.querySelectorAll('img,svg').length===0);
 t.ok('fits_width',w.querySelector('table').getBoundingClientRect().right<=innerWidth+1);
}};
