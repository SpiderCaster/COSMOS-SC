(function(){"use strict";
function init(box){
 var d=box.querySelectorAll("details.sc-grp");
 if(!window.matchMedia||!window.matchMedia("(max-width:899px)").matches)return;
 for(var i=1;i<d.length;i++)d[i].open=false}
function run(){var n=document.querySelectorAll('[data-sc="groups"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
