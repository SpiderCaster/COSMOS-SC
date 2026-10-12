(function(){"use strict";
function init(box){
 var b=box.querySelector(".sc-sh-copy"),m=box.querySelector(".sc-sh-m");
 b.addEventListener("click",function(){
  var u=box.getAttribute("data-url")||location.href;
  var ok=function(){m.textContent=box.getAttribute("data-ok")},bad=function(){m.textContent=box.getAttribute("data-fail")};
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(ok,bad)}else{bad()}
 })}
function run(){var n=document.querySelectorAll('[data-sc="share"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
