window.scTest={behavior:function(t){
 var b=document.querySelector('.sc-rp');
 t.ok('progressbar_role',b.getAttribute('role')==='progressbar'&&b.getAttribute('aria-valuemax')==='100');
 t.ok('starts_at_zero',b.getAttribute('aria-valuenow')==='0');
 window.scrollTo(0,500);window.dispatchEvent(new Event('scroll'));
 var mid=parseInt(b.getAttribute('aria-valuenow'),10);
 t.ok('mid_value_between',mid>0&&mid<100,String(mid));
 window.scrollTo(0,100000);window.dispatchEvent(new Event('scroll'));
 t.ok('ends_at_100',b.getAttribute('aria-valuenow')==='100',b.getAttribute('aria-valuenow'));
 t.ok('bar_scale_follows',parseFloat(b.style.getPropertyValue('--sc-p'))===1);
 t.ok('fixed_to_top',b.getBoundingClientRect().top===0&&b.getBoundingClientRect().width>=innerWidth-1);
 window.scrollTo(0,0);window.dispatchEvent(new Event('scroll'));
 t.ok('returns_to_zero',b.getAttribute('aria-valuenow')==='0');
}};
