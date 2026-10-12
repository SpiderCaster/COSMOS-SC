(function(){"use strict";
function init(el){
 var src=document.querySelector(el.getAttribute("data-source")||"article");if(!src)return;
 var bar=el;
 function upd(){
  var r=src.getBoundingClientRect(),h=r.height-window.innerHeight,p=h<=0?1:Math.min(1,Math.max(0,-r.top/h));
  bar.style.setProperty("--sc-p",p.toFixed(3));bar.setAttribute("aria-valuenow",String(Math.round(p*100)))}
 window.addEventListener("scroll",upd,{passive:true});window.addEventListener("resize",upd);upd()}
function run(){var n=document.querySelectorAll('[data-sc="progress"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
