window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-faq');var d=w.querySelectorAll('details');
 t.ok('two_details',d.length===2);
 t.ok('closed_by_default',!d[0].open&&!d[1].open);
 t.ok('answer_not_rendered_when_closed',d[0].querySelector('.sc-fq-a').checkVisibility()===false);
 d[0].querySelector('summary').click();
 t.ok('summary_click_opens',d[0].open===true);
 t.ok('answer_visible_when_open',d[0].querySelector('.sc-fq-a').checkVisibility()===true);
 t.ok('summary_44',d[1].querySelector('summary').getBoundingClientRect().height>=44);
}};
