window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-contact');
 t.ok('address_element',!!w.querySelector('address'));
 t.ok('tel_link',w.querySelector('a[href="tel:+15550100"]'));
 t.ok('mailto_link',w.querySelector('a[href="mailto:fixture@example.com"]'));
 t.ok('two_lines',w.querySelectorAll('.sc-ct-line').length===2);
 t.ok('links_44',Array.prototype.every.call(w.querySelectorAll('a'),function(a){return a.getBoundingClientRect().height>=44}));
}};
