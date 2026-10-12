window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-share');var a=w.querySelectorAll('a');var b=w.querySelector('.sc-sh-copy');var m=w.querySelector('.sc-sh-m');
 t.ok('four_links_one_button',a.length===4&&!!b);
 t.ok('encoded_url_in_hrefs',Array.prototype.every.call(a,function(x){return x.href.indexOf('fixture-post-one')>0}));
 t.ok('no_raw_url_in_query',Array.prototype.every.call(a,function(x){return !/[?&](url|u)=https:\/\//.test(x.href)}));
 t.ok('external_rel',w.querySelectorAll('a[href^="https://"][rel*="noopener"]').length===3);
 var got=null;
 Object.defineProperty(navigator,'clipboard',{value:{writeText:function(s){got=s;return Promise.resolve()}},configurable:true});
 b.click();
 return t.sleep(30).then(function(){
  t.ok('copy_writes_url',got==='/fixture-post-one/',got);
  t.ok('copy_message',m.textContent==='Link copied.',m.textContent);
  Object.defineProperty(navigator,'clipboard',{value:{writeText:function(){return Promise.reject(new Error('no'))}},configurable:true});
  b.click();return t.sleep(30)}).then(function(){t.ok('copy_failure_message',/Copy failed/.test(m.textContent),m.textContent)});
}};
