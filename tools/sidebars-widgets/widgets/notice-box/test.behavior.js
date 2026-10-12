window.scTest={behavior:function(t){
 var w=document.querySelector('.sc-note');
 t.ok('role_note',w.getAttribute('role')==='note');
 t.ok('heading_shown',!!w.querySelector('.sc-note-h'));
 var c=w.cloneNode(true);c.className='sc-w sc-note sc-note-warning';w.parentNode.appendChild(c);
 var bg=getComputedStyle(c).backgroundColor,fg=getComputedStyle(c).color;
 function lum(s){var n=s.match(/\d+/g).map(Number).map(function(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*n[0]+0.7152*n[1]+0.0722*n[2]}
 var a=lum(bg),b=lum(fg),r=(Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);
 t.ok('warning_contrast_4_5',r>=4.5,r.toFixed(2));
 c.parentNode.removeChild(c);
}};
