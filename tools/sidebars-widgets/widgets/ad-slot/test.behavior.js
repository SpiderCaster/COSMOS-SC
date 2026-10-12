window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-ad');var b=w.querySelector('.sc-ad-box');
 t.ok('slot_height_reserved_250',b.getBoundingClientRect().height>=250,b.getBoundingClientRect().height);
 t.ok('slot_width_300_or_fits',b.getBoundingClientRect().width<=300.5);
 t.ok('label_text',w.querySelector('.sc-ad-l').textContent==='Advertisement');
 t.ok('slot_id_attr',w.getAttribute('data-slot')==='fixture-sidebar-1');
 var c=w.cloneNode(true);c.querySelector('.sc-ad-box').textContent='';w.parentNode.appendChild(c);
 t.ok('empty_hides_slot',getComputedStyle(c).display==='none');
 c.parentNode.removeChild(c);
 var tall=w.cloneNode(true);tall.className='sc-w sc-ad sc-ad-300x600';w.parentNode.appendChild(tall);
 t.ok('size_600_reserves_600',tall.querySelector('.sc-ad-box').getBoundingClientRect().height>=600);
 tall.parentNode.removeChild(tall);
}};
