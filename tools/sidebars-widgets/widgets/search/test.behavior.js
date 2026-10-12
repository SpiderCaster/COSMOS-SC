window.scTest={behavior:function(t){
 var f=document.querySelector('.sc-search');var i=f.querySelector('input');var l=f.querySelector('label');
 t.ok('role_search',f.getAttribute('role')==='search');
 t.ok('label_for_matches',l.htmlFor===i.id&&i.labels[0]===l);
 t.ok('param_name',i.name==='q');
 t.ok('method_get',f.method==='get');
 t.ok('action_set',f.getAttribute('action')==='/search/');
 t.ok('button_beside_field',f.querySelector('button').getBoundingClientRect().left>i.getBoundingClientRect().left);
 t.ok('field_fills_row',i.getBoundingClientRect().width>=120,i.getBoundingClientRect().width);
}};
