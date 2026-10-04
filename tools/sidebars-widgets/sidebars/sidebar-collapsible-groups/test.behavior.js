window.scTest={behavior:function(t,c){
 var d=document.querySelectorAll('.sc-grp');
 t.ok('three_groups',d.length===3);
 if(c.width<900){t.ok('first_open_rest_closed',d[0].open&&!d[1].open&&!d[2].open)}
 else{t.ok('all_open_on_wide',d[0].open&&d[1].open&&d[2].open)}
 d[1].open=false;
 d[1].querySelector('summary').click();
 t.ok('summary_click_opens_group_two',d[1].open===true);
 d[1].querySelector('summary').click();
 t.ok('summary_click_closes_again',d[1].open===false);
 t.ok('links_not_rendered_when_closed',d[1].querySelector('a').checkVisibility()===false);
 d[1].open=true;d[2].open=true;
}};
