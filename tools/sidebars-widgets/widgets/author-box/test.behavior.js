window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-author');
 t.ok('no_photo_without_avatar',w.querySelectorAll('img').length===0);
 t.ok('name_shown',w.querySelector('.sc-au-n').textContent==='Fixture Author');
 t.ok('profile_link',w.querySelectorAll('a.sc-btn').length===1);
 t.ok('bio_18px',getComputedStyle(w.querySelector('.sc-body')).fontSize==='18px');
}};
