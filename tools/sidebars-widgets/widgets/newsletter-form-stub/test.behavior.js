window.scTest={behavior:function(t){
 var f=document.querySelector('.sc-news');var e=f.querySelector('input[type=email]');var m=f.querySelector('.sc-nl-m');var c=f.querySelector('[type=checkbox]');
 var prevented=[];f.addEventListener('submit',function(ev){prevented.push(ev.defaultPrevented);ev.preventDefault()});
 t.ok('label_for',e.labels.length===1);
 e.value='not-an-email';f.requestSubmit();
 t.ok('invalid_blocked',prevented[0]===true);
 t.ok('invalid_marked',e.getAttribute('aria-invalid')==='true');
 t.ok('invalid_message',m.textContent==='Enter a valid email address.'&&m.classList.contains('sc-err'));
 e.value='name@example.com';c.checked=true;f.requestSubmit();
 t.ok('valid_stub_blocked',prevented[1]===true);
 t.ok('stub_message',m.textContent==='This form is not connected yet.',m.textContent);
 t.ok('valid_marked',e.getAttribute('aria-invalid')==='false');
 f.setAttribute('action','/fixture-form/');e.value='name@example.com';f.requestSubmit();
 t.ok('action_set_not_blocked_by_script',prevented[2]===false,String(prevented[2]));
 f.querySelector('.sc-hp input').value='x';f.requestSubmit();
 t.ok('honeypot_blocked',prevented[3]===true);
 f.setAttribute('action','');f.querySelector('.sc-hp input').value='';e.value='';
}, prepare:function(){document.querySelector('.sc-news .sc-nl-m').textContent='This form is not connected yet.'}};
