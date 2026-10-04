(function(){"use strict";
function init(box){
 var btn=box.querySelector(".sc-drw-open"),panel=box.querySelector(".sc-drw-panel"),close=box.querySelector(".sc-drw-close"),ov=box.querySelector(".sc-drw-ov"),mq=window.matchMedia("(min-width:900px)"),root=document.documentElement;
 function isOpen(){return panel.classList.contains("sc-open")}
 function open(){panel.classList.add("sc-open");ov.hidden=false;btn.setAttribute("aria-expanded","true");root.classList.add("sc-drw-lock");close.focus()}
 function shut(back){panel.classList.remove("sc-open");ov.hidden=true;btn.setAttribute("aria-expanded","false");root.classList.remove("sc-drw-lock");if(back)btn.focus()}
 btn.addEventListener("click",open);
 close.addEventListener("click",function(){shut(true)});
 ov.addEventListener("click",function(){shut(true)});
 box.addEventListener("keydown",function(e){
  if(!isOpen())return;
  if(e.key==="Escape"){shut(true);return}
  if(e.key!=="Tab")return;
  var f=panel.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]):not([type="hidden"]),select,textarea,summary'),a=f[0],z=f[f.length-1];
  if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}
  else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}
 });
 function chg(){if(mq.matches)shut(false)}
 if(mq.addEventListener)mq.addEventListener("change",chg);else mq.addListener(chg)}
function run(){var n=document.querySelectorAll('[data-sc="drawer"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
