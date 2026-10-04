(function(){"use strict";
function init(box){
 var bar=box.querySelector(".sc-tp-bar"),tabs=bar.querySelectorAll('[role="tab"]'),panels=box.querySelectorAll('[role="tabpanel"]');
 function pick(i,focus){for(var k=0;k<tabs.length;k++){var on=k===i;tabs[k].setAttribute("aria-selected",on?"true":"false");tabs[k].tabIndex=on?0:-1;panels[k].hidden=!on}
  if(focus)tabs[i].focus()}
 for(var i=0;i<tabs.length;i++){(function(i){
  tabs[i].addEventListener("click",function(){pick(i,false)});
  tabs[i].addEventListener("keydown",function(e){var n=-1;
   if(e.key==="ArrowRight")n=(i+1)%tabs.length;else if(e.key==="ArrowLeft")n=(i+tabs.length-1)%tabs.length;
   else if(e.key==="Home")n=0;else if(e.key==="End")n=tabs.length-1;
   if(n>-1){e.preventDefault();pick(n,true)}})})(i)}
 bar.hidden=false;box.classList.add("sc-tp-on");pick(0,false)}
function run(){var n=document.querySelectorAll('[data-sc="tabs"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
