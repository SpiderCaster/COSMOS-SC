(function(){"use strict";
function init(b){
 var after=parseInt(b.getAttribute("data-after"),10)||400;
 function upd(){b.hidden=(window.pageYOffset||document.documentElement.scrollTop)<after}
 window.addEventListener("scroll",upd,{passive:true});
 b.addEventListener("click",function(){window.scrollTo(0,0);b.blur()});
 upd()}
function run(){var n=document.querySelectorAll('[data-sc="btt"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
