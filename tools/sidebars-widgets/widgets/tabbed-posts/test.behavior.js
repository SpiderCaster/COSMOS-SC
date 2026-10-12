window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-tabs');var tabs=w.querySelectorAll('[role=tab]');var ps=w.querySelectorAll('[role=tabpanel]');
 t.ok('bar_shown_by_script',!w.querySelector('.sc-tp-bar').hidden);
 t.ok('first_selected',tabs[0].getAttribute('aria-selected')==='true'&&!ps[0].hidden&&ps[1].hidden);
 t.ok('roving_tabindex',tabs[0].tabIndex===0&&tabs[1].tabIndex===-1);
 tabs[1].click();
 t.ok('click_selects_second',tabs[1].getAttribute('aria-selected')==='true'&&ps[0].hidden&&!ps[1].hidden);
 tabs[1].dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
 t.ok('arrow_right_wraps',tabs[0].getAttribute('aria-selected')==='true'&&document.activeElement===tabs[0]);
 tabs[0].dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true}));
 t.ok('end_key',tabs[1].getAttribute('aria-selected')==='true');
 t.ok('aria_wiring',tabs[0].getAttribute('aria-controls')===ps[0].id&&ps[0].getAttribute('aria-labelledby')===tabs[0].id);
 t.ok('tabs_44',tabs[0].getBoundingClientRect().height>=44);
}};
