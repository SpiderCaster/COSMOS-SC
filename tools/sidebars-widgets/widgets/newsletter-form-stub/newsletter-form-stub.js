(function(){"use strict";
function init(f){
 var e=f.querySelector('input[type="email"]'),m=f.querySelector(".sc-nl-m");
 f.addEventListener("submit",function(ev){
  var hp=f.querySelector(".sc-hp input");
  if(hp&&hp.value){ev.preventDefault();return}
  var ok=e.value.trim()!==""&&e.checkValidity();
  e.setAttribute("aria-invalid",ok?"false":"true");
  m.className="sc-nl-m"+(ok?"":" sc-err");
  if(!ok){ev.preventDefault();m.textContent=f.getAttribute("data-error");e.focus();return}
  if(!f.getAttribute("action")){ev.preventDefault();m.textContent=f.getAttribute("data-stub")}
 })}
function run(){var n=document.querySelectorAll('[data-sc="news"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
